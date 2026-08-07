from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

from audio_effects import calculate_nightcore_speed, create_nightcore
from audio_engine import transform_audio


class AudioEffectsTest(unittest.TestCase):
    def test_calculates_nightcore_speed_from_bpm(self):
        speed = calculate_nightcore_speed(123.0, 180.0)

        self.assertAlmostEqual(speed, 180.0 / 123.0)


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

    def test_nightcore_output_is_shorter_than_source(self):
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

            create_nightcore(source, output, speed=1.20)

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


if __name__ == "__main__":
    unittest.main()
