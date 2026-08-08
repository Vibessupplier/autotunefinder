"""Reusable mastering-oriented loudness and level analysis."""

from dataclasses import dataclass
import math
from pathlib import Path
import re

from audio_engine import (
    AudioProcessingError,
    analyze_audio_filter,
    probe_audio_duration,
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
