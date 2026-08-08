"""Shared Jungle Tech presentation helpers for Streamlit pages."""

import streamlit as st


def load_design() -> None:
    """Load the shared Jungle Tech visual system."""
    st.markdown(
        """
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
                linear-gradient(rgba(8, 17, 13, 0.52), rgba(8, 17, 13, 0.72)),
                radial-gradient(circle at 50% 32%, transparent 0 16rem, rgba(8, 17, 13, 0.24) 42rem),
                url("/app/static/jungle-tech-background.png");
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
            border-color: var(--line) !important;
            background: rgba(16, 39, 27, 0.56) !important;
            border-radius: 7px !important;
        }

        [data-testid="stWidgetLabel"] p {
            color: var(--bone);
            font-size: 0.75rem;
            font-weight: 720;
            letter-spacing: 0.045em;
        }

        [data-baseweb="radio"] > div {
            background-color: var(--lime) !important;
        }

        [data-testid="stSlider"] [role="slider"] {
            border-color: var(--lime) !important;
            background: var(--lime) !important;
            box-shadow: 0 0 12px rgba(184, 255, 61, 0.28);
        }

        /* Actions */
        div.stButton > button,
        div.stDownloadButton > button {
            min-height: 3.25rem;
            width: 100%;
            border: 1px solid var(--lime);
            border-radius: 7px;
            background: var(--lime);
            color: var(--jungle-black);
            font-size: 0.82rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            box-shadow: 0 6px 22px rgba(184, 255, 61, 0.08);
            transition: transform 150ms ease, box-shadow 150ms ease, background 150ms ease;
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover {
            border-color: var(--bone);
            background: var(--lime);
            color: var(--jungle-black);
            transform: translateY(-1px);
            box-shadow: 0 8px 26px rgba(184, 255, 61, 0.18);
        }

        div.stButton > button:focus:not(:active),
        div.stDownloadButton > button:focus:not(:active) {
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
        """,
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
