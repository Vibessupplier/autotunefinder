from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from stem_separation import (
    VOCAL_PREVIEW_SECONDS,
    StemSeparationError,
    VocalSplitResult,
    create_vocal_split_preview,
    separate_vocals,
)


class StemSeparationTest(unittest.TestCase):
    @patch("stem_separation.separate_vocals")
    @patch("stem_separation.transform_audio")
    def test_preview_extracts_only_selected_20_seconds(
        self, transform_mock, separate_mock
    ):
        source = Path("source.mp3")
        preview = Path("preview.wav")
        output = Path("output")
        expected = VocalSplitResult(
            Path("vocals.mp3"), Path("no_vocals.mp3")
        )
        separate_mock.return_value = expected

        result = create_vocal_split_preview(
            source,
            preview,
            output,
            start_seconds=45.0,
        )

        self.assertEqual(result, expected)
        transform_mock.assert_called_once_with(
            source,
            preview,
            input_start_seconds=45.0,
            output_duration_seconds=VOCAL_PREVIEW_SECONDS,
        )
        separate_mock.assert_called_once_with(preview, output)

    def test_preview_rejects_negative_start_time(self):
        with self.assertRaisesRegex(StemSeparationError, "cannot be negative"):
            create_vocal_split_preview(
                Path("source.mp3"),
                Path("preview.wav"),
                Path("output"),
                start_seconds=-1.0,
            )

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
