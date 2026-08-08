"""Privacy-conscious product analytics for the Streamlit application."""

import hashlib
import json
import threading
from typing import Any
from urllib import request
import uuid

import streamlit as st


def _configuration() -> tuple[str, str] | None:
    try:
        settings = st.secrets.get("analytics", {})
        if not settings.get("enabled", False):
            return None
        api_key = str(settings.get("posthog_api_key", "")).strip()
        host = str(settings.get("posthog_host", "")).strip().rstrip("/")
    except (FileNotFoundError, KeyError, TypeError):
        return None

    if not api_key.startswith("phc_") or not host.startswith("https://"):
        return None
    return api_key, host


def _distinct_id(api_key: str) -> str:
    """Return a pseudonymous browser ID without sending the source cookie."""
    try:
        browser_cookie = st.context.cookies.get("_streamlit_xsrf", "")
    except (AttributeError, RuntimeError):
        browser_cookie = ""

    if browser_cookie:
        digest = hashlib.sha256(
            f"{api_key}:{browser_cookie}".encode("utf-8")
        ).hexdigest()
        return f"browser_{digest[:32]}"

    if "analytics_session_id" not in st.session_state:
        st.session_state["analytics_session_id"] = f"session_{uuid.uuid4().hex}"
    return st.session_state["analytics_session_id"]


def _post_event(url: str, payload: dict[str, Any]) -> None:
    try:
        body = json.dumps(payload).encode("utf-8")
        event_request = request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(event_request, timeout=3):
            pass
    except Exception:
        # Analytics must never break or delay an audio tool.
        return


def track_event(
    event: str,
    properties: dict[str, Any] | None = None,
    *,
    once_key: str | None = None,
) -> None:
    """Send an anonymous event when analytics is configured and enabled."""
    configuration = _configuration()
    if configuration is None:
        return

    if once_key is not None:
        state_key = f"analytics_once_{once_key}"
        if st.session_state.get(state_key):
            return
        st.session_state[state_key] = True

    api_key, host = configuration
    safe_properties = dict(properties or {})
    safe_properties.update(
        {
            "distinct_id": _distinct_id(api_key),
            "$geoip_disable": True,
            "analytics_source": "streamlit_server",
        }
    )
    payload = {
        "api_key": api_key,
        "event": event,
        "properties": safe_properties,
    }
    threading.Thread(
        target=_post_event,
        args=(f"{host}/capture/", payload),
        daemon=True,
    ).start()


def track_page_view(page: str) -> None:
    """Capture one page view per page and Streamlit session."""
    track_event(
        "$pageview",
        {"page": page, "$current_url": page},
        once_key=f"page_{page}",
    )
