"""Product-level audio effects built on top of the FFmpeg engine."""

import math
from pathlib import Path
from typing import Optional

from audio_engine import AudioProcessingError, transform_audio


MIN_SPEED_FACTOR = 0.50
MAX_SPEED_FACTOR = 2.00
MIN_PITCH_SEMITONES = -12.0
MAX_PITCH_SEMITONES = 12.0
OUTPUT_SAMPLE_RATE = 48_000


def _validate_speed_factor(speed: float) -> None:
    if not MIN_SPEED_FACTOR <= speed <= MAX_SPEED_FACTOR:
        raise AudioProcessingError(
            f"Speed factor must be between "
            f"{MIN_SPEED_FACTOR} and {MAX_SPEED_FACTOR}."
        )


def calculate_speed_factor(source_bpm: float, target_bpm: float) -> float:
    """Calculate and validate the playback speed for two BPM values."""
    if source_bpm <= 0:
        raise AudioProcessingError("Original BPM must be greater than zero.")

    speed = target_bpm / source_bpm
    _validate_speed_factor(speed)

    return speed


def _atempo_filters(factor: float) -> list[str]:
    """Split a tempo factor into high-quality FFmpeg atempo stages."""
    filters = []

    while factor < 0.50:
        filters.append("atempo=0.5")
        factor /= 0.50

    while factor > 2.00:
        filters.append("atempo=2.0")
        factor /= 2.00

    if not math.isclose(factor, 1.0):
        filters.append(f"atempo={factor}")

    return filters


def change_speed(
    input_path: Path,
    output_path: Path,
    speed: float = 1.20,
    pitch_semitones: Optional[float] = None,
) -> Path:
    """Change speed and optionally control pitch independently."""
    _validate_speed_factor(speed)

    if pitch_semitones is None:
        pitch_factor = speed
    else:
        if not MIN_PITCH_SEMITONES <= pitch_semitones <= MAX_PITCH_SEMITONES:
            raise AudioProcessingError(
                f"Pitch must be between {MIN_PITCH_SEMITONES} and "
                f"{MAX_PITCH_SEMITONES} semitones."
            )
        pitch_factor = 2 ** (pitch_semitones / 12)

    filters = [
        f"aresample={OUTPUT_SAMPLE_RATE}",
        f"asetrate={OUTPUT_SAMPLE_RATE}*{pitch_factor}",
        f"aresample={OUTPUT_SAMPLE_RATE}",
    ]
    filters.extend(_atempo_filters(speed / pitch_factor))

    return transform_audio(input_path, output_path, filters=filters)
