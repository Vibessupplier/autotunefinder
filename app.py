import streamlit as st

st.set_page_config(
    page_title="AutoTune Finder",
    page_icon="🎵"
)

st.title("🎵 AutoTune Finder")

st.write(
    "Puja una vocal i t'ajudaré a estimar la tonalitat "
    "per configurar l'Auto-Tune."
)

audio_file = st.file_uploader(
    "Puja un fitxer d'àudio",
    type=["wav", "mp3", "m4a"]
)

if audio_file is not None:
    st.audio(audio_file)

    st.success("Fitxer carregat correctament.")

    st.write("En el següent pas afegirem l'anàlisi de tonalitat.")
