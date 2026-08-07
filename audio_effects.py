"""Product-level audio effects built on top of the FFmpeg engine."""

from pathlib import Path

from audio_engine import AudioProcessingError, transform_audio


MIN_NIGHTCORE_SPEED = 1.05
MAX_NIGHTCORE_SPEED = 1.50
OUTPUT_SAMPLE_RATE = 48_000


def create_nightcore(
    input_path: Path,
    output_path: Path,
    speed: float = 1.20,
) -> Path:
    """Increase playback speed and pitch together for a Nightcore effect."""
    if not MIN_NIGHTCORE_SPEED <= speed <= MAX_NIGHTCORE_SPEED:
        raise AudioProcessingError(
            f"Nightcore speed must be between "
            f"{MIN_NIGHTCORE_SPEED} and {MAX_NIGHTCORE_SPEED}."
        )

    filters = [
        f"aresample={OUTPUT_SAMPLE_RATE}",
        f"asetrate={OUTPUT_SAMPLE_RATE}*{speed}",
        f"aresample={OUTPUT_SAMPLE_RATE}",
    ]

    return transform_audio(input_path, output_path, filters=filters)
