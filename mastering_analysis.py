"""Reusable mastering-oriented loudness and level analysis."""

from dataclasses import dataclass
import math
from pathlib import Path
import re
import tempfile

import soundfile as sf

from audio_engine import (
    AudioProcessingError,
    analyze_audio_filter,
    probe_audio_duration,
    transform_audio,
)


MASTERING_FILTER = "ebur128=peak=true,astats=metadata=0:reset=0"
NUMBER_PATTERN = r"[-+]?(?:\d+(?:\.\d+)?|inf)"


class MasteringAnalysisError(RuntimeError):
    """Raised when mastering measurements cannot be produced."""


@dataclass(frozen=True)
class MasteringMetrics:
    integrated_lufs: float
    loudness_range_lu: float
    true_peak_dbfs: float
    sample_peak_dbfs: float
    rms_level_dbfs: float
    duration_seconds: float


@dataclass(frozen=True)
class StereoMetrics:
    channels: int
    balance_db: float
    width_percent: float
    correlation: float


def _last_measurement(output: str, label: str) -> float:
    matches = re.findall(
        rf"{re.escape(label)}:\s*({NUMBER_PATTERN})",
        output,
        flags=re.IGNORECASE,
    )
    if not matches:
        raise MasteringAnalysisError(f"FFmpeg did not report {label}.")
    return float(matches[-1])


def parse_mastering_output(
    output: str,
    duration_seconds: float,
) -> MasteringMetrics:
    """Parse the final EBU R128 and astats summaries from FFmpeg output."""
    if "Summary:" not in output:
        raise MasteringAnalysisError("FFmpeg did not report a loudness summary.")

    summary = output.rsplit("Summary:", maxsplit=1)[-1]
    integrated_lufs = _last_measurement(summary, "I")
    loudness_range_lu = _last_measurement(summary, "LRA")
    true_peak_dbfs = _last_measurement(summary, "Peak")

    overall = output.rsplit("Overall", maxsplit=1)[-1]
    sample_peak_dbfs = _last_measurement(overall, "Peak level dB")
    rms_level_dbfs = _last_measurement(overall, "RMS level dB")

    values = (
        integrated_lufs,
        loudness_range_lu,
        true_peak_dbfs,
        sample_peak_dbfs,
        rms_level_dbfs,
        duration_seconds,
    )
    if not all(math.isfinite(value) for value in values):
        raise MasteringAnalysisError(
            "The track is too quiet to produce reliable mastering measurements."
        )
    if duration_seconds <= 0:
        raise MasteringAnalysisError("Audio duration must be greater than zero.")

    return MasteringMetrics(
        integrated_lufs=integrated_lufs,
        loudness_range_lu=loudness_range_lu,
        true_peak_dbfs=true_peak_dbfs,
        sample_peak_dbfs=sample_peak_dbfs,
        rms_level_dbfs=rms_level_dbfs,
        duration_seconds=duration_seconds,
    )


def analyze_mastering(input_path: Path) -> MasteringMetrics:
    """Measure loudness and levels without modifying the source audio."""
    try:
        duration = probe_audio_duration(input_path)
        output = analyze_audio_filter(input_path, MASTERING_FILTER)
        return parse_mastering_output(output, duration)
    except AudioProcessingError as error:
        raise MasteringAnalysisError(str(error)) from error


def _db_ratio(numerator: float, denominator: float) -> float:
    floor = 1e-12
    ratio = max(numerator, floor) / max(denominator, floor)
    return max(-60.0, min(60.0, 20.0 * math.log10(ratio)))


def _analyze_stereo_wav(wav_path: Path) -> StereoMetrics:
    """Measure stereo energy by blocks without loading the track into memory."""
    with sf.SoundFile(wav_path) as audio_file:
        channels = audio_file.channels
        if channels == 1:
            return StereoMetrics(
                channels=1,
                balance_db=0.0,
                width_percent=0.0,
                correlation=1.0,
            )
        if channels != 2:
            raise MasteringAnalysisError(
                "Stereo analysis currently supports mono or stereo audio."
            )

        sample_count = 0
        sum_left = 0.0
        sum_right = 0.0
        sum_left_squared = 0.0
        sum_right_squared = 0.0
        sum_cross = 0.0

        for block in audio_file.blocks(
            blocksize=65536,
            dtype="float32",
            always_2d=True,
        ):
            left = block[:, 0].astype("float64", copy=False)
            right = block[:, 1].astype("float64", copy=False)
            sample_count += len(block)
            sum_left += float(left.sum())
            sum_right += float(right.sum())
            sum_left_squared += float(left @ left)
            sum_right_squared += float(right @ right)
            sum_cross += float(left @ right)

    if sample_count == 0:
        raise MasteringAnalysisError("The audio file contains no samples.")

    mean_left = sum_left / sample_count
    mean_right = sum_right / sample_count
    left_variance = max(
        sum_left_squared / sample_count - mean_left**2,
        0.0,
    )
    right_variance = max(
        sum_right_squared / sample_count - mean_right**2,
        0.0,
    )
    covariance = sum_cross / sample_count - mean_left * mean_right

    left_rms = math.sqrt(sum_left_squared / sample_count)
    right_rms = math.sqrt(sum_right_squared / sample_count)
    balance_db = _db_ratio(right_rms, left_rms)

    mid_energy = max(
        (sum_left_squared + 2.0 * sum_cross + sum_right_squared)
        / (4.0 * sample_count),
        0.0,
    )
    side_energy = max(
        (sum_left_squared - 2.0 * sum_cross + sum_right_squared)
        / (4.0 * sample_count),
        0.0,
    )
    mid_rms = math.sqrt(mid_energy)
    side_rms = math.sqrt(side_energy)
    width_denominator = mid_rms + side_rms
    width_percent = (
        0.0
        if width_denominator <= 1e-12
        else 100.0 * side_rms / width_denominator
    )

    correlation_denominator = math.sqrt(left_variance * right_variance)
    correlation = (
        1.0
        if correlation_denominator <= 1e-12
        else covariance / correlation_denominator
    )
    correlation = max(-1.0, min(1.0, correlation))

    return StereoMetrics(
        channels=2,
        balance_db=balance_db,
        width_percent=width_percent,
        correlation=correlation,
    )


def analyze_stereo(input_path: Path) -> StereoMetrics:
    """Decode a source safely and return static stereo-field measurements."""
    try:
        with tempfile.TemporaryDirectory() as temp_directory:
            decoded_path = Path(temp_directory) / "stereo-analysis.wav"
            transform_audio(input_path, decoded_path)
            return _analyze_stereo_wav(decoded_path)
    except (AudioProcessingError, sf.LibsndfileError) as error:
        raise MasteringAnalysisError(str(error)) from error


def calculate_volume_match_gains(
    reference_lufs: float,
    track_lufs: float,
) -> tuple[float, float]:
    """Return non-positive gains that match both tracks to the quieter one."""
    if not math.isfinite(reference_lufs) or not math.isfinite(track_lufs):
        raise MasteringAnalysisError("Volume Match requires finite LUFS values.")

    target_lufs = min(reference_lufs, track_lufs)
    return target_lufs - reference_lufs, target_lufs - track_lufs


def create_volume_matched_audio(
    input_path: Path,
    output_path: Path,
    gain_db: float,
) -> Path:
    """Create a listening copy with a validated, attenuation-only gain."""
    if not math.isfinite(gain_db) or gain_db > 0:
        raise MasteringAnalysisError(
            "Volume Match gain must be a finite attenuation value."
        )

    try:
        return transform_audio(
            input_path,
            output_path,
            filters=[f"volume={gain_db:.4f}dB"],
        )
    except AudioProcessingError as error:
        raise MasteringAnalysisError(str(error)) from error
