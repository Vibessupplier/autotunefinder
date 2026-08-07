import librosa
import numpy as np


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

    return max(scores, key=lambda x: x[0])


def detect_bpm(y, sr):
    tempo, _ = librosa.beat.beat_track(
        y=y,
        sr=sr
    )

    if isinstance(tempo, np.ndarray):
        tempo = tempo.item()

    return float(tempo)
