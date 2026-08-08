"""Reusable waveform and sample extraction for the Audio Chopper."""

from dataclasses import dataclass
import math
from pathlib import Path
import tempfile

import numpy as np
import soundfile as sf

from audio_engine import AudioProcessingError, transform_audio


WAVEFORM_POINTS = 12_000
CHOPPER_PREVIEW_SECONDS = 30.0
MIN_CLIP_SECONDS = 0.1


class AudioChopperError(RuntimeError):
    """Raised when waveform analysis or sample extraction fails."""


@dataclass(frozen=True)
class WaveformData:
    duration_seconds: float
    peaks: tuple[float, ...]


def _extract_wav_waveform(wav_path: Path, points: int) -> WaveformData:
    if points < 16 or points > 20_000:
        raise AudioChopperError("Waveform resolution must be between 16 and 20000.")

    with sf.SoundFile(wav_path) as audio_file:
        if audio_file.frames <= 0 or audio_file.samplerate <= 0:
            raise AudioChopperError("The audio file contains no samples.")

        duration = audio_file.frames / audio_file.samplerate
        samples_per_bin = max(1, math.ceil(audio_file.frames / points))
        peaks = np.zeros(points, dtype=np.float64)
        sample_offset = 0

        for block in audio_file.blocks(
            blocksize=65536,
            dtype="float32",
            always_2d=True,
        ):
            mono_peaks = np.max(np.abs(block), axis=1)
            bin_indices = (
                sample_offset + np.arange(len(mono_peaks), dtype=np.int64)
            ) // samples_per_bin
            valid = bin_indices < points
            np.maximum.at(peaks, bin_indices[valid], mono_peaks[valid])
            sample_offset += len(block)

    maximum = float(peaks.max())
    if maximum > 1e-12:
        peaks /= maximum

    return WaveformData(
        duration_seconds=duration,
        peaks=tuple(float(value) for value in peaks),
    )


def extract_waveform(
    input_path: Path,
    points: int = WAVEFORM_POINTS,
) -> WaveformData:
    """Decode audio safely and return a normalized static peak envelope."""
    try:
        with tempfile.TemporaryDirectory() as temp_directory:
            decoded_path = Path(temp_directory) / "waveform.wav"
            transform_audio(input_path, decoded_path)
            return _extract_wav_waveform(decoded_path, points)
    except (AudioProcessingError, sf.LibsndfileError) as error:
        raise AudioChopperError(str(error)) from error


def validate_clip_range(
    start_seconds: float,
    end_seconds: float,
    duration_seconds: float,
) -> float:
    """Validate a user-selected range and return its duration."""
    values = (start_seconds, end_seconds, duration_seconds)
    if not all(math.isfinite(value) for value in values):
        raise AudioChopperError("Clip times must be finite values.")
    if duration_seconds <= 0:
        raise AudioChopperError("Audio duration must be greater than zero.")
    if start_seconds < 0 or end_seconds > duration_seconds:
        raise AudioChopperError("The selected clip must stay inside the audio.")
    clip_duration = end_seconds - start_seconds
    if clip_duration < MIN_CLIP_SECONDS:
        raise AudioChopperError(
            f"The selected clip must be at least {MIN_CLIP_SECONDS:.1f} seconds."
        )
    return clip_duration


def create_audio_clip(
    input_path: Path,
    output_path: Path,
    start_seconds: float,
    end_seconds: float,
    source_duration_seconds: float,
    maximum_duration_seconds: float | None = None,
) -> Path:
    """Export a selected range, optionally limiting a listening preview."""
    clip_duration = validate_clip_range(
        start_seconds,
        end_seconds,
        source_duration_seconds,
    )
    if maximum_duration_seconds is not None:
        if maximum_duration_seconds <= 0:
            raise AudioChopperError("Maximum duration must be greater than zero.")
        clip_duration = min(clip_duration, maximum_duration_seconds)

    try:
        return transform_audio(
            input_path,
            output_path,
            input_start_seconds=start_seconds,
            output_duration_seconds=clip_duration,
        )
    except AudioProcessingError as error:
        raise AudioChopperError(str(error)) from error
