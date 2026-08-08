import streamlit as st


st.set_page_config(
    page_title="Vibes Supplier",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

pages = {
    "ANALYZE": [
        st.Page(
            "pages/1_Key_BPM_Finder.py",
            title="Key & BPM Finder",
            default=True,
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
