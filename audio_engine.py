"""Reusable FFmpeg-based audio transformation engine."""

from pathlib import Path
import shutil
import subprocess
from typing import Iterable, Optional


class AudioProcessingError(RuntimeError):
    """Raised when an audio transformation cannot be completed."""


def _ffmpeg_executable() -> str:
    executable = shutil.which("ffmpeg")

    if executable is None:
        raise AudioProcessingError(
            "FFmpeg is not installed or is not available on PATH."
        )

    return executable


def transform_audio(
    input_path: Path,
    output_path: Path,
    filters: Optional[Iterable[str]] = None,
    output_duration_seconds: Optional[float] = None,
) -> Path:
    """Transform an audio file with FFmpeg and return the output path."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        _ffmpeg_executable(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
        "-vn",
    ]

    audio_filters = list(filters or [])
    if audio_filters:
        command.extend(["-af", ",".join(audio_filters)])

    if output_duration_seconds is not None:
        if output_duration_seconds <= 0:
            raise AudioProcessingError(
                "Output duration must be greater than zero."
            )
        command.extend(["-t", str(output_duration_seconds)])

    command.append(str(output_path))

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg error"
        raise AudioProcessingError(details) from error

    return output_path
