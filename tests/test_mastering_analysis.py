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
    analyze_spectral_balance,
    analyze_stereo,
    calculate_volume_match_gains,
    create_volume_matched_audio,
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
    def test_volume_match_attenuates_only_the_louder_track(self):
        reference_gain, track_gain = calculate_volume_match_gains(-9.0, -12.5)

        self.assertEqual(reference_gain, -3.5)
        self.assertEqual(track_gain, 0.0)

    def test_volume_match_handles_quieter_reference(self):
        reference_gain, track_gain = calculate_volume_match_gains(-14.0, -10.0)

        self.assertEqual(reference_gain, 0.0)
        self.assertEqual(track_gain, -4.0)

    @patch("mastering_analysis.transform_audio")
    def test_volume_match_uses_shared_audio_engine(self, transform_mock):
        source = Path("source.wav")
        output = Path("matched.wav")
        transform_mock.return_value = output

        result = create_volume_matched_audio(source, output, -2.25)

        self.assertEqual(result, output)
        transform_mock.assert_called_once_with(
            source,
            output,
            filters=["volume=-2.2500dB"],
        )

    def test_volume_match_rejects_gain_boost(self):
        with self.assertRaisesRegex(MasteringAnalysisError, "attenuation"):
            create_volume_matched_audio(Path("source.wav"), Path("out.wav"), 1.0)

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
    def test_places_low_tone_in_sub_band(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "sub.wav"
            sample_rate = 48000
            time = np.arange(sample_rate, dtype=np.float64) / sample_rate
            tone = 0.25 * np.sin(2 * np.pi * 50 * time)
            sf.write(source, tone, sample_rate)

            metrics = analyze_spectral_balance(source)

            bands = dict(metrics.items())
            self.assertGreater(bands["Sub"], 90.0)
            self.assertAlmostEqual(sum(bands.values()), 100.0, places=5)

    def test_places_high_tone_in_highs_band(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "highs.wav"
            sample_rate = 48000
            time = np.arange(sample_rate, dtype=np.float64) / sample_rate
            tone = 0.25 * np.sin(2 * np.pi * 8000 * time)
            sf.write(source, tone, sample_rate)

            bands = dict(analyze_spectral_balance(source).items())

            self.assertGreater(bands["Highs"], 99.0)

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
