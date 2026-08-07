"""Product-level audio effects built on top of the FFmpeg engine."""

from pathlib import Path

from audio_engine import AudioProcessingError, transform_audio


MIN_NIGHTCORE_SPEED = 1.05
MAX_NIGHTCORE_SPEED = 1.50
OUTPUT_SAMPLE_RATE = 48_000


def _validate_nightcore_speed(speed: float) -> None:
    if not MIN_NIGHTCORE_SPEED <= speed <= MAX_NIGHTCORE_SPEED:
        raise AudioProcessingError(
            f"Nightcore speed must be between "
            f"{MIN_NIGHTCORE_SPEED} and {MAX_NIGHTCORE_SPEED}."
        )


def calculate_nightcore_speed(source_bpm: float, target_bpm: float) -> float:
    """Calculate and validate the Nightcore speed for two BPM values."""
    if source_bpm <= 0:
        raise AudioProcessingError("Original BPM must be greater than zero.")

    speed = target_bpm / source_bpm
    _validate_nightcore_speed(speed)

    return speed


def create_nightcore(
    input_path: Path,
    output_path: Path,
    speed: float = 1.20,
) -> Path:
    """Increase playback speed and pitch together for a Nightcore effect."""
    _validate_nightcore_speed(speed)

    filters = [
        f"aresample={OUTPUT_SAMPLE_RATE}",
        f"asetrate={OUTPUT_SAMPLE_RATE}*{speed}",
        f"aresample={OUTPUT_SAMPLE_RATE}",
    ]

    return transform_audio(input_path, output_path, filters=filters)
