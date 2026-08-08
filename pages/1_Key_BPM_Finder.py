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

from ui import load_design, show_header, show_tool_header


# -------------------------
# DESIGN
# -------------------------

load_design()
show_header()
show_tool_header(
    "Analyze / 01",
    "Key & BPM Finder",
    "Read the musical DNA of your track: key, tempo and Camelot position.",
)


# -------------------------
# AUDIO UPLOAD
# -------------------------

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"]
)


if audio_file is not None:

    st.audio(audio_file)

    if st.button("ANALYZE AUDIO", type="primary"):

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

                # -------------------------
                # LOAD AUDIO
                # -------------------------

                y, sr = librosa.load(
                    temp_path,
                    mono=True,
                    duration=120
                )


                # -------------------------
                # KEY DETECTION
                # -------------------------

                results = detect_key(
                    y,
                    sr
                )

                best = results[0]

                score = best["score"]
                note = best["note"]
                mode = best["mode"]


                # -------------------------
                # BPM DETECTION
                # -------------------------

                bpm = detect_bpm(
                    y,
                    sr
                )


                # -------------------------
                # CAMELOT
                # -------------------------

                camelot = get_camelot(
                    note,
                    mode
                )


                # -------------------------
                # BPM ALTERNATIVES
                # -------------------------

                bpm_options = get_bpm_options(
                    bpm
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


                # -------------------------
                # BPM INTERPRETATIONS
                # -------------------------

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


                # -------------------------
                # ALTERNATIVE KEY DETECTION
                # -------------------------

                st.markdown("---")

                st.subheader(
                    "Alternative Detection"
                )

                for candidate in results[1:4]:

                    confidence = max(
                        0,
                        min(
                            100,
                            (
                                (candidate["score"] + 1)
                                / 2
                            ) * 100
                        )
                    )

                    st.write(
                        f"**{candidate['note']} "
                        f"{candidate['mode']}**"
                        f" — {confidence:.0f}%"
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
