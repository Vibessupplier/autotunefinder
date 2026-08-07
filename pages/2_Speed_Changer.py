from pathlib import Path
import math
import tempfile

import streamlit as st

from audio_analysis import detect_bpm_from_file
from audio_effects import (
    MAX_PITCH_SEMITONES,
    MAX_SPEED_FACTOR,
    MIN_PITCH_SEMITONES,
    MIN_SPEED_FACTOR,
    calculate_speed_factor,
    change_speed,
)
from audio_engine import AudioProcessingError
from ui import load_design, show_header


@st.cache_data(show_spinner=False)
def detect_uploaded_bpm(audio_data: bytes, suffix: str) -> float:
    """Cache BPM detection so UI reruns do not analyze the same file again."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"input{suffix}"
        input_path.write_bytes(audio_data)
        return detect_bpm_from_file(input_path)

load_design()
show_header()

st.title("Speed Changer")
st.write("Choose an exact target BPM and change your track's speed.")

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"],
    key="speed_upload",
)

if audio_file is not None:
    st.audio(audio_file)

    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = (audio_file.name, audio_file.size)

    if st.session_state.get("speed_upload_signature") != upload_signature:
        with st.spinner("Detecting original BPM..."):
            try:
                detected_bpm = detect_uploaded_bpm(audio_data, suffix)
            except Exception as error:
                st.error("The original BPM could not be detected.")
                st.code(str(error))
                st.stop()

        st.session_state["speed_source_bpm"] = round(detected_bpm, 1)
        st.session_state.pop("speed_target_bpm", None)
        st.session_state.pop("speed_result", None)
        st.session_state["speed_upload_signature"] = upload_signature

    source_bpm = st.number_input(
        "Original BPM",
        min_value=40.0,
        max_value=250.0,
        step=0.1,
        help="This is an estimate. Correct it if you know the exact BPM.",
        key="speed_source_bpm",
    )

    minimum_target = math.ceil(source_bpm * MIN_SPEED_FACTOR * 10) / 10
    maximum_target = math.floor(
        min(source_bpm * MAX_SPEED_FACTOR, 300.0) * 10
    ) / 10
    default_target = round(min(source_bpm * 1.20, maximum_target), 1)

    current_target = st.session_state.get("speed_target_bpm")
    if (
        current_target is None
        or not minimum_target <= current_target <= maximum_target
    ):
        st.session_state["speed_target_bpm"] = default_target

    target_bpm = st.slider(
        "Target BPM",
        min_value=minimum_target,
        max_value=maximum_target,
        step=0.1,
        key="speed_target_bpm",
    )

    speed = calculate_speed_factor(source_bpm, target_bpm)

    pitch_mode = st.radio(
        "Pitch",
        options=["Follow speed", "Keep original", "Custom"],
        horizontal=True,
        help=(
            "Follow speed changes pitch naturally. Keep original locks the key. "
            "Custom lets you choose a pitch shift."
        ),
    )

    if pitch_mode == "Follow speed":
        pitch_semitones = 12 * math.log2(speed)
        processing_pitch = None
    elif pitch_mode == "Keep original":
        pitch_semitones = 0.0
        processing_pitch = 0.0
    else:
        pitch_semitones = st.slider(
            "Pitch shift (semitones)",
            min_value=MIN_PITCH_SEMITONES,
            max_value=MAX_PITCH_SEMITONES,
            value=0.0,
            step=0.5,
        )
        processing_pitch = pitch_semitones

    st.caption(f"Speed: {speed:.3f}x · Pitch: {pitch_semitones:+.1f} semitones")

    settings_signature = (
        audio_file.name,
        audio_file.size,
        source_bpm,
        target_bpm,
        pitch_mode,
        pitch_semitones,
    )
    if st.session_state.get("speed_settings") != settings_signature:
        st.session_state.pop("speed_result", None)
        st.session_state["speed_settings"] = settings_signature

    if st.button("CHANGE SPEED"):
        with st.spinner("Changing your track's speed..."):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    input_path = Path(temp_directory) / f"input{suffix}"
                    output_path = Path(temp_directory) / "speed-changed.mp3"

                    input_path.write_bytes(audio_data)
                    change_speed(
                        input_path,
                        output_path,
                        speed=speed,
                        pitch_semitones=processing_pitch,
                    )

                    st.session_state["speed_result"] = {
                        "audio": output_path.read_bytes(),
                        "filename": (
                            f"{Path(audio_file.name).stem}_speed-changed.mp3"
                        ),
                        "source_bpm": source_bpm,
                        "target_bpm": target_bpm,
                        "pitch_semitones": pitch_semitones,
                    }

            except (AudioProcessingError, OSError) as error:
                st.error("The speed-changed version could not be created.")
                st.code(str(error))

    result = st.session_state.get("speed_result")
    if result is not None:
        st.success("Your speed-changed version is ready.")
        st.write(
            f"**{result['source_bpm']:.1f} BPM → "
            f"{result['target_bpm']:.1f} BPM**"
        )
        st.write(f"**Pitch: {result['pitch_semitones']:+.1f} semitones**")
        st.audio(result["audio"], format="audio/mpeg")
        st.download_button(
            "DOWNLOAD MP3",
            data=result["audio"],
            file_name=result["filename"],
            mime="audio/mpeg",
        )
