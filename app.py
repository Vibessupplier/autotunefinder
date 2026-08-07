import streamlit as st
import librosa
import numpy as np
import tempfile
import os

st.set_page_config(
    page_title="AutoTune Finder",
    page_icon="🎵",
    layout="centered"
)

# -------------------------
# CUSTOM DESIGN
# -------------------------

st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #151515 0%, #090909 55%, #000000 100%);
    color: white;
}

.block-container {
    max-width: 900px;
    padding-top: 3rem;
}

.neon-title {
    text-align: center;
    font-size: 64px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #ffffff;
    text-shadow:
        0 0 5px #00ffff,
        0 0 10px #00ffff,
        0 0 20px #00ffff,
        0 0 40px #00ffff;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #bdbdbd;
    font-size: 18px;
    margin-bottom: 40px;
}

.result-box {
    background-color: rgba(20, 20, 20, 0.85);
    border: 1px solid #333333;
    border-radius: 16px;
    padding: 25px;
    margin-top: 20px;
}

div.stButton > button {
    width: 100%;
    height: 3.5rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 17px;
    border: 1px solid #00ffff;
    background-color: #090909;
    color: white;
    box-shadow: 0 0 12px rgba(0, 255, 255, 0.3);
}

div.stButton > button:hover {
    border-color: #00ffff;
    color: #00ffff;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.6);
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# TITLE
# -------------------------

st.markdown(
    '<div class="neon-title">AUTOTUNE FINDER</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your vocal or track and detect the estimated key and BPM.'
    '</div>',
    unsafe_allow_html=True
)


# -------------------------
# KEY DETECTION
# -------------------------

major_profile = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
])

minor_profile = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
])

notes = [
    "C", "C#/Db", "D", "D#/Eb", "E", "F",
    "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"
]


def detect_key(y, sr):

    chroma = librosa.feature.chroma_cqt(
        y=y,
        sr=sr
    )

    chroma_mean = np.mean(chroma, axis=1)

    scores = []

    for i in range(12):

        major_score = np.corrcoef(
            chroma_mean,
            np.roll(major_profile, i)
        )[0, 1]

        minor_score = np.corrcoef(
            chroma_mean,
            np.roll(minor_profile, i)
        )[0, 1]

        scores.append(
            (major_score, notes[i], "Major")
        )

        scores.append(
            (minor_score, notes[i], "Minor")
        )

    return max(
        scores,
        key=lambda x: x[0]
    )


# -------------------------
# BPM DETECTION
# -------------------------

def detect_bpm(y, sr):

    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    # Newer librosa versions may return an array
    if isinstance(tempo, np.ndarray):
        tempo = tempo.item()

    return float(tempo)


# -------------------------
# FILE UPLOAD
# -------------------------

audio_file = st.file_uploader(
    "Upload audio",
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

                y, sr = librosa.load(
                    temp_path,
                    mono=True,
                    duration=120
                )

                # KEY
                score, note, mode = detect_key(
                    y,
                    sr
                )

                # BPM
                bpm = detect_bpm(
                    y,
                    sr
                )

                confidence = max(
                    0,
                    min(
                        100,
                        ((score + 1) / 2) * 100
                    )
                )

                st.markdown(
                    '<div class="result-box">',
                    unsafe_allow_html=True
                )

                st.subheader("Analysis")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "KEY",
                        f"{note} {mode}"
                    )

                with col2:

                    st.metric(
                        "BPM",
                        f"{bpm:.1f}"
                    )

                st.markdown(
                    f"### 🎛 Auto-Tune setting: "
                    f"**{note} {mode}**"
                )

                st.write(
                    f"Key confidence: "
                    f"**{confidence:.0f}%**"
                )

                st.caption(
                    "Results are estimates. "
                    "Isolated vocals, tempo changes, "
                    "rap sections or highly chromatic "
                    "music can reduce accuracy."
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            except Exception as e:

                st.error(
                    "The audio file could not be analyzed."
                )

                st.code(
                    str(e)
                )

            finally:

                if os.path.exists(
                    temp_path
                ):

                    os.remove(
                        temp_path
                    )
