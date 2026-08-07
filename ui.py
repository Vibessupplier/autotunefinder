import streamlit as st


def load_design():

    st.markdown("""
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top,
                #151515 0%,
                #090909 55%,
                #000000 100%
            );

        color: white;
    }

    .block-container {
        max-width: 900px;
        padding-top: 3rem;
    }

    .neon-title {
        text-align: center;
        font-size: 64px;
        font-weight: 900;
        letter-spacing: 3px;

        color: #ffffff;

        text-shadow:
            0 0 5px #00ffff,
            0 0 10px #00ffff,
            0 0 20px #00ffff,
            0 0 40px #00ffff;

        margin-bottom: 10px;
    }

    .subtitle {
        text-align: center;
        color: #bdbdbd;
        font-size: 18px;
        margin-bottom: 40px;
    }

    div.stButton > button {
        width: 100%;
        height: 3.5rem;

        border-radius: 12px;

        font-weight: 700;
        font-size: 17px;

        border: 1px solid #00ffff;

        background-color: #090909;
        color: white;

        box-shadow:
            0 0 12px
            rgba(0,255,255,0.3);
    }

    div.stButton > button:hover {
        border-color: #00ffff;
        color: #00ffff;

        box-shadow:
            0 0 20px
            rgba(0,255,255,0.6);
    }

    </style>
    """, unsafe_allow_html=True)


def show_header():

    st.markdown(
        '<div class="neon-title">'
        'VIBES SUPPLIER'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Professional audio tools for producers, DJs and artists.'
        '</div>',
        unsafe_allow_html=True
    )
