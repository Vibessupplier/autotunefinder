import streamlit as st


st.set_page_config(
    page_title="Vibes Supplier",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page(
        "pages/1_Key_BPM_Finder.py",
        title="Key & BPM Finder",
        icon="🎵",
        default=True,
    ),
    st.Page(
        "pages/2_Speed_Changer.py",
        title="Speed Changer",
        icon="⚡",
        url_path="speed-changer",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
