import asyncio
import os
import tempfile

import edge_tts
import streamlit as st


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Text-to-Speech",
    page_icon="🔊",
    layout="centered"
)

st.title("Text-to-Speech")
st.write("Convert text into speech using Microsoft Edge voices.")


# --------------------------------------------------
# Available voices
# --------------------------------------------------

VOICES = {
    "English - US - Jenny": "en-US-JennyNeural",
    "English - US - Guy": "en-US-GuyNeural",
    "English - UK - Sonia": "en-GB-SoniaNeural",
    "Spanish - Mexico - Dalia": "es-MX-DaliaNeural",
    "Spanish - Mexico - Jorge": "es-MX-JorgeNeural",
    "Spanish - Spain - Elvira": "es-ES-ElviraNeural",
    "French - France - Denise": "fr-FR-DeniseNeural",
    "German - Germany - Katja": "de-DE-KatjaNeural",
    "Italian - Italy - Elsa": "it-IT-ElsaNeural",
    "Portuguese - Brazil - Francisca": "pt-BR-FranciscaNeural",
}


# --------------------------------------------------
# TTS function
# --------------------------------------------------

async def generate_audio(text, voice, rate, pitch, output_file):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )

    await communicate.save(output_file)


# --------------------------------------------------
# User interface
# --------------------------------------------------

text = st.text_area(
    "Text",
    placeholder="Write the text you want to convert to speech...",
    height=200
)

voice_name = st.selectbox(
    "Voice",
    list(VOICES.keys())
)

col1, col2 = st.columns(2)

with col1:
    rate = st.slider(
        "Speech speed",
        min_value=-50,
        max_value=50,
        value=0,
        step=5
    )

with col2:
    pitch = st.slider(
        "Pitch",
        min_value=-50,
        max_value=50,
        value=0,
        step=5
    )

loop_audio = st.checkbox("Reproducir en bucle")

# Convert slider values to Edge TTS format

rate_string = f"{rate:+d}%"
pitch_string = f"{pitch:+d}Hz"


# --------------------------------------------------
# Generate audio
# --------------------------------------------------

if st.button("Generate audio", type="primary"):

    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    selected_voice = VOICES[voice_name]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as temp_file:

        output_file = temp_file.name

    try:

        with st.spinner("Generating audio..."):

            asyncio.run(
                generate_audio(
                    text,
                    selected_voice,
                    rate_string,
                    pitch_string,
                    output_file
                )
            )

        st.success("Audio generated successfully.")

        # Audio player
        with open(output_file, "rb") as audio_file:
            audio_data = audio_file.read()

        st.audio(
            audio_data,
            format="audio/mp3",
            loop=loop_audio
        )

        # Download button
        st.download_button(
            label="Download MP3",
            data=audio_data,
            file_name="generated_audio.mp3",
            mime="audio/mpeg"
        )

    except Exception as e:
        st.error(f"Error generating audio: {e}")

    finally:

        if os.path.exists(output_file):
            os.remove(output_file)