"""Product-level vocal separation using a local Demucs process."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from audio_engine import AudioProcessingError, transform_audio


VOCAL_PREVIEW_SECONDS = 20.0


class StemSeparationError(RuntimeError):
    """Raised when vocal separation cannot be completed."""


@dataclass(frozen=True)
class VocalSplitResult:
    vocals_path: Path
    instrumental_path: Path


def create_vocal_split_preview(
    input_path: Path,
    preview_path: Path,
    output_directory: Path,
    start_seconds: float,
) -> VocalSplitResult:
    """Extract and separate a 20-second vocal preview."""
    if start_seconds < 0:
        raise StemSeparationError("Preview start time cannot be negative.")

    try:
        transform_audio(
            input_path,
            preview_path,
            input_start_seconds=start_seconds,
            output_duration_seconds=VOCAL_PREVIEW_SECONDS,
        )
    except AudioProcessingError as error:
        raise StemSeparationError(str(error)) from error

    return separate_vocals(preview_path, output_directory)


def separate_vocals(
    input_path: Path,
    output_directory: Path,
) -> VocalSplitResult:
    """Separate an audio file into vocal and instrumental MP3 stems."""
    input_path = Path(input_path)
    output_directory = Path(output_directory)

    if not input_path.is_file():
        raise StemSeparationError(f"Input audio does not exist: {input_path}")

    output_directory.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "demucs.separate",
        "--two-stems",
        "vocals",
        "--mp3",
        "--mp3-bitrate",
        "320",
        "--device",
        "cpu",
        "--jobs",
        "1",
        "--out",
        str(output_directory),
        str(input_path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        details = error.stderr.strip() or error.stdout.strip()
        if "No module named" in details and "demucs" in details:
            details = "Demucs is not installed in the local environment."
        raise StemSeparationError(
            details or "Unknown Demucs separation error."
        ) from error

    vocal_files = list(output_directory.rglob("vocals.mp3"))
    instrumental_files = list(output_directory.rglob("no_vocals.mp3"))
    if len(vocal_files) != 1 or len(instrumental_files) != 1:
        raise StemSeparationError("Demucs did not create both expected stems.")

    return VocalSplitResult(
        vocals_path=vocal_files[0],
        instrumental_path=instrumental_files[0],
    )
