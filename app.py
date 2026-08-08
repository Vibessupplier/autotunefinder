import streamlit as st


st.set_page_config(
    page_title="Vibes Supplier",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

pages = {
    "HOME": [
        st.Page(
            "pages/0_Home.py",
            title="Vibes Supplier",
            default=True,
        ),
    ],
    "ANALYZE": [
        st.Page(
            "pages/1_Key_BPM_Finder.py",
            title="Key & BPM Finder",
            url_path="key-bpm-finder",
        ),
        st.Page(
            "pages/4_Mastering_Analyzer.py",
            title="Mastering Analyzer",
            url_path="mastering-analyzer",
        ),
    ],
    "TRANSFORM": [
        st.Page(
            "pages/2_Speed_Changer.py",
            title="Speed Changer",
            url_path="speed-changer",
        ),
    ],
    "SEPARATE": [
        st.Page(
            "pages/3_Vocal_Split.py",
            title="Vocal Split · Soon",
            url_path="vocal-split",
        ),
    ],
}

navigation = st.navigation(pages, position="sidebar")
navigation.run()
