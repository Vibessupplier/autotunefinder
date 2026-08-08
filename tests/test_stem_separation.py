from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from stem_separation import StemSeparationError, separate_vocals


class StemSeparationTest(unittest.TestCase):
    @patch("stem_separation.subprocess.run")
    def test_separates_vocals_and_instrumental_with_safe_command(self, run_mock):
        with tempfile.TemporaryDirectory() as temp_directory:
            temporary_path = Path(temp_directory)
            source = temporary_path / "source.mp3"
            output = temporary_path / "output"
            source.touch()

            def create_stems(command, **kwargs):
                stem_directory = output / "htdemucs" / "source"
                stem_directory.mkdir(parents=True)
                (stem_directory / "vocals.mp3").touch()
                (stem_directory / "no_vocals.mp3").touch()

            run_mock.side_effect = create_stems

            result = separate_vocals(source, output)

            command = run_mock.call_args.args[0]
            self.assertIn("--two-stems", command)
            self.assertIn("vocals", command)
            self.assertIn("--device", command)
            self.assertIn("cpu", command)
            self.assertEqual(command[-1], str(source))
            self.assertTrue(result.vocals_path.name == "vocals.mp3")
            self.assertTrue(
                result.instrumental_path.name == "no_vocals.mp3"
            )
            run_mock.assert_called_once()
            self.assertTrue(run_mock.call_args.kwargs["check"])

    @patch("stem_separation.subprocess.run")
    def test_reports_demucs_processing_errors(self, run_mock):
        with tempfile.TemporaryDirectory() as temp_directory:
            source = Path(temp_directory) / "source.wav"
            source.touch()
            run_mock.side_effect = subprocess.CalledProcessError(
                1,
                ["demucs"],
                stderr="Separation failed",
            )

            with self.assertRaisesRegex(
                StemSeparationError, "Separation failed"
            ):
                separate_vocals(source, Path(temp_directory) / "output")

    def test_rejects_missing_input(self):
        with self.assertRaisesRegex(StemSeparationError, "does not exist"):
            separate_vocals(Path("missing.wav"), Path("output"))


if __name__ == "__main__":
    unittest.main()
