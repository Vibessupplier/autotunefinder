from pathlib import Path
import unittest
from unittest.mock import patch

from audio_chopper import (
    AudioChopperError,
    create_audio_clip,
    validate_clip_range,
)


class AudioChopperTest(unittest.TestCase):
    def test_validates_selected_range(self):
        self.assertEqual(validate_clip_range(12.5, 20.0, 60.0), 7.5)

    def test_rejects_range_outside_source(self):
        with self.assertRaisesRegex(AudioChopperError, "inside"):
            validate_clip_range(10.0, 61.0, 60.0)

    @patch("audio_chopper.transform_audio")
    def test_exports_exact_selected_range(self, transform_mock):
        source = Path("track.wav")
        output = Path("sample.mp3")
        transform_mock.return_value = output

        result = create_audio_clip(source, output, 15.0, 23.25, 120.0)

        self.assertEqual(result, output)
        transform_mock.assert_called_once_with(
            source,
            output,
            input_start_seconds=15.0,
            output_duration_seconds=8.25,
        )

    @patch("audio_chopper.transform_audio")
    def test_limits_preview_without_changing_start(self, transform_mock):
        source = Path("track.wav")
        output = Path("preview.mp3")
        transform_mock.return_value = output

        create_audio_clip(
            source,
            output,
            45.0,
            100.0,
            180.0,
            maximum_duration_seconds=30.0,
        )

        transform_mock.assert_called_once_with(
            source,
            output,
            input_start_seconds=45.0,
            output_duration_seconds=30.0,
        )


if __name__ == "__main__":
    unittest.main()
