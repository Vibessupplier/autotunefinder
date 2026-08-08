"""Shared Jungle Tech presentation helpers for Streamlit pages."""

import base64
from pathlib import Path

import streamlit as st


def _asset_data_uri(filename: str) -> str:
    """Embed a visual asset so it works consistently on Streamlit Cloud."""
    asset_path = Path(__file__).parent / "static" / filename
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
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
        .vs-inner-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0 0 3.5rem;
            padding-bottom: 0.9rem;
            border-bottom: 1px solid var(--line);
            color: var(--bone);
            font-size: 0.72rem;
            font-weight: 850;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .vs-inner-index {
            color: var(--mango);
            font-size: 0.6rem;
        }

        .vs-inner-brand b {
            color: var(--lime);
            font-weight: 850;
        }

        .vs-inner-system {
            margin-left: auto;
            color: var(--muted);
            font-size: 0.54rem;
            letter-spacing: 0.18em;
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

            .vs-inner-brand {
                margin-bottom: 2.6rem;
            }

            .vs-inner-system {
                display: none;
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
        design.replace(
            "__JUNGLE_BACKGROUND__",
            _asset_data_uri("jungle-tech-background.png"),
        ),
        unsafe_allow_html=True,
    )


def show_header() -> None:
    """Render the compact editorial identity used inside tools."""
    st.markdown(
        """
        <header class="vs-inner-brand">
            <span class="vs-inner-index">09</span>
            <span>VIBES <b>SUPPLIER</b></span>
            <span class="vs-inner-system">Jungle Tech Audio System</span>
        </header>
        """,
        unsafe_allow_html=True,
    )


def show_homepage() -> None:
    """Render the Jungle Tech home hero and tool-family navigation."""
    hero_background = _asset_data_uri("jungle-tech-home-hero.png")
    st.markdown(
        f"""
        <style>
        .block-container {{ max-width: 1120px; }}

        .vs-home-hero {{
            position: relative;
            min-height: 570px;
            overflow: hidden;
            margin-bottom: 4.5rem;
            border: 1px solid var(--line);
            border-radius: 20px 7px 20px 7px;
            background-image:
                linear-gradient(90deg, rgba(8, 17, 13, 0.34), transparent 62%),
                url("{hero_background}");
            background-position: center;
            background-size: cover;
            box-shadow: 0 28px 80px rgba(8, 17, 13, 0.42);
        }}

        .vs-home-copy {{
            position: absolute;
            z-index: 1;
            top: 50%;
            left: clamp(1.6rem, 5vw, 4.5rem);
            width: min(43%, 27rem);
            transform: translateY(-50%);
        }}

        .vs-home-index {{
            margin-bottom: 1.15rem;
            color: var(--mango);
            font-size: 0.7rem;
            font-weight: 850;
            letter-spacing: 0.18em;
        }}

        .vs-home-vibes {{
            margin: 0;
            color: var(--bone);
            font-family: Impact, Haettenschweiler, "Arial Narrow Bold", sans-serif;
            font-size: clamp(5.2rem, 11vw, 8.8rem);
            font-weight: 900;
            letter-spacing: 0.01em;
            line-height: 0.78;
            text-transform: uppercase;
            text-shadow: 0 8px 28px rgba(8, 17, 13, 0.50);
        }}

        .vs-home-supplier {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-top: 1.45rem;
            color: var(--lime);
            font-size: clamp(0.78rem, 1.8vw, 1.1rem);
            font-weight: 850;
            letter-spacing: 0.36em;
            text-transform: uppercase;
        }}

        .vs-home-supplier::before,
        .vs-home-supplier::after {{
            content: "";
            height: 1px;
            flex: 1;
            background: var(--lime);
            box-shadow: 0 0 8px rgba(184, 255, 61, 0.28);
        }}

        .vs-home-tagline {{
            margin-top: 1.25rem;
            color: var(--sand);
            font-size: 0.72rem;
            font-weight: 720;
            letter-spacing: 0.14em;
            line-height: 1.7;
            text-transform: uppercase;
        }}

        .vs-home-section {{ margin-bottom: 1.5rem; }}
        .vs-home-section h2 {{
            max-width: 38rem;
            margin: 0.55rem 0 0 !important;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.04;
        }}

        .vs-tool-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
        }}

        .vs-home-card {{
            display: flex;
            min-height: 245px;
            flex-direction: column;
            padding: 1.35rem;
            border: 1px solid var(--line);
            border-radius: 15px 6px 15px 6px;
            background:
                linear-gradient(145deg, rgba(31, 107, 69, 0.18), transparent 60%),
                rgba(16, 39, 27, 0.84);
            color: var(--bone) !important;
            text-decoration: none !important;
            backdrop-filter: blur(16px);
            transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
        }}

        .vs-home-card:hover {{
            border-color: rgba(184, 255, 61, 0.56);
            background:
                linear-gradient(145deg, rgba(31, 107, 69, 0.34), transparent 68%),
                rgba(16, 39, 27, 0.92);
            transform: translateY(-3px);
        }}

        .vs-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--lime);
            font-size: 0.62rem;
            font-weight: 850;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}

        .vs-card-status {{
            padding: 0.25rem 0.45rem;
            border: 1px solid rgba(184, 255, 61, 0.34);
            border-radius: 999px;
        }}

        .vs-card-status.soon {{
            border-color: rgba(216, 195, 154, 0.24);
            color: var(--muted);
        }}

        .vs-home-card h3 {{
            margin: auto 0 0.7rem !important;
            font-size: 1.55rem;
        }}

        .vs-home-card p {{
            min-height: 3.2rem;
            margin: 0;
            color: var(--sand);
            font-size: 0.85rem;
            line-height: 1.55;
        }}

        .vs-card-enter {{
            margin-top: 1.2rem;
            color: var(--lime);
            font-size: 0.66rem;
            font-weight: 850;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }}

        @media (max-width: 760px) {{
            .vs-home-hero {{ min-height: 620px; background-position: 64% center; }}
            .vs-home-hero::after {{
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(0deg, rgba(8, 17, 13, 0.94) 0 38%, transparent 74%);
            }}
            .vs-home-copy {{
                top: auto;
                right: 1.4rem;
                bottom: 2.1rem;
                left: 1.4rem;
                width: auto;
                transform: none;
            }}
            .vs-home-vibes {{ font-size: clamp(4.4rem, 23vw, 6.6rem); }}
            .vs-tool-grid {{ grid-template-columns: 1fr; }}
            .vs-home-card {{ min-height: 205px; }}
        }}
        </style>

        <section class="vs-home-hero">
            <div class="vs-home-copy">
                <div class="vs-home-index">09 / AUDIO SYSTEM</div>
                <div class="vs-home-vibes">VIBES</div>
                <div class="vs-home-supplier">SUPPLIER</div>
                <div class="vs-home-tagline">
                    Independent audio tools<br>
                    for producers, DJs &amp; artists
                </div>
            </div>
        </section>

        <section class="vs-home-section">
            <div class="vs-family">Enter the system</div>
            <h2>Three ways into the sound.</h2>
        </section>

        <nav class="vs-tool-grid" aria-label="Audio tool families">
            <a class="vs-home-card" href="/key-bpm-finder" target="_self">
                <div class="vs-card-top"><span>Analyze / 01</span><span class="vs-card-status">Live</span></div>
                <h3>Read the signal.</h3>
                <p>Find key, BPM and Camelot position before you mix, DJ or create.</p>
                <span class="vs-card-enter">Open Key &amp; BPM →</span>
            </a>
            <a class="vs-home-card" href="/speed-changer" target="_self">
                <div class="vs-card-top"><span>Transform / 02</span><span class="vs-card-status">Live</span></div>
                <h3>Reshape the motion.</h3>
                <p>Set exact tempo and control the relationship between speed and pitch.</p>
                <span class="vs-card-enter">Open Speed Changer →</span>
            </a>
            <a class="vs-home-card" href="/vocal-split" target="_self">
                <div class="vs-card-top"><span>Separate / 03</span><span class="vs-card-status soon">Soon</span></div>
                <h3>Pull voice from rhythm.</h3>
                <p>High-quality acapella and instrumental separation is being prepared.</p>
                <span class="vs-card-enter">Preview the tool →</span>
            </a>
        </nav>
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
