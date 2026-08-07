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

def get_camelot(note, mode):

    camelot_map = {
        ("C", "Major"): "8B",
        ("C#/Db", "Major"): "3B",
        ("D", "Major"): "10B",
        ("D#/Eb", "Major"): "5B",
        ("E", "Major"): "12B",
        ("F", "Major"): "7B",
        ("F#/Gb", "Major"): "2B",
        ("G", "Major"): "9B",
        ("G#/Ab", "Major"): "4B",
        ("A", "Major"): "11B",
        ("A#/Bb", "Major"): "6B",
        ("B", "Major"): "1B",

        ("C", "Minor"): "5A",
        ("C#/Db", "Minor"): "12A",
        ("D", "Minor"): "7A",
        ("D#/Eb", "Minor"): "2A",
        ("E", "Minor"): "9A",
        ("F", "Minor"): "4A",
        ("F#/Gb", "Minor"): "11A",
        ("G", "Minor"): "6A",
        ("G#/Ab", "Minor"): "1A",
        ("A", "Minor"): "8A",
        ("A#/Bb", "Minor"): "3A",
        ("B", "Minor"): "10A"
    }

    return camelot_map.get(
        (note, mode),
        "Unknown"
    )


def get_bpm_options(bpm):

    options = [bpm]

    half = bpm / 2
    double = bpm * 2

MIN_BPM = 40
MAX_BPM = 250

def get_bpm_options(bpm):

    options = [bpm]

    half = bpm / 2
    double = bpm * 2

    if MIN_BPM <= half <= MAX_BPM:
        options.append(half)

    if MIN_BPM <= double <= MAX_BPM:
        options.append(double)

    return sorted(set(options))
