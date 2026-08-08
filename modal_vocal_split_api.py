"""HTTP API executed inside the private Modal Vocal Split container."""

import io
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from modal_vocal_split import ALLOWED_SUFFIXES, MAX_BENCHMARK_BYTES


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def split(request: Request) -> Response:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BENCHMARK_BYTES:
        return JSONResponse({"error": "Audio cannot exceed 50 MB."}, status_code=413)

    suffix = request.headers.get("x-audio-suffix", "").lower()
    if suffix not in ALLOWED_SUFFIXES:
        return JSONResponse({"error": "Unsupported audio format."}, status_code=400)

    audio_data = await request.body()
    if not audio_data or len(audio_data) > MAX_BENCHMARK_BYTES:
        return JSONResponse(
            {"error": "Audio must be between 1 byte and 50 MB."}, status_code=413
        )

    with tempfile.TemporaryDirectory() as temp_directory:
        temporary_path = Path(temp_directory)
        input_path = temporary_path / f"input{suffix}"
        output_directory = temporary_path / "stems"
        input_path.write_bytes(audio_data)

        command = [
            sys.executable,
            "-m",
            "demucs.separate",
            "--two-stems",
            "vocals",
            "--mp3",
            "--mp3-bitrate",
            "320",
            "--device",
            "cuda",
            "--jobs",
            "1",
            "--out",
            str(output_directory),
            str(input_path),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            return JSONResponse({"error": "Vocal separation failed."}, status_code=500)

        vocal_files = list(output_directory.rglob("vocals.mp3"))
        instrumental_files = list(output_directory.rglob("no_vocals.mp3"))
        if len(vocal_files) != 1 or len(instrumental_files) != 1:
            return JSONResponse({"error": "Vocal stems were not created."}, status_code=500)

        archive_buffer = io.BytesIO()
        with zipfile.ZipFile(
            archive_buffer, "w", compression=zipfile.ZIP_STORED
        ) as archive:
            archive.writestr("acapella.mp3", vocal_files[0].read_bytes())
            archive.writestr(
                "instrumental.mp3", instrumental_files[0].read_bytes()
            )

    return Response(archive_buffer.getvalue(), media_type="application/zip")


app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/split", split, methods=["POST"]),
    ]
)
