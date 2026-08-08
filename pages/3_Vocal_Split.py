from pathlib import Path
import tempfile

import streamlit as st

from audio_engine import probe_audio_duration
from stem_separation import (
    VOCAL_PREVIEW_SECONDS,
    StemSeparationError,
    create_vocal_split_preview,
    separate_vocals,
)
from ui import load_design, show_header


@st.cache_data(show_spinner=False)
def get_uploaded_duration(audio_data: bytes, suffix: str) -> float:
    """Cache duration detection so UI reruns do not reopen the same audio."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"input{suffix}"
        input_path.write_bytes(audio_data)
        return probe_audio_duration(input_path)


def format_time(seconds: float) -> str:
    minutes, remaining_seconds = divmod(int(seconds), 60)
    return f"{minutes}:{remaining_seconds:02d}"


load_design()
show_header()

st.title("Vocal Remover & Acapella Extractor")
st.write("Separate a track into an acapella and an instrumental.")
st.info(
    "Local prototype: processing runs on this Mac and can take several minutes."
)

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"],
    key="vocal_split_upload",
)

if audio_file is not None:
    st.audio(audio_file)

    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = (audio_file.name, audio_file.size)

    if st.session_state.get("vocal_split_signature") != upload_signature:
        st.session_state.pop("vocal_preview_start", None)
        st.session_state.pop("vocal_preview_settings", None)
        st.session_state.pop("vocal_split_preview", None)
        st.session_state.pop("vocal_split_result", None)
        st.session_state["vocal_split_signature"] = upload_signature

    try:
        duration = get_uploaded_duration(audio_data, suffix)
    except Exception as error:
        st.error("The audio duration could not be detected.")
        st.code(str(error))
        st.stop()

    maximum_start = max(duration - VOCAL_PREVIEW_SECONDS, 0.0)
    if maximum_start > 0:
        preview_start = st.slider(
            "Preview start",
            min_value=0.0,
            max_value=maximum_start,
            value=min(30.0, maximum_start),
            step=1.0,
            format="%.0f seconds",
            key="vocal_preview_start",
            help="Choose a section where the vocals are clearly audible.",
        )
    else:
        preview_start = 0.0
        st.caption("This track is shorter than 20 seconds, so all of it is used.")

    preview_end = min(preview_start + VOCAL_PREVIEW_SECONDS, duration)
    st.caption(
        f"Free preview section: {format_time(preview_start)}–"
        f"{format_time(preview_end)}"
    )

    preview_signature = upload_signature + (preview_start,)
    if st.session_state.get("vocal_preview_settings") != preview_signature:
        st.session_state.pop("vocal_split_preview", None)
        st.session_state["vocal_preview_settings"] = preview_signature

    if st.button("CREATE 20-SECOND VOCAL PREVIEW"):
        with st.spinner("Separating this 20-second preview..."):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    temporary_path = Path(temp_directory)
                    input_path = temporary_path / f"input{suffix}"
                    preview_path = temporary_path / "preview.wav"
                    output_directory = temporary_path / "preview-stems"
                    input_path.write_bytes(audio_data)

                    split = create_vocal_split_preview(
                        input_path,
                        preview_path,
                        output_directory,
                        start_seconds=preview_start,
                    )
                    st.session_state["vocal_split_preview"] = {
                        "vocals": split.vocals_path.read_bytes(),
                        "instrumental": split.instrumental_path.read_bytes(),
                        "start": preview_start,
                        "end": preview_end,
                    }
            except (StemSeparationError, OSError) as error:
                st.error("The vocal preview could not be created.")
                st.code(str(error))

    preview = st.session_state.get("vocal_split_preview")
    if preview is not None:
        st.success(
            f"Preview ready: {format_time(preview['start'])}–"
            f"{format_time(preview['end'])}"
        )
        st.subheader("Acapella preview")
        st.audio(preview["vocals"], format="audio/mpeg")
        st.subheader("Instrumental preview")
        st.audio(preview["instrumental"], format="audio/mpeg")

    st.divider()
    st.subheader("Full track — local test")
    st.caption(
        "Full-track processing currently runs only on this Mac and may take "
        "10–20 minutes."
    )

    if st.button("SEPARATE FULL TRACK"):
        with st.spinner(
            "Separating vocals... Keep this page open. This may take several minutes."
        ):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    temporary_path = Path(temp_directory)
                    input_path = temporary_path / f"input{suffix}"
                    output_directory = temporary_path / "stems"
                    input_path.write_bytes(audio_data)

                    split = separate_vocals(input_path, output_directory)
                    st.session_state["vocal_split_result"] = {
                        "vocals": split.vocals_path.read_bytes(),
                        "instrumental": split.instrumental_path.read_bytes(),
                        "stem": Path(audio_file.name).stem,
                    }
            except (StemSeparationError, OSError) as error:
                st.error("The vocals could not be separated.")
                st.code(str(error))

    result = st.session_state.get("vocal_split_result")
    if result is not None:
        st.success("Your acapella and instrumental are ready.")

        st.subheader("Acapella")
        st.audio(result["vocals"], format="audio/mpeg")
        st.download_button(
            "DOWNLOAD ACAPELLA",
            data=result["vocals"],
            file_name=f"{result['stem']}_acapella.mp3",
            mime="audio/mpeg",
        )

        st.subheader("Instrumental")
        st.audio(result["instrumental"], format="audio/mpeg")
        st.download_button(
            "DOWNLOAD INSTRUMENTAL",
            data=result["instrumental"],
            file_name=f"{result['stem']}_instrumental.mp3",
            mime="audio/mpeg",
        )
