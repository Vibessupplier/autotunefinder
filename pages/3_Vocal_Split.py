from pathlib import Path
import tempfile

import streamlit as st

from stem_separation import StemSeparationError, separate_vocals
from ui import load_design, show_header


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
        st.session_state.pop("vocal_split_result", None)
        st.session_state["vocal_split_signature"] = upload_signature

    if st.button("SEPARATE VOCALS"):
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
