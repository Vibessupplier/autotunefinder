from pathlib import Path
import tempfile

import streamlit as st

from mastering_analysis import (
    MasteringAnalysisError,
    MasteringMetrics,
    analyze_mastering,
)
from ui import load_design, show_header, show_tool_header


@st.cache_data(show_spinner=False)
def analyze_uploaded_master(
    audio_data: bytes,
    suffix: str,
) -> MasteringMetrics:
    """Cache analysis so Streamlit reruns do not process the same file again."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"master{suffix}"
        input_path.write_bytes(audio_data)
        return analyze_mastering(input_path)


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


load_design()
show_header()
show_tool_header(
    "Analyze / 04",
    "Mastering Analyzer",
    "Measure loudness, peak levels and dynamics without changing your audio.",
)

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
        st.session_state.pop("mastering_metrics", None)
        st.session_state["mastering_signature"] = upload_signature

    size_megabytes = audio_file.size / (1024 * 1024)
    st.caption(
        f"{audio_file.name} · {suffix.removeprefix('.').upper()} · "
        f"{size_megabytes:.1f} MB"
    )

    if st.button("ANALYZE MASTER", type="primary"):
        with st.spinner("Measuring loudness and peak levels..."):
            try:
                st.session_state["mastering_metrics"] = analyze_uploaded_master(
                    audio_data,
                    suffix,
                )
            except (MasteringAnalysisError, OSError) as error:
                st.error("The master could not be analyzed.")
                st.code(str(error))

    metrics = st.session_state.get("mastering_metrics")
    if metrics is not None:
        st.success("Mastering analysis complete.")

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

        with st.expander("HOW TO READ THESE RESULTS"):
            st.markdown(
                """
                - **LUFS is not a quality score.** A louder master is not
                  automatically better, and playback platforms may normalize it.
                - **True peak and sample peak are different.** True peak estimates
                  inter-sample behavior that a sample meter can miss.
                - **LRA depends on the music.** Dense club music and an acoustic
                  arrangement naturally produce very different ranges.
                - Compare measurements with suitable references, then make the
                  final decision with your ears in a calibrated listening setup.
                """
            )

        st.caption(
            "Measurements use FFmpeg's EBU R128 and signal-statistics filters. "
            "They are technical estimates, not a mastering verdict."
        )
