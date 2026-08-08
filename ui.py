"""Shared Jungle Tech presentation helpers for Streamlit pages."""

import base64
from pathlib import Path

import streamlit as st


def _jungle_background_data_uri() -> str:
    """Embed the background so it works consistently on Streamlit Cloud."""
    background_path = (
        Path(__file__).parent / "static" / "jungle-tech-background.png"
    )
    encoded = base64.b64encode(background_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def load_design() -> None:
    """Load the shared Jungle Tech visual system."""
    design = """
        <style>
        :root {
            --jungle-black: #08110d;
            --deep-forest: #10271b;
            --tropical-green: #1f6b45;
            --sand: #d8c39a;
            --bone: #f1e9d5;
            --lime: #b8ff3d;
            --mango: #ffb23f;
            --muted: rgba(216, 195, 154, 0.68);
            --line: rgba(216, 195, 154, 0.16);
        }

        html, body, [class*="css"] {
            color: var(--bone);
        }

        .stApp {
            background-color: var(--jungle-black);
            background-image:
                linear-gradient(rgba(8, 17, 13, 0.16), rgba(8, 17, 13, 0.42)),
                radial-gradient(circle at 50% 32%, transparent 0 18rem, rgba(8, 17, 13, 0.12) 44rem),
                url("__JUNGLE_BACKGROUND__");
            background-position: center top;
            background-repeat: no-repeat;
            background-size: cover;
            background-attachment: fixed;
            color: var(--bone);
        }

        .stApp::before,
        .stApp::after {
            display: none;
        }

        [data-testid="stAppViewContainer"] > .main {
            position: relative;
            z-index: 1;
        }

        .block-container {
            max-width: 960px;
            padding-top: 2.4rem;
            padding-bottom: 5rem;
        }

        /* Brand */
        .neon-title {
            margin: 0 0 0.55rem;
            color: #ffffff;
            font-size: clamp(3rem, 8vw, 4rem);
            font-weight: 900;
            letter-spacing: 0.05em;
            line-height: 1;
            text-align: center;
            text-shadow:
                0 0 5px #00ffff,
                0 0 10px #00ffff,
                0 0 20px #00ffff,
                0 0 36px rgba(0, 255, 255, 0.62);
        }

        .subtitle {
            margin: 0 0 3.8rem;
            color: var(--sand);
            font-size: 0.92rem;
            letter-spacing: 0.035em;
            text-align: center;
        }

        /* Tool identity */
        .vs-tool-header {
            margin-bottom: 2rem;
        }

        .vs-family {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.65rem;
            color: var(--lime);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.22em;
            text-transform: uppercase;
        }

        .vs-family::before {
            content: "";
            width: 1.6rem;
            height: 1px;
            background: currentColor;
            box-shadow: 0 0 8px rgba(184, 255, 61, 0.42);
        }

        .vs-tool-title {
            margin: 0;
            color: var(--bone);
            font-size: clamp(2.25rem, 6vw, 4.25rem);
            font-weight: 820;
            line-height: 0.98;
            letter-spacing: -0.045em;
        }

        .vs-tool-description {
            max-width: 39rem;
            margin: 0.85rem 0 0;
            color: var(--sand);
            font-size: 1.02rem;
            line-height: 1.65;
        }

        /* Typography */
        h1, h2, h3, h4 {
            color: var(--bone) !important;
            letter-spacing: -0.025em;
        }

        h2, h3 {
            margin-top: 2rem !important;
        }

        p, label, [data-testid="stCaptionContainer"] {
            color: var(--sand);
        }

        [data-testid="stCaptionContainer"] {
            opacity: 0.76;
        }

        hr {
            border-color: var(--line) !important;
        }

        /* Sidebar / taxonomy */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(rgba(8, 17, 13, 0.91), rgba(8, 17, 13, 0.97)),
                url("/app/static/jungle-tech-background.png") left top / auto 100% fixed,
                var(--jungle-black);
            border-right: 1px solid var(--line);
            box-shadow: 12px 0 40px rgba(8, 17, 13, 0.28);
        }

        [data-testid="stSidebar"]::before {
            content: "VS / AUDIO SYSTEM";
            display: block;
            margin: 1.5rem 1.25rem 0.8rem;
            color: var(--sand);
            font-size: 0.66rem;
            font-weight: 800;
            letter-spacing: 0.2em;
        }

        [data-testid="stSidebarNavSeparator"] {
            border-color: var(--line);
        }

        [data-testid="stSidebar"] [data-testid="stNavSectionHeader"] {
            color: rgba(216, 195, 154, 0.58);
            font-size: 0.63rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            margin-top: 0.65rem;
        }

        [data-testid="stSidebar"] a {
            border: 1px solid transparent;
            border-radius: 9px 4px 9px 4px;
            color: var(--sand);
            transition: background 140ms ease, border-color 140ms ease;
        }

        [data-testid="stSidebar"] a:hover {
            background: rgba(31, 107, 69, 0.16);
            border-color: rgba(216, 195, 154, 0.08);
        }

        [data-testid="stSidebar"] a[aria-current="page"] {
            background: rgba(31, 107, 69, 0.24);
            border-color: rgba(184, 255, 61, 0.24);
            color: var(--bone);
            box-shadow: inset 3px 0 0 var(--lime);
        }

        /* Input surfaces */
        [data-testid="stFileUploader"] {
            padding: 0.7rem;
            border: 1px solid var(--line);
            border-radius: 16px 7px 16px 7px;
            background:
                linear-gradient(135deg, rgba(31, 107, 69, 0.12), transparent 55%),
                rgba(16, 39, 27, 0.72);
            backdrop-filter: blur(16px);
        }

        [data-testid="stFileUploaderDropzone"] {
            min-height: 8.5rem;
            border: 1px dashed rgba(216, 195, 154, 0.34);
            border-radius: 12px 5px 12px 5px;
            background: rgba(8, 17, 13, 0.48);
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: rgba(184, 255, 61, 0.66);
            background: rgba(31, 107, 69, 0.12);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-testid="stNumberInputContainer"] > div {
            border: 1px solid var(--line) !important;
            background: rgba(16, 39, 27, 0.82) !important;
            border-radius: 11px 5px 11px 5px !important;
            box-shadow: inset 0 1px 0 rgba(241, 233, 213, 0.03);
        }

        [data-baseweb="input"] > div:focus-within,
        [data-testid="stNumberInputContainer"] > div:focus-within {
            border-color: rgba(184, 255, 61, 0.72) !important;
            box-shadow: 0 0 0 2px rgba(184, 255, 61, 0.10);
        }

        [data-testid="stNumberInput"] input {
            color: var(--bone) !important;
            font-weight: 720;
        }

        [data-testid="stNumberInput"] button {
            color: var(--lime) !important;
        }

        [data-testid="stWidgetLabel"] p {
            color: var(--bone);
            font-size: 0.75rem;
            font-weight: 720;
            letter-spacing: 0.045em;
        }

        [data-testid="stTooltipIcon"] {
            color: var(--lime) !important;
            opacity: 1 !important;
            filter: drop-shadow(0 0 5px rgba(184, 255, 61, 0.28));
        }

        [data-testid="stTooltipIcon"] svg {
            width: 1.08rem !important;
            height: 1.08rem !important;
            color: var(--lime) !important;
            fill: transparent !important;
            stroke: currentColor !important;
            stroke-width: 2.2px;
        }

        [data-testid="stRadio"] [role="radiogroup"] {
            gap: 0.55rem;
        }

        [data-testid="stRadio"] label {
            min-height: 2.65rem;
            margin: 0;
            padding: 0.58rem 0.78rem;
            border: 1px solid var(--line);
            border-radius: 9px 4px 9px 4px;
            background: rgba(16, 39, 27, 0.74);
            transition: border-color 140ms ease, background 140ms ease;
        }

        [data-testid="stRadio"] label:hover {
            border-color: rgba(184, 255, 61, 0.45);
            background: rgba(31, 107, 69, 0.28);
        }

        [data-testid="stRadio"] label:has(input:checked) {
            border-color: var(--lime);
            background: rgba(31, 107, 69, 0.40);
            box-shadow: inset 3px 0 0 var(--lime);
        }

        [data-baseweb="radio"] > div {
            background-color: var(--lime) !important;
        }

        [data-testid="stSlider"] {
            margin: 0.25rem 0 0.85rem;
            padding: 0.75rem 0.95rem 0.95rem;
            border: 1px solid var(--line);
            border-radius: 12px 5px 12px 5px;
            background:
                linear-gradient(90deg, rgba(31, 107, 69, 0.20), transparent 60%),
                rgba(16, 39, 27, 0.68);
            backdrop-filter: blur(14px);
        }

        [data-testid="stSlider"] [data-baseweb="slider"] > div {
            height: 4px;
            border-radius: 0;
        }

        [data-testid="stSlider"] [role="slider"] {
            width: 16px !important;
            height: 16px !important;
            border: 3px solid var(--jungle-black) !important;
            border-radius: 4px !important;
            background: var(--lime) !important;
            box-shadow: 0 0 12px rgba(184, 255, 61, 0.28);
            transform: rotate(45deg);
        }

        /* Actions */
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button {
            min-height: 3.25rem;
            border: 1px solid var(--lime);
            border-radius: 10px 4px 10px 4px;
            font-size: 0.82rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            transition: transform 150ms ease, box-shadow 150ms ease, background 150ms ease;
        }

        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stDownloadButton"] button {
            background: var(--lime);
            color: var(--jungle-black);
            box-shadow: 0 6px 22px rgba(184, 255, 61, 0.10);
        }

        [data-testid="stButton"] button[kind="secondary"] {
            background: rgba(16, 39, 27, 0.84);
            color: var(--lime);
            box-shadow: inset 0 1px 0 rgba(241, 233, 213, 0.04);
        }

        [data-testid="stButton"] button p,
        [data-testid="stDownloadButton"] button p {
            color: inherit !important;
            font-weight: inherit !important;
        }

        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {
            border-color: var(--bone);
            transform: translateY(-1px);
            box-shadow: 0 8px 26px rgba(184, 255, 61, 0.18);
        }

        [data-testid="stButton"] button:focus:not(:active),
        [data-testid="stDownloadButton"] button:focus:not(:active) {
            border-color: var(--bone);
            box-shadow: 0 0 0 3px rgba(184, 255, 61, 0.28);
        }

        /* Results, players and states */
        [data-testid="stMetric"] {
            min-height: 8.3rem;
            padding: 1.25rem;
            border: 1px solid var(--line);
            border-radius: 15px 6px 15px 6px;
            background:
                linear-gradient(145deg, rgba(31, 107, 69, 0.18), transparent 70%),
                rgba(16, 39, 27, 0.78);
            backdrop-filter: blur(16px);
        }

        [data-testid="stMetricLabel"] {
            color: var(--sand);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.15em;
        }

        [data-testid="stMetricValue"] {
            color: var(--lime);
            font-weight: 780;
            text-shadow: 0 0 16px rgba(184, 255, 61, 0.14);
        }

        [data-testid="stAudio"] {
            padding: 0.55rem;
            border: 1px solid var(--line);
            border-radius: 12px 5px 12px 5px;
            background: rgba(16, 39, 27, 0.78);
            backdrop-filter: blur(16px);
        }

        [data-testid="stAlert"] {
            border: 1px solid rgba(216, 195, 154, 0.18);
            border-radius: 12px 5px 12px 5px;
            background: rgba(16, 39, 27, 0.76);
            color: var(--bone);
        }

        [data-baseweb="notification"] {
            border-color: rgba(216, 195, 154, 0.18) !important;
            background: rgba(16, 39, 27, 0.88) !important;
            color: var(--bone) !important;
        }

        [data-testid="stAlert"] svg {
            color: var(--lime);
        }

        [data-testid="stSpinner"] > div {
            border-top-color: var(--lime) !important;
        }

        code, pre {
            border-color: var(--line) !important;
            background: var(--jungle-black) !important;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-top: 1.5rem;
                padding-left: 1.15rem;
                padding-right: 1.15rem;
            }

            .neon-title {
                font-size: clamp(2.25rem, 12vw, 3.2rem);
            }

            .subtitle {
                margin-bottom: 3rem;
            }

            [data-testid="stMetric"] {
                min-height: auto;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                transition: none !important;
            }
        }
        </style>
        """
    st.markdown(
        design.replace("__JUNGLE_BACKGROUND__", _jungle_background_data_uri()),
        unsafe_allow_html=True,
    )


def show_header() -> None:
    """Render the provisional original Vibes Supplier header."""
    st.markdown(
        """
        <div class="neon-title">VIBES SUPPLIER</div>
        <div class="subtitle">
            Professional audio tools for producers, DJs and artists.
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_tool_header(family: str, title: str, description: str) -> None:
    """Render a consistent family label and tool introduction."""
    st.markdown(
        f"""
        <section class="vs-tool-header">
            <div class="vs-family">{family}</div>
            <h1 class="vs-tool-title">{title}</h1>
            <p class="vs-tool-description">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
