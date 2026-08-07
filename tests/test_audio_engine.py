from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from audio_engine import transform_audio


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


if __name__ == "__main__":
    unittest.main()
