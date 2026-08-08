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


def _ffprobe_executable() -> str:
    executable = shutil.which("ffprobe")

    if executable is None:
        raise AudioProcessingError(
            "FFprobe is not installed or is not available on PATH."
        )

    return executable


def probe_audio_duration(input_path: Path) -> float:
    """Return an audio file's duration in seconds using FFprobe."""
    input_path = Path(input_path)
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")

    command = [
        _ffprobe_executable(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        duration = float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as error:
        details = getattr(error, "stderr", "") or "Invalid audio duration."
        raise AudioProcessingError(details.strip()) from error

    if duration <= 0:
        raise AudioProcessingError("Audio duration must be greater than zero.")

    return duration


def analyze_audio_filter(input_path: Path, audio_filter: str) -> str:
    """Run a read-only FFmpeg audio filter and return its diagnostic output."""
    input_path = Path(input_path)
    if not input_path.is_file():
        raise AudioProcessingError(f"Input audio does not exist: {input_path}")
    if not audio_filter or not audio_filter.strip():
        raise AudioProcessingError("An audio analysis filter is required.")

    command = [
        _ffmpeg_executable(),
        "-hide_banner",
        "-nostats",
        "-i",
        str(input_path),
        "-vn",
        "-af",
        audio_filter,
        "-f",
        "null",
        "-",
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or "Unknown FFmpeg analysis error"
        raise AudioProcessingError(details) from error

    return result.stderr


def transform_audio(
    input_path: Path,
    output_path: Path,
    filters: Optional[Iterable[str]] = None,
    output_duration_seconds: Optional[float] = None,
    input_start_seconds: Optional[float] = None,
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
    ]

    if input_start_seconds is not None:
        if input_start_seconds < 0:
            raise AudioProcessingError("Input start time cannot be negative.")
        command.extend(["-ss", str(input_start_seconds)])

    command.extend(["-i", str(input_path), "-vn"])

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
