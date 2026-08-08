from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from mastering_analysis import (
    MasteringAnalysisError,
    MasteringMetrics,
    StereoMetrics,
    analyze_mastering,
    analyze_stereo,
    calculate_volume_match_gains,
    create_volume_matched_audio,
)
from ui import load_design, show_header, show_tool_header


@st.cache_data(show_spinner=False)
def analyze_uploaded_master(
    audio_data: bytes,
    suffix: str,
) -> tuple[MasteringMetrics, StereoMetrics]:
    """Cache analysis so Streamlit reruns do not process the same file again."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"master{suffix}"
        input_path.write_bytes(audio_data)
        return analyze_mastering(input_path), analyze_stereo(input_path)


@st.cache_data(show_spinner=False)
def create_matched_player_audio(
    audio_data: bytes,
    suffix: str,
    gain_db: float,
) -> bytes:
    """Create a cached MP3 listening copy at the requested matched level."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        output_path = Path(temp_directory) / "volume-matched.mp3"
        input_path.write_bytes(audio_data)
        create_volume_matched_audio(input_path, output_path, gain_db)
        return output_path.read_bytes()


def format_duration(seconds: float) -> str:
    total_seconds = round(seconds)
    minutes, remaining_seconds = divmod(total_seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"


def true_peak_context(true_peak_dbfs: float) -> str:
    if true_peak_dbfs > 0:
        return (
            "The measured true peak exceeds 0 dBTP. This can indicate "
            "inter-sample clipping risk in playback or encoding."
        )
    if true_peak_dbfs > -1.0:
        return (
            "The track has less than 1 dB of true-peak headroom. That may be "
            "intentional, but lossy encoding can create additional peaks."
        )
    return (
        "The track has at least 1 dB of measured true-peak headroom. Loudness "
        "and headroom still need to be judged in context."
    )


def format_balance(balance_db: float) -> str:
    if abs(balance_db) < 0.1:
        return "Centered"
    louder_side = "R" if balance_db > 0 else "L"
    return f"{louder_side} +{abs(balance_db):.1f} dB"


def stereo_context(stereo: StereoMetrics) -> str:
    if stereo.channels == 1:
        return "This is a mono source, so stereo width and phase are not present."
    if stereo.correlation < 0:
        return (
            "Negative phase correlation was measured. Some elements may lose "
            "level or cancel when the track is played in mono."
        )
    if stereo.correlation < 0.2:
        return (
            "Phase correlation is low. The master is very wide and should be "
            "checked carefully in mono."
        )
    return (
        "Phase correlation is positive overall. This reduces broad mono "
        "cancellation risk, but short problem sections may still exist."
    )


def render_file_caption(audio_file) -> None:
    suffix = Path(audio_file.name).suffix.lower()
    size_megabytes = audio_file.size / (1024 * 1024)
    st.caption(
        f"{audio_file.name} · {suffix.removeprefix('.').upper()} · "
        f"{size_megabytes:.1f} MB"
    )


def audio_mime_type(filename: str) -> str:
    """Return the browser media type for a supported uploaded audio file."""
    return {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".m4a": "audio/mp4",
    }.get(Path(filename).suffix.lower(), "audio/mpeg")


def render_report(metrics: MasteringMetrics, stereo: StereoMetrics) -> None:
    st.subheader("Loudness & dynamics")
    loudness_column, range_column, rms_column = st.columns(3)
    loudness_column.metric("INTEGRATED LOUDNESS", f"{metrics.integrated_lufs:.1f} LUFS")
    range_column.metric("LOUDNESS RANGE", f"{metrics.loudness_range_lu:.1f} LU")
    rms_column.metric("RMS LEVEL", f"{metrics.rms_level_dbfs:.1f} dBFS")

    st.subheader("Peak levels")
    true_peak_column, sample_peak_column, duration_column = st.columns(3)
    true_peak_column.metric("TRUE PEAK", f"{metrics.true_peak_dbfs:.1f} dBTP")
    sample_peak_column.metric("SAMPLE PEAK", f"{metrics.sample_peak_dbfs:.1f} dBFS")
    duration_column.metric("DURATION", format_duration(metrics.duration_seconds))
    st.info(true_peak_context(metrics.true_peak_dbfs))

    st.subheader("Stereo field")
    balance_column, width_column, phase_column = st.columns(3)
    balance_column.metric("L / R BALANCE", format_balance(stereo.balance_db))
    width_column.metric(
        "STEREO WIDTH",
        "Mono" if stereo.channels == 1 else f"{stereo.width_percent:.0f}% side",
    )
    phase_column.metric(
        "PHASE CORRELATION",
        "Mono" if stereo.channels == 1 else f"{stereo.correlation:+.2f}",
    )
    st.info(stereo_context(stereo))


def render_comparison(
    reference_report: tuple[MasteringMetrics, StereoMetrics],
    track_report: tuple[MasteringMetrics, StereoMetrics],
) -> None:
    reference, reference_stereo = reference_report
    track, track_stereo = track_report

    st.subheader("Original measurements")
    st.caption(
        "These values always come from the original files. Volume Match only "
        "changes the listening copies below."
    )
    rows = [
        ("Integrated loudness", reference.integrated_lufs, track.integrated_lufs, "LUFS"),
        ("RMS level", reference.rms_level_dbfs, track.rms_level_dbfs, "dBFS"),
        ("True peak", reference.true_peak_dbfs, track.true_peak_dbfs, "dBTP"),
        ("Sample peak", reference.sample_peak_dbfs, track.sample_peak_dbfs, "dBFS"),
        ("Loudness range", reference.loudness_range_lu, track.loudness_range_lu, "LU"),
        ("Stereo width", reference_stereo.width_percent, track_stereo.width_percent, "% side"),
        ("Phase correlation", reference_stereo.correlation, track_stereo.correlation, ""),
    ]
    table_rows = []
    for label, reference_value, track_value, unit in rows:
        difference = track_value - reference_value
        table_rows.append(
            "<tr>"
            f"<th scope='row'>{label}</th>"
            f"<td>{f'{reference_value:.1f} {unit}'.strip()}</td>"
            f"<td>{f'{track_value:.1f} {unit}'.strip()}</td>"
            f"<td class='difference'>{f'{difference:+.1f} {unit}'.strip()}</td>"
            "</tr>"
        )
    st.markdown(
        """
        <style>
        .ab-comparison-grid {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            border: 1px solid rgba(216, 195, 154, 0.32);
            border-radius: 12px;
            background: rgba(8, 17, 13, 0.72);
        }
        .ab-comparison-grid th,
        .ab-comparison-grid td {
            padding: 0.8rem 0.9rem;
            border-right: 1px solid rgba(216, 195, 154, 0.20);
            border-bottom: 1px solid rgba(216, 195, 154, 0.20);
            text-align: left;
        }
        .ab-comparison-grid thead th {
            background: rgba(31, 107, 69, 0.35);
            color: #f1e9d5;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
        }
        .ab-comparison-grid tbody th {
            color: #d8c39a;
            font-weight: 600;
        }
        .ab-comparison-grid td {
            color: #f1e9d5;
            font-family: var(--font-technical);
            font-variant-numeric: tabular-nums;
        }
        .ab-comparison-grid td.difference {
            color: #b8ff3d;
            font-weight: 700;
        }
        .ab-comparison-grid th:last-child,
        .ab-comparison-grid td:last-child { border-right: 0; }
        .ab-comparison-grid tbody tr:last-child th,
        .ab-comparison-grid tbody tr:last-child td { border-bottom: 0; }
        @media (max-width: 640px) {
            .ab-comparison-grid th,
            .ab-comparison-grid td { padding: 0.65rem 0.45rem; font-size: 0.76rem; }
        }
        </style>
        <table class="ab-comparison-grid">
            <thead>
                <tr>
                    <th>MEASUREMENT</th>
                    <th>REFERENCE</th>
                    <th>YOUR MASTER</th>
                    <th>DIFFERENCE</th>
                </tr>
            </thead>
            <tbody>
        """
        + "".join(table_rows)
        + """
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def analysis_help() -> None:
    with st.expander("HOW TO READ THESE RESULTS"):
        st.markdown(
            """
            - **LUFS is not a quality score.** A louder master is not automatically better.
            - **RMS shows average signal energy.** Keep Volume Match off when judging raw level.
            - **True peak and sample peak are different.** True peak estimates inter-sample behavior.
            - **Stereo width needs a mono check.** Negative correlation can cause cancellation.
            - Use a reference from a similar genre and arrangement, then make the final decision by ear.
            """
        )


load_design()
track_page_view("mastering_analyzer")
show_header()
show_tool_header(
    "Analyze / 04",
    "Mastering Analyzer",
    "Measure loudness, peak levels and dynamics without changing your audio.",
)

analysis_mode = st.radio(
    "Analysis mode",
    ["Single master", "Compare with reference"],
    horizontal=True,
    help=(
        "Use Compare with reference to measure your master beside a released "
        "track and audition both with or without loudness matching."
    ),
)

if analysis_mode == "Compare with reference":
    st.subheader("A / B reference comparison")
    st.caption(
        "Upload a suitable commercial reference and your own master. The "
        "analysis never modifies either file."
    )
    reference_column, track_column = st.columns(2)
    with reference_column:
        st.markdown("#### Reference track")
        reference_file = st.file_uploader(
            "Upload the sound you are aiming for",
            type=["wav", "mp3", "m4a", "flac"],
            key="mastering_reference_upload",
        )
        if reference_file is not None:
            render_file_caption(reference_file)
    with track_column:
        st.markdown("#### Your master")
        track_file = st.file_uploader(
            "Upload the master you want to check",
            type=["wav", "mp3", "m4a", "flac"],
            key="mastering_comparison_upload",
        )
        if track_file is not None:
            render_file_caption(track_file)

    if reference_file is not None and track_file is not None:
        comparison_signature = (
            reference_file.name,
            reference_file.size,
            track_file.name,
            track_file.size,
        )
        if st.session_state.get("comparison_signature") != comparison_signature:
            st.session_state.pop("comparison_reports", None)
            st.session_state["comparison_signature"] = comparison_signature

        if st.button("ANALYZE BOTH MASTERS", type="primary"):
            with st.spinner("Measuring both masters..."):
                try:
                    reference_data = reference_file.getvalue()
                    track_data = track_file.getvalue()
                    reference_suffix = Path(reference_file.name).suffix.lower()
                    track_suffix = Path(track_file.name).suffix.lower()
                    st.session_state["comparison_reports"] = (
                        analyze_uploaded_master(reference_data, reference_suffix),
                        analyze_uploaded_master(track_data, track_suffix),
                    )
                except (MasteringAnalysisError, OSError) as error:
                    st.error("The masters could not be compared.")
                    st.code(str(error))

        comparison_reports = st.session_state.get("comparison_reports")
        if comparison_reports is not None:
            reference_report, track_report = comparison_reports
            reference_metrics, _ = reference_report
            track_metrics, _ = track_report
            st.success("A / B analysis complete.")
            track_event(
                "audio_comparison_completed",
                {"tool": "mastering_analyzer"},
                once_key=f"comparison_{comparison_signature}",
            )
            render_comparison(reference_report, track_report)

            st.subheader("A / B listening")
            volume_match = st.toggle(
                "VOLUME MATCH",
                value=True,
                help=(
                    "Matches both players to the quieter integrated LUFS level. "
                    "Turn it off to hear their real loudness difference."
                ),
            )
            track_event(
                "volume_match_selected",
                {"tool": "mastering_analyzer", "enabled": volume_match},
                once_key=f"volume_match_{volume_match}",
            )
            player_reference = reference_file.getvalue()
            player_track = track_file.getvalue()
            if volume_match:
                reference_gain, track_gain = calculate_volume_match_gains(
                    reference_metrics.integrated_lufs,
                    track_metrics.integrated_lufs,
                )
                with st.spinner("Preparing level-matched listening copies..."):
                    try:
                        player_reference = create_matched_player_audio(
                            player_reference,
                            Path(reference_file.name).suffix.lower(),
                            reference_gain,
                        )
                        player_track = create_matched_player_audio(
                            player_track,
                            Path(track_file.name).suffix.lower(),
                            track_gain,
                        )
                    except (MasteringAnalysisError, OSError) as error:
                        st.error("Volume-matched players could not be prepared.")
                        st.code(str(error))
                st.caption(
                    f"Matched to {min(reference_metrics.integrated_lufs, track_metrics.integrated_lufs):.1f} "
                    "LUFS for listening only. The measurements above remain original."
                )
            else:
                st.caption("Original playback levels — useful for judging the real LUFS/RMS difference.")

            player_reference_column, player_track_column = st.columns(2)
            with player_reference_column:
                st.markdown("**REFERENCE**")
                st.audio(
                    player_reference,
                    format=(
                        "audio/mpeg"
                        if volume_match
                        else audio_mime_type(reference_file.name)
                    ),
                )
            with player_track_column:
                st.markdown("**YOUR MASTER**")
                st.audio(
                    player_track,
                    format=(
                        "audio/mpeg"
                        if volume_match
                        else audio_mime_type(track_file.name)
                    ),
                )

            analysis_help()
            st.caption(
                "Volume Match creates temporary listening copies and does not "
                "alter or retain the uploaded masters."
            )
    else:
        st.info("Upload both files to begin the A / B comparison.")

    st.stop()

audio_file = st.file_uploader(
    "Upload your master",
    type=["wav", "mp3", "m4a", "flac"],
    key="mastering_analyzer_upload",
    help=(
        "Analyze the final exported master when possible. WAV or FLAC avoids "
        "measurements being affected by lossy encoding."
    ),
)

if audio_file is not None:
    st.audio(audio_file)

    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = (audio_file.name, audio_file.size)

    if st.session_state.get("mastering_signature") != upload_signature:
        st.session_state.pop("mastering_report", None)
        st.session_state["mastering_signature"] = upload_signature

    size_megabytes = audio_file.size / (1024 * 1024)
    st.caption(
        f"{audio_file.name} · {suffix.removeprefix('.').upper()} · "
        f"{size_megabytes:.1f} MB"
    )

    if st.button("ANALYZE MASTER", type="primary"):
        with st.spinner("Measuring loudness and peak levels..."):
            try:
                st.session_state["mastering_report"] = analyze_uploaded_master(
                    audio_data,
                    suffix,
                )
            except (MasteringAnalysisError, OSError) as error:
                st.error("The master could not be analyzed.")
                st.code(str(error))

    report = st.session_state.get("mastering_report")
    if report is not None:
        metrics, stereo = report
        st.success("Mastering analysis complete.")
        track_event(
            "audio_analysis_completed",
            {"tool": "mastering_analyzer"},
            once_key=f"mastering_{upload_signature}",
        )

        st.subheader("Loudness & dynamics")
        loudness_column, range_column, rms_column = st.columns(3)
        with loudness_column:
            st.metric(
                "INTEGRATED LOUDNESS",
                f"{metrics.integrated_lufs:.1f} LUFS",
                help=(
                    "Average perceived loudness across the complete track, "
                    "measured using EBU R128 gating."
                ),
            )
        with range_column:
            st.metric(
                "LOUDNESS RANGE",
                f"{metrics.loudness_range_lu:.1f} LU",
                help=(
                    "The variation between quieter and louder sections after "
                    "gating. Genre and arrangement strongly affect this value."
                ),
            )
        with rms_column:
            st.metric(
                "RMS LEVEL",
                f"{metrics.rms_level_dbfs:.1f} dBFS",
                help=(
                    "Average signal energy. RMS is useful context but does not "
                    "model perceived loudness as accurately as LUFS."
                ),
            )

        st.subheader("Peak levels")
        true_peak_column, sample_peak_column, duration_column = st.columns(3)
        with true_peak_column:
            st.metric(
                "TRUE PEAK",
                f"{metrics.true_peak_dbfs:.1f} dBTP",
                help=(
                    "An oversampled estimate of peaks that may occur between "
                    "digital samples during conversion or playback."
                ),
            )
        with sample_peak_column:
            st.metric(
                "SAMPLE PEAK",
                f"{metrics.sample_peak_dbfs:.1f} dBFS",
                help="The highest individual digital sample in the file.",
            )
        with duration_column:
            st.metric(
                "DURATION",
                format_duration(metrics.duration_seconds),
                help="Duration reported by the uploaded audio container.",
            )

        st.info(true_peak_context(metrics.true_peak_dbfs))

        st.subheader("Stereo field")
        balance_column, width_column, phase_column = st.columns(3)
        with balance_column:
            st.metric(
                "L / R BALANCE",
                format_balance(stereo.balance_db),
                help=(
                    "The RMS level difference between the right and left "
                    "channels. A small offset can be musically intentional."
                ),
            )
        with width_column:
            st.metric(
                "STEREO WIDTH",
                (
                    "Mono"
                    if stereo.channels == 1
                    else f"{stereo.width_percent:.0f}% side"
                ),
                help=(
                    "The side signal as a percentage of combined mid and side "
                    "RMS energy. 0% is fully centered; higher values indicate "
                    "more side information."
                ),
            )
        with phase_column:
            st.metric(
                "PHASE CORRELATION",
                (
                    "Mono"
                    if stereo.channels == 1
                    else f"{stereo.correlation:+.2f}"
                ),
                help=(
                    "+1 means the channels move together, 0 means they are "
                    "largely unrelated, and negative values indicate possible "
                    "mono cancellation."
                ),
            )

        st.info(stereo_context(stereo))

        with st.expander("HOW TO READ THESE RESULTS"):
            st.markdown(
                """
                - **LUFS is not a quality score.** A louder master is not
                  automatically better, and playback platforms may normalize it.
                - **True peak and sample peak are different.** True peak estimates
                  inter-sample behavior that a sample meter can miss.
                - **LRA depends on the music.** Dense club music and an acoustic
                  arrangement naturally produce very different ranges.
                - **Stereo width needs a mono check.** A wide master can sound
                  excellent, but negative phase correlation can cause cancellation.
                - Compare measurements with suitable references, then make the
                  final decision with your ears in a calibrated listening setup.
                """
            )

        st.caption(
            "Measurements use FFmpeg's EBU R128 and signal-statistics filters. "
            "They are technical estimates, not a mastering verdict."
        )
