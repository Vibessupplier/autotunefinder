from pathlib import Path
import tempfile

import streamlit as st

from audio_effects import create_nightcore
from audio_engine import AudioProcessingError
from ui import load_design, show_header


st.set_page_config(
    page_title="Nightcore Generator | Vibes Supplier",
    page_icon="⚡",
    layout="centered",
)

load_design()
show_header()

st.title("Nightcore Generator")
st.write("Speed up your track and raise its pitch in one step.")

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"],
    key="nightcore_upload",
)

speed = st.slider(
    "Speed",
    min_value=1.05,
    max_value=1.50,
    value=1.20,
    step=0.05,
    format="%.2fx",
)

if audio_file is not None:
    st.audio(audio_file)

    settings_signature = (audio_file.name, audio_file.size, speed)
    if st.session_state.get("nightcore_settings") != settings_signature:
        st.session_state.pop("nightcore_result", None)
        st.session_state["nightcore_settings"] = settings_signature

    if st.button("CREATE NIGHTCORE"):
        with st.spinner("Creating your Nightcore version..."):
            try:
                suffix = Path(audio_file.name).suffix.lower()

                with tempfile.TemporaryDirectory() as temp_directory:
                    input_path = Path(temp_directory) / f"input{suffix}"
                    output_path = Path(temp_directory) / "nightcore.mp3"

                    input_path.write_bytes(audio_file.getvalue())
                    create_nightcore(input_path, output_path, speed=speed)

                    st.session_state["nightcore_result"] = {
                        "audio": output_path.read_bytes(),
                        "filename": f"{Path(audio_file.name).stem}_nightcore.mp3",
                    }

            except (AudioProcessingError, OSError) as error:
                st.error("The Nightcore version could not be created.")
                st.code(str(error))

    result = st.session_state.get("nightcore_result")
    if result is not None:
        st.success("Your Nightcore version is ready.")
        st.audio(result["audio"], format="audio/mpeg")
        st.download_button(
            "DOWNLOAD MP3",
            data=result["audio"],
            file_name=result["filename"],
            mime="audio/mpeg",
        )
