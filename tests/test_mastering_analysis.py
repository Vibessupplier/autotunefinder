from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import soundfile as sf

from mastering_analysis import (
    MASTERING_FILTER,
    MasteringAnalysisError,
    analyze_mastering,
    analyze_stereo,
    parse_mastering_output,
)


SAMPLE_OUTPUT = """
[Parsed_ebur128] Summary:

  Integrated loudness:
    I:         -11.8 LUFS
    Threshold: -21.8 LUFS

  Loudness range:
    LRA:         4.2 LU

  True peak:
    Peak:       -0.8 dBFS
[Parsed_astats] Overall
[Parsed_astats] Peak level dB: -1.024000
[Parsed_astats] RMS level dB: -13.420000
"""


class MasteringAnalysisTest(unittest.TestCase):
    def test_parses_final_loudness_and_level_summaries(self):
        metrics = parse_mastering_output(SAMPLE_OUTPUT, 183.5)

        self.assertEqual(metrics.integrated_lufs, -11.8)
        self.assertEqual(metrics.loudness_range_lu, 4.2)
        self.assertEqual(metrics.true_peak_dbfs, -0.8)
        self.assertEqual(metrics.sample_peak_dbfs, -1.024)
        self.assertEqual(metrics.rms_level_dbfs, -13.42)
        self.assertEqual(metrics.duration_seconds, 183.5)

    def test_rejects_missing_loudness_summary(self):
        with self.assertRaisesRegex(MasteringAnalysisError, "loudness summary"):
            parse_mastering_output("invalid output", 10.0)

    @patch("mastering_analysis.analyze_audio_filter")
    @patch("mastering_analysis.probe_audio_duration", return_value=183.5)
    def test_uses_shared_ffmpeg_analysis_engine(
        self,
        duration_mock,
        analyze_filter_mock,
    ):
        analyze_filter_mock.return_value = SAMPLE_OUTPUT
        source = Path("master.wav")

        metrics = analyze_mastering(source)

        duration_mock.assert_called_once_with(source)
        analyze_filter_mock.assert_called_once_with(source, MASTERING_FILTER)
        self.assertEqual(metrics.integrated_lufs, -11.8)


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required")
class MasteringAnalysisIntegrationTest(unittest.TestCase):
    def test_analyzes_synthetic_audio(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "tone.wav"
            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=1000:duration=2",
                    "-af",
                    "volume=0.1",
                    str(source),
                ],
                check=True,
            )

            metrics = analyze_mastering(source)

            self.assertAlmostEqual(metrics.duration_seconds, 2.0, places=2)
            self.assertLess(metrics.integrated_lufs, -35.0)
            self.assertLessEqual(metrics.true_peak_dbfs, 0.0)
            self.assertLessEqual(metrics.sample_peak_dbfs, 0.0)

    def test_measures_balanced_correlated_stereo(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "stereo.wav"
            sample_rate = 48000
            time = np.arange(sample_rate, dtype=np.float64) / sample_rate
            tone = 0.25 * np.sin(2 * np.pi * 440 * time)
            sf.write(source, np.column_stack((tone, tone)), sample_rate)

            metrics = analyze_stereo(source)

            self.assertEqual(metrics.channels, 2)
            self.assertAlmostEqual(metrics.balance_db, 0.0, places=2)
            self.assertLess(metrics.width_percent, 0.1)
            self.assertGreater(metrics.correlation, 0.999)

    def test_detects_right_channel_attenuation(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "unbalanced.wav"
            sample_rate = 48000
            time = np.arange(sample_rate, dtype=np.float64) / sample_rate
            left = 0.25 * np.sin(2 * np.pi * 440 * time)
            right = left * 0.5
            sf.write(source, np.column_stack((left, right)), sample_rate)

            metrics = analyze_stereo(source)

            self.assertAlmostEqual(metrics.balance_db, -6.02, delta=0.05)

    def test_detects_out_of_phase_stereo(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "phase.wav"
            sample_rate = 48000
            time = np.arange(sample_rate, dtype=np.float64) / sample_rate
            left = 0.25 * np.sin(2 * np.pi * 440 * time)
            sf.write(source, np.column_stack((left, -left)), sample_rate)

            metrics = analyze_stereo(source)

            self.assertGreater(metrics.width_percent, 99.9)
            self.assertLess(metrics.correlation, -0.999)


if __name__ == "__main__":
    unittest.main()
