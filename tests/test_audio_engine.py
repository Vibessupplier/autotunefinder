from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

import numpy as np

from audio_effects import calculate_speed_factor, change_speed
from audio_engine import transform_audio


class AudioEffectsTest(unittest.TestCase):
    def test_calculates_speed_factor_from_bpm(self):
        speed = calculate_speed_factor(123.0, 180.0)

        self.assertAlmostEqual(speed, 180.0 / 123.0)

    def test_accepts_slowest_and_fastest_speed_limits(self):
        self.assertEqual(calculate_speed_factor(120.0, 60.0), 0.50)
        self.assertEqual(calculate_speed_factor(120.0, 240.0), 2.00)


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required")
class AudioEngineIntegrationTest(unittest.TestCase):
    def test_transform_audio_creates_output_file(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            output = Path(temp_directory) / "output.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=0.1",
                    str(source),
                ],
                check=True,
            )

            result = transform_audio(source, output, filters=["volume=0.5"])

            self.assertEqual(result, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 0)

    def test_faster_output_is_shorter_than_source(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            output = Path(temp_directory) / "nightcore.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=1",
                    str(source),
                ],
                check=True,
            )

            change_speed(source, output, speed=1.20)

            self.assertTrue(output.is_file())

            with wave.open(str(source), "rb") as source_audio:
                source_duration = (
                    source_audio.getnframes() / source_audio.getframerate()
                )

            with wave.open(str(output), "rb") as output_audio:
                output_duration = (
                    output_audio.getnframes() / output_audio.getframerate()
                )

            self.assertAlmostEqual(
                output_duration,
                source_duration / 1.20,
                delta=0.02,
            )

    def test_slower_output_is_longer_than_source(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            output = Path(temp_directory) / "slowed.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=1",
                    str(source),
                ],
                check=True,
            )

            change_speed(source, output, speed=0.50)

            with wave.open(str(output), "rb") as output_audio:
                output_duration = (
                    output_audio.getnframes() / output_audio.getframerate()
                )

            self.assertAlmostEqual(output_duration, 2.0, delta=0.02)

    def test_custom_pitch_preserves_requested_duration(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            output = Path(temp_directory) / "pitched.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=1",
                    str(source),
                ],
                check=True,
            )

            change_speed(source, output, speed=1.0, pitch_semitones=12.0)

            with wave.open(str(output), "rb") as output_audio:
                sample_rate = output_audio.getframerate()
                samples = np.frombuffer(
                    output_audio.readframes(output_audio.getnframes()),
                    dtype="<i2",
                )
                output_duration = (
                    len(samples) / sample_rate
                )

            frequencies = np.fft.rfftfreq(len(samples), d=1 / sample_rate)
            dominant_frequency = frequencies[
                np.argmax(np.abs(np.fft.rfft(samples)))
            ]

            self.assertAlmostEqual(output_duration, 1.0, delta=0.03)
            self.assertAlmostEqual(dominant_frequency, 880.0, delta=10.0)


if __name__ == "__main__":
    unittest.main()
