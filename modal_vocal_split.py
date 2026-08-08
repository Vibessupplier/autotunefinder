"""Modal GPU benchmark for Vocal Split.

This is an infrastructure experiment, not the production upload endpoint.
Run it only with test audio while evaluating Modal.
"""

from pathlib import Path
import tempfile

import modal


APP_NAME = "vibes-supplier-vocal-split-benchmark"
MODEL_NAME = "htdemucs"
ALLOWED_SUFFIXES = {".wav", ".mp3", ".m4a"}
MAX_BENCHMARK_BYTES = 50 * 1024 * 1024


def download_demucs_model() -> None:
    """Bake public Demucs model weights into the private Modal image."""
    from demucs.pretrained import get_model

    get_model(MODEL_NAME)


demucs_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "numpy==1.26.4",
        "torch==2.2.2",
        "torchaudio==2.2.2",
        "demucs==4.0.1",
    )
    .run_function(download_demucs_model)
)

app = modal.App(APP_NAME)


@app.function(
    image=demucs_image,
    gpu="L4",
    timeout=15 * 60,
    scaledown_window=60,
)
def separate_test_audio(audio_data: bytes, suffix: str) -> tuple[bytes, bytes]:
    """Separate test audio on an L4 GPU and return MP3 stem bytes."""
    import subprocess
    import sys

    suffix = suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("Unsupported test audio format.")
    if not audio_data or len(audio_data) > MAX_BENCHMARK_BYTES:
        raise ValueError("Test audio must be between 1 byte and 50 MB.")

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
        subprocess.run(command, check=True)

        vocal_files = list(output_directory.rglob("vocals.mp3"))
        instrumental_files = list(output_directory.rglob("no_vocals.mp3"))
        if len(vocal_files) != 1 or len(instrumental_files) != 1:
            raise RuntimeError("Demucs did not create both expected stems.")

        return vocal_files[0].read_bytes(), instrumental_files[0].read_bytes()


@app.local_entrypoint()
def benchmark(input_path: str, output_directory: str) -> None:
    """Run one explicit test file and save its two benchmark outputs."""
    source = Path(input_path)
    destination = Path(output_directory)
    suffix = source.suffix.lower()

    if not source.is_file():
        raise ValueError(f"Test audio does not exist: {source}")
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("Unsupported test audio format.")
    if source.stat().st_size > MAX_BENCHMARK_BYTES:
        raise ValueError("Test audio cannot exceed 50 MB.")

    vocals, instrumental = separate_test_audio.remote(
        source.read_bytes(), suffix
    )
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "modal-acapella.mp3").write_bytes(vocals)
    (destination / "modal-instrumental.mp3").write_bytes(instrumental)
