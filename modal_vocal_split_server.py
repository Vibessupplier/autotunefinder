"""Private, zero-retention Modal web app for Vocal Split processing."""

import modal

from modal_vocal_split import demucs_image


APP_NAME = "vibes-supplier-vocal-split"

server_image = demucs_image.pip_install(
    "starlette==0.47.3",
).add_local_file(
    "modal_vocal_split_api.py",
    remote_path="/root/modal_vocal_split_api.py",
)

app = modal.App(APP_NAME)


@app.function(
    image=server_image,
    gpu="L4",
    max_containers=1,
    scaledown_window=60,
    timeout=10 * 60,
)
@modal.asgi_app(requires_proxy_auth=True)
def vocal_split_api():
    from modal_vocal_split_api import app as web_app

    return web_app
