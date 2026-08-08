from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from audio_chopper import (
    AudioChopperError,
    CHOPPER_PREVIEW_SECONDS,
    WaveformData,
    create_audio_clip,
    extract_waveform,
)
from ui import load_design, show_header, show_tool_header


@st.cache_data(show_spinner=False)
def analyze_uploaded_waveform(audio_data: bytes, suffix: str) -> WaveformData:
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        input_path.write_bytes(audio_data)
        return extract_waveform(input_path)


@st.cache_data(show_spinner=False)
def create_selected_player_audio(
    audio_data: bytes,
    suffix: str,
    start_seconds: float,
    end_seconds: float,
    source_duration_seconds: float,
) -> bytes:
    """Create the exact selected fragment for the always-visible player."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        output_path = Path(temp_directory) / "selected-fragment.mp3"
        input_path.write_bytes(audio_data)
        create_audio_clip(
            input_path,
            output_path,
            start_seconds,
            end_seconds,
            source_duration_seconds,
        )
        return output_path.read_bytes()


def format_time(seconds: float) -> str:
    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{remaining_seconds:04.1f}"


def update_waveform_view(action: str) -> None:
    """Zoom or pan the waveform without adding a second range slider."""
    waveform = st.session_state.get("chopper_waveform")
    if waveform is None:
        return
    duration = waveform.duration_seconds
    view_start, view_end = st.session_state.get(
        "chopper_view_window",
        (0.0, duration),
    )
    span = view_end - view_start
    selection = st.session_state.get("chopper_selection", (view_start, view_end))
    selection_start, selection_end = selection

    if action == "zoom_in":
        selection_span = selection_end - selection_start
        new_span = max(0.25, selection_span * 1.25, span / 2)
        center = (selection_start + selection_end) / 2
    elif action == "zoom_out":
        new_span = min(duration, span * 2)
        center = (selection_start + selection_end) / 2
    elif action == "pan_left":
        new_span = span
        center = (view_start + view_end) / 2 - span * 0.4
    elif action == "pan_right":
        new_span = span
        center = (view_start + view_end) / 2 + span * 0.4
    else:
        return

    new_span = min(duration, new_span)
    new_start = max(0.0, min(duration - new_span, center - new_span / 2))
    st.session_state["chopper_view_window"] = (
        float(new_start),
        float(new_start + new_span),
    )


def waveform_svg(
    waveform: WaveformData,
    start_seconds: float,
    end_seconds: float,
    view_start_seconds: float,
    view_end_seconds: float,
) -> str:
    total_points = len(waveform.peaks)
    first_point = max(
        0,
        int(total_points * view_start_seconds / waveform.duration_seconds),
    )
    last_point = min(
        total_points,
        max(
            first_point + 2,
            int(total_points * view_end_seconds / waveform.duration_seconds),
        ),
    )
    visible_peaks = waveform.peaks[first_point:last_point]
    width = len(visible_peaks)
    height = 120
    center = height / 2
    amplitude = height * 0.43
    upper = [
        f"{index:.1f},{center - peak * amplitude:.1f}"
        for index, peak in enumerate(visible_peaks)
    ]
    lower = [
        f"{index:.1f},{center + peak * amplitude:.1f}"
        for index, peak in reversed(tuple(enumerate(visible_peaks)))
    ]
    polygon = " ".join(upper + lower)
    view_duration = view_end_seconds - view_start_seconds
    selection_x = width * (start_seconds - view_start_seconds) / view_duration
    selection_width = width * (end_seconds - start_seconds) / view_duration
    return f"""
        <div class="chopper-waveform">
            <svg viewBox="0 0 {width} {height}" preserveAspectRatio="none"
                 role="img" aria-label="Audio waveform with selected sample highlighted">
                <defs>
                    <clipPath id="selected-sample">
                        <rect x="{selection_x:.2f}" y="0" width="{selection_width:.2f}" height="{height}" />
                    </clipPath>
                </defs>
                <line x1="0" y1="{center}" x2="{width}" y2="{center}" class="wave-center" />
                <polygon points="{polygon}" class="wave-base" />
                <polygon points="{polygon}" class="wave-selected" clip-path="url(#selected-sample)" />
                <line x1="{selection_x:.2f}" y1="0" x2="{selection_x:.2f}" y2="{height}" class="cut-marker" />
                <line x1="{selection_x + selection_width:.2f}" y1="0" x2="{selection_x + selection_width:.2f}" y2="{height}" class="cut-marker" />
            </svg>
            <div class="wave-times"><span>{format_time(view_start_seconds)}</span><span>{format_time(view_end_seconds)}</span></div>
        </div>
    """


load_design()
track_page_view("audio_chopper")
show_header()
show_tool_header(
    "Transform / 05",
    "Audio Chopper",
    "Find the moment, cut the sample and take it into your next production.",
)

st.markdown(
    """
    <style>
    .chopper-waveform { padding:1rem 1rem .55rem; border:1px solid var(--line); border-radius:15px 6px 15px 6px; background:rgba(8,17,13,.78); overflow:hidden; }
    .chopper-waveform svg { display:block; width:100%; height:190px; }
    .wave-center { stroke:rgba(216,195,154,.13); stroke-width:1; }
    .wave-base { fill:rgba(216,195,154,.34); }
    .wave-selected { fill:var(--lime); filter:drop-shadow(0 0 4px rgba(184,255,61,.28)); }
    .cut-marker { stroke:var(--bone); stroke-width:1.5; }
    .wave-times { display:flex; justify-content:space-between; color:var(--muted); font-family:var(--font-technical); font-size:.68rem; }
    .sample-readout { display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin:.4rem 0 1rem; }
    .sample-readout div { padding:.75rem; border:1px solid var(--line); background:rgba(16,39,27,.72); color:var(--sand); font-size:.68rem; letter-spacing:.08em; }
    .sample-readout b { display:block; margin-top:.3rem; color:var(--lime); font-family:var(--font-technical); font-size:.95rem; letter-spacing:0; }
    .st-key-chopper_pan_left button, .st-key-chopper_zoom_out button,
    .st-key-chopper_zoom_in button, .st-key-chopper_pan_right button {
        min-height:2.25rem; width:100%; padding:0; border-radius:6px 3px 6px 3px;
        font-family:var(--font-technical); font-size:1rem; letter-spacing:0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

audio_file = st.file_uploader(
    "Upload audio to sample",
    type=["wav", "mp3", "m4a", "flac"],
    key="audio_chopper_upload",
)

if audio_file is not None:
    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = ("waveform-v2", audio_file.name, audio_file.size)

    if st.session_state.get("chopper_upload_signature") != upload_signature:
        with st.spinner("Drawing the waveform..."):
            try:
                waveform = analyze_uploaded_waveform(audio_data, suffix)
            except (AudioChopperError, OSError) as error:
                st.error("The waveform could not be created.")
                st.code(str(error))
                st.stop()
        st.session_state["chopper_waveform"] = waveform
        st.session_state.pop("chopper_preview", None)
        st.session_state.pop("chopper_export", None)
        st.session_state["chopper_view_window"] = (
            0.0,
            float(waveform.duration_seconds),
        )
        st.session_state.pop("chopper_selection", None)
        st.session_state.pop("chopper_selection_signature", None)
        st.session_state["chopper_upload_signature"] = upload_signature

    waveform = st.session_state["chopper_waveform"]
    default_end = min(30.0, waveform.duration_seconds)
    view_start_seconds, view_end_seconds = st.session_state.get(
        "chopper_view_window",
        (0.0, float(waveform.duration_seconds)),
    )

    current_selection = st.session_state.get("chopper_selection")
    if (
        current_selection is None
        or current_selection[0] < view_start_seconds
        or current_selection[1] > view_end_seconds
        or current_selection[1] <= current_selection[0]
    ):
        st.session_state["chopper_selection"] = (
            float(view_start_seconds),
            float(min(view_end_seconds, view_start_seconds + default_end)),
        )
    selection = st.slider(
        "Select sample range",
        min_value=float(view_start_seconds),
        max_value=float(view_end_seconds),
        step=0.01,
        format="%.2f s",
        key="chopper_selection",
    )
    start_seconds, end_seconds = selection

    view_label, pan_left, zoom_out, zoom_in, pan_right = st.columns(
        [6, 1, 1, 1, 1],
        vertical_alignment="center",
    )
    with view_label:
        st.caption(
            f"VIEW · {format_time(view_start_seconds)} — "
            f"{format_time(view_end_seconds)}"
        )
    with pan_left:
        st.button(
            "←",
            key="chopper_pan_left",
            help="Move the waveform view left",
            on_click=update_waveform_view,
            args=("pan_left",),
        )
    with zoom_out:
        st.button(
            "−",
            key="chopper_zoom_out",
            help="Zoom out",
            on_click=update_waveform_view,
            args=("zoom_out",),
        )
    with zoom_in:
        st.button(
            "+",
            key="chopper_zoom_in",
            help="Zoom into the selected fragment",
            on_click=update_waveform_view,
            args=("zoom_in",),
        )
    with pan_right:
        st.button(
            "→",
            key="chopper_pan_right",
            help="Move the waveform view right",
            on_click=update_waveform_view,
            args=("pan_right",),
        )
    selection_signature = (*upload_signature, start_seconds, end_seconds)
    if st.session_state.get("chopper_selection_signature") != selection_signature:
        st.session_state.pop("chopper_preview", None)
        st.session_state.pop("chopper_export", None)
        st.session_state["chopper_selection_signature"] = selection_signature

    st.markdown(
        waveform_svg(
            waveform,
            start_seconds,
            end_seconds,
            view_start_seconds,
            view_end_seconds,
        ),
        unsafe_allow_html=True,
    )

    st.write("**Selected fragment — press Play to audition the current range**")
    with st.spinner("Updating the selected fragment..."):
        try:
            selected_player = create_selected_player_audio(
                audio_data,
                suffix,
                start_seconds,
                end_seconds,
                waveform.duration_seconds,
            )
        except (AudioChopperError, OSError) as error:
            st.error("The selected fragment player could not be prepared.")
            st.code(str(error))
            selected_player = None
    if selected_player is not None:
        st.audio(selected_player, format="audio/mpeg")
    st.markdown(
        f"""
        <div class="sample-readout">
            <div>START<b>{format_time(start_seconds)}</b></div>
            <div>END<b>{format_time(end_seconds)}</b></div>
            <div>LENGTH<b>{end_seconds - start_seconds:.1f} s</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preview_column, export_column = st.columns(2)
    with preview_column:
        create_preview = st.button("PREVIEW SELECTION", type="secondary")
    with export_column:
        export_sample = st.button("CUT SAMPLE", type="primary")

    if create_preview:
        with st.spinner("Preparing the selected preview..."):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    input_path = Path(temp_directory) / f"source{suffix}"
                    output_path = Path(temp_directory) / "sample-preview.mp3"
                    input_path.write_bytes(audio_data)
                    create_audio_clip(
                        input_path,
                        output_path,
                        start_seconds,
                        end_seconds,
                        waveform.duration_seconds,
                        maximum_duration_seconds=CHOPPER_PREVIEW_SECONDS,
                    )
                    st.session_state["chopper_preview"] = output_path.read_bytes()
                    track_event("audio_preview_created", {"tool": "audio_chopper"})
            except (AudioChopperError, OSError) as error:
                st.error("The selected preview could not be created.")
                st.code(str(error))

    if export_sample:
        with st.spinner("Cutting your sample..."):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    input_path = Path(temp_directory) / f"source{suffix}"
                    output_path = Path(temp_directory) / "sample.mp3"
                    input_path.write_bytes(audio_data)
                    create_audio_clip(
                        input_path,
                        output_path,
                        start_seconds,
                        end_seconds,
                        waveform.duration_seconds,
                    )
                    st.session_state["chopper_export"] = output_path.read_bytes()
                    track_event("audio_processing_completed", {"tool": "audio_chopper"})
            except (AudioChopperError, OSError) as error:
                st.error("The sample could not be cut.")
                st.code(str(error))

    preview = st.session_state.get("chopper_preview")
    if preview is not None:
        st.write("**Selected preview (up to 30 seconds)**")
        st.audio(preview, format="audio/mpeg")

    sample = st.session_state.get("chopper_export")
    if sample is not None:
        st.success("Your sample is ready.")
        st.audio(sample, format="audio/mpeg")
        st.download_button(
            "DOWNLOAD SAMPLE MP3",
            data=sample,
            file_name=f"{Path(audio_file.name).stem}_sample.mp3",
            mime="audio/mpeg",
            on_click=track_event,
            args=("audio_downloaded", {"tool": "audio_chopper", "format": "mp3"}),
        )

    st.caption(
        "The highlighted waveform is the selected range. Preview is limited "
        "to 30 seconds; Cut Sample exports the complete selection."
    )
