"""Private HTTP client for the Modal Vocal Split server."""

from dataclasses import dataclass
import io
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile


ALLOWED_SUFFIXES = {".wav", ".mp3", ".m4a"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_RESPONSE_BYTES = 100 * 1024 * 1024


class CloudStemSeparationError(RuntimeError):
    """Raised when the private cloud separator cannot complete a request."""


@dataclass(frozen=True)
class CloudVocalSplitResult:
    vocals: bytes
    instrumental: bytes


def _validate_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith((".modal.direct", ".modal.run"))
    ):
        raise CloudStemSeparationError("Invalid Modal endpoint configuration.")
    return endpoint.rstrip("/")


def separate_vocals_in_cloud(
    audio_data: bytes,
    suffix: str,
    endpoint: str,
    token_id: str,
    token_secret: str,
    cold_start_retries: int = 30,
) -> CloudVocalSplitResult:
    """Send temporary audio to the private zero-retention Modal server."""
    suffix = suffix.lower()
    endpoint = _validate_endpoint(endpoint)
    if suffix not in ALLOWED_SUFFIXES:
        raise CloudStemSeparationError("Unsupported audio format.")
    if not audio_data or len(audio_data) > MAX_UPLOAD_BYTES:
        raise CloudStemSeparationError(
            "Audio must be between 1 byte and 50 MB."
        )
    if not token_id or not token_secret:
        raise CloudStemSeparationError("Modal authentication is not configured.")

    request = Request(
        f"{endpoint}/split",
        data=audio_data,
        method="POST",
        headers={
            "Content-Type": "application/octet-stream",
            "X-Audio-Suffix": suffix,
            "Modal-Key": token_id,
            "Modal-Secret": token_secret,
        },
    )

    for attempt in range(cold_start_retries + 1):
        try:
            with urlopen(request, timeout=5 * 60) as response:
                archive_data = response.read(MAX_RESPONSE_BYTES + 1)
            break
        except HTTPError as error:
            if error.code == 503 and attempt < cold_start_retries:
                time.sleep(2)
                continue
            try:
                details = json.loads(error.read().decode("utf-8")).get("error")
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                details = None
            raise CloudStemSeparationError(
                details or f"Modal returned HTTP {error.code}."
            ) from error
        except URLError as error:
            if attempt < cold_start_retries:
                time.sleep(2)
                continue
            raise CloudStemSeparationError(
                "The Vocal Split service could not be reached."
            ) from error
    else:
        raise CloudStemSeparationError("The Vocal Split service did not start.")

    if len(archive_data) > MAX_RESPONSE_BYTES:
        raise CloudStemSeparationError("Modal returned an oversized response.")

    try:
        with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
            if set(archive.namelist()) != {
                "acapella.mp3",
                "instrumental.mp3",
            }:
                raise CloudStemSeparationError(
                    "Modal returned unexpected stem files."
                )
            vocals = archive.read("acapella.mp3")
            instrumental = archive.read("instrumental.mp3")
    except zipfile.BadZipFile as error:
        raise CloudStemSeparationError(
            "Modal returned an invalid stem archive."
        ) from error

    if not vocals or not instrumental:
        raise CloudStemSeparationError("Modal returned empty stem audio.")

    return CloudVocalSplitResult(vocals=vocals, instrumental=instrumental)
