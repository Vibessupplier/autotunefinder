import io
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
import zipfile

from cloud_stem_separation import (
    CloudStemSeparationError,
    separate_vocals_in_cloud,
)


ENDPOINT = "https://test.eu-west.modal.direct"


def stem_archive() -> bytes:
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w") as archive:
        archive.writestr("acapella.mp3", b"vocals")
        archive.writestr("instrumental.mp3", b"instrumental")
    return archive_buffer.getvalue()


class CloudStemSeparationTest(unittest.TestCase):
    @patch("cloud_stem_separation.urlopen")
    def test_calls_private_modal_endpoint_and_reads_stems(self, urlopen_mock):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = stem_archive()
        urlopen_mock.return_value = response

        result = separate_vocals_in_cloud(
            b"audio",
            ".wav",
            ENDPOINT,
            "token-id",
            "token-secret",
        )

        request = urlopen_mock.call_args.args[0]
        self.assertEqual(request.full_url, f"{ENDPOINT}/split")
        self.assertEqual(request.get_header("Modal-key"), "token-id")
        self.assertEqual(result.vocals, b"vocals")
        self.assertEqual(result.instrumental, b"instrumental")

    @patch("cloud_stem_separation.time.sleep")
    @patch("cloud_stem_separation.urlopen")
    def test_retries_modal_cold_start(self, urlopen_mock, sleep_mock):
        cold_start = HTTPError(ENDPOINT, 503, "starting", {}, io.BytesIO())
        response = MagicMock()
        response.__enter__.return_value.read.return_value = stem_archive()
        urlopen_mock.side_effect = [cold_start, response]

        separate_vocals_in_cloud(
            b"audio",
            ".mp3",
            ENDPOINT,
            "token-id",
            "token-secret",
        )

        self.assertEqual(urlopen_mock.call_count, 2)
        sleep_mock.assert_called_once_with(2)

    def test_rejects_untrusted_endpoint(self):
        with self.assertRaisesRegex(CloudStemSeparationError, "Invalid Modal"):
            separate_vocals_in_cloud(
                b"audio",
                ".wav",
                "https://example.com",
                "token-id",
                "token-secret",
            )


if __name__ == "__main__":
    unittest.main()
