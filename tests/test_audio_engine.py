from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import wave

import numpy as np

from audio_effects import (
    SPEED_PREVIEW_SECONDS,
    calculate_speed_factor,
    change_speed,
    create_speed_preview,
)
from audio_engine import (
    AudioProcessingError,
    probe_audio_duration,
    transform_audio,
)


class AudioEffectsTest(unittest.TestCase):
    def test_calculates_speed_factor_from_bpm(self):
        speed = calculate_speed_factor(123.0, 180.0)

        self.assertAlmostEqual(speed, 180.0 / 123.0)

    def test_accepts_slowest_and_fastest_speed_limits(self):
        self.assertEqual(calculate_speed_factor(120.0, 60.0), 0.50)
        self.assertEqual(calculate_speed_factor(120.0, 240.0), 2.00)

    @patch("audio_effects.transform_audio")
    def test_preview_uses_selected_processing_and_20_second_limit(
        self, transform_audio_mock
    ):
        source = Path("source.wav")
        output = Path("preview.mp3")
        transform_audio_mock.return_value = output

        result = create_speed_preview(
            source,
            output,
            speed=1.25,
            pitch_semitones=-2.0,
        )

        self.assertEqual(result, output)
        call = transform_audio_mock.call_args
        self.assertEqual(call.args[:2], (source, output))
        self.assertEqual(
            call.kwargs["output_duration_seconds"], SPEED_PREVIEW_SECONDS
        )
        filters = call.kwargs["filters"]
        self.assertIn("asetrate=48000*0.8908987181403393", filters)
        self.assertIn("atempo=1.4030775603867163", filters)

    def test_rejects_non_positive_output_duration(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            source.touch()

            with self.assertRaises(AudioProcessingError):
                transform_audio(
                    source,
                    Path(temp_directory) / "output.wav",
                    output_duration_seconds=0,
                )


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

    def test_probes_audio_duration(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=1.5",
                    str(source),
                ],
                check=True,
            )

            self.assertAlmostEqual(probe_audio_duration(source), 1.5, places=2)

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

    def test_preview_is_limited_to_20_processed_seconds(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            output = Path(temp_directory) / "preview.wav"

            subprocess.run(
                [
                    shutil.which("ffmpeg"),
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:duration=25",
                    str(source),
                ],
                check=True,
            )

            create_speed_preview(
                source,
                output,
                speed=0.8,
                pitch_semitones=3.0,
            )

            with wave.open(str(output), "rb") as preview_audio:
                preview_duration = (
                    preview_audio.getnframes() / preview_audio.getframerate()
                )

            self.assertAlmostEqual(preview_duration, 20.0, delta=0.03)


if __name__ == "__main__":
    unittest.main()
