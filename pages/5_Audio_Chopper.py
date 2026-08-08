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
from waveform_component import interactive_waveform


@st.cache_data(show_spinner=False)
def analyze_uploaded_waveform(audio_data: bytes, suffix: str) -> WaveformData:
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        input_path.write_bytes(audio_data)
        return extract_waveform(input_path)


@st.cache_data(show_spinner=False)
def create_browser_audio(
    audio_data: bytes,
    suffix: str,
    source_duration_seconds: float,
) -> bytes:
    """Create one browser-friendly copy for fluid JavaScript playback."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        output_path = Path(temp_directory) / "browser-player.mp3"
        input_path.write_bytes(audio_data)
        create_audio_clip(
            input_path,
            output_path,
            0.0,
            source_duration_seconds,
            source_duration_seconds,
        )
        return output_path.read_bytes()


def format_time(seconds: float) -> str:
    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{remaining_seconds:04.1f}"


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
    .sample-readout { display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin:.4rem 0 1rem; }
    .sample-readout div { padding:.75rem; border:1px solid var(--line); background:rgba(16,39,27,.72); color:var(--sand); font-size:.68rem; letter-spacing:.08em; }
    .sample-readout b { display:block; margin-top:.3rem; color:var(--lime); font-family:var(--font-technical); font-size:.95rem; letter-spacing:0; }
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
    upload_signature = ("waveform-v3", audio_file.name, audio_file.size)

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

    current_selection = st.session_state.get(
        "chopper_selection",
        (0.0, float(default_end)),
    )
    with st.spinner("Preparing the interactive player..."):
        try:
            browser_audio = create_browser_audio(
                audio_data,
                suffix,
                waveform.duration_seconds,
            )
        except (AudioChopperError, OSError) as error:
            st.error("The interactive player could not be prepared.")
            st.code(str(error))
            st.stop()
    component_selection = interactive_waveform(
        waveform,
        current_selection,
        (view_start_seconds, view_end_seconds),
        browser_audio,
    )
    start_seconds = float(component_selection["start"])
    end_seconds = float(component_selection["end"])
    view_start_seconds = float(component_selection["view_start"])
    view_end_seconds = float(component_selection["view_end"])
    st.session_state["chopper_selection"] = (start_seconds, end_seconds)
    st.session_state["chopper_view_window"] = (
        view_start_seconds,
        view_end_seconds,
    )
    selection_signature = (*upload_signature, start_seconds, end_seconds)
    if st.session_state.get("chopper_selection_signature") != selection_signature:
        st.session_state.pop("chopper_preview", None)
        st.session_state.pop("chopper_export", None)
        st.session_state["chopper_selection_signature"] = selection_signature

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
    st.caption(
        "Play, selection and zoom stay in the browser. Press Use Selection "
        "only when the range is ready for preview or export."
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
