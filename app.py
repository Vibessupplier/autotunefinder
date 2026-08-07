import streamlit as st
import librosa
import tempfile
import os

from audio_analysis import (
    detect_key,
    detect_bpm,
    get_camelot,
    get_bpm_options
)

from ui import load_design, show_header


# -------------------------
# PAGE CONFIGURATION
# -------------------------

st.set_page_config(
    page_title="AutoTune Finder",
    page_icon="🎵",
    layout="centered"
)


# -------------------------
# DESIGN
# -------------------------

load_design()
show_header()


# -------------------------
# AUDIO UPLOAD
# -------------------------

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"]
)


if audio_file is not None:

    st.audio(audio_file)

    if st.button("ANALYZE AUDIO"):

        with st.spinner("Analyzing audio..."):

            suffix = os.path.splitext(
                audio_file.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as tmp_file:

                tmp_file.write(
                    audio_file.getvalue()
                )

                temp_path = tmp_file.name

            try:

                # Load audio
                y, sr = librosa.load(
                    temp_path,
                    mono=True,
                    duration=120
                )

                # Analyze key
                score, note, mode = detect_key(
                    y,
                    sr
                )

                # Analyze BPM
                bpm = detect_bpm(
                    y,
                    sr
                )

                # Camelot
                camelot = get_camelot(
                    note,
                    mode
                )

                # Alternative BPM interpretations
                bpm_options = get_bpm_options(
                    bpm
                )

                # Approximate confidence
                confidence = max(
                    0,
                    min(
                        100,
                        ((score + 1) / 2) * 100
                    )
                )


                # -------------------------
                # RESULTS
                # -------------------------

                st.subheader("TRACK ANALYSIS")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "KEY",
                        f"{note} {mode}"
                    )

                with col2:
                    st.metric(
                        "CAMELOT",
                        camelot
                    )

                with col3:
                    st.metric(
                        "BPM",
                        f"{bpm:.1f}"
                    )


                # Alternative BPM
                alternatives = [
                    f"{value:.1f}"
                    for value in bpm_options
                    if abs(value - bpm) > 0.1
                ]

                if alternatives:
                    st.caption(
                        "Possible tempo interpretation: "
                        + " / ".join(alternatives)
                        + " BPM"
                    )


                st.markdown(
                    f"### 🎛 Auto-Tune Setting: "
                    f"**{note} {mode}**"
                )

                st.write(
                    f"Key confidence: "
                    f"**{confidence:.0f}%**"
                )

                st.caption(
                    "Results are estimates. "
                    "Complex arrangements, tempo changes "
                    "or highly chromatic music may reduce accuracy."
                )


            except Exception as e:

                st.error(
                    "The audio file could not be analyzed."
                )

                st.code(
                    str(e)
                )


            finally:

                if os.path.exists(temp_path):
                    os.remove(temp_path)
