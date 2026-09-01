import streamlit as st
import numpy as np
import io
import wave


def run():
    st.title("Noise Generation")

    st.write("This is for generate grey, pink and brown noise.")

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    st.set_page_config(
        page_title="Noise Generator",
        layout="centered"
    )



    # --------------------------------------------------
    # Noise generation
    # --------------------------------------------------

    def normalize_audio(audio):
        """Normalize audio between -1 and 1."""
        max_value = np.max(np.abs(audio))

        if max_value == 0:
            return audio

        return audio / max_value


    def white_noise(duration, sample_rate):
        """Generate white noise."""
        samples = int(duration * sample_rate)

        return np.random.normal(0, 1, samples)


    def pink_noise(duration, sample_rate):
        """Generate pink noise using frequency-domain filtering."""
        samples = int(duration * sample_rate)

        white = np.random.normal(0, 1, samples)

        # FFT
        spectrum = np.fft.rfft(white)

        frequencies = np.fft.rfftfreq(samples, 1 / sample_rate)

        # Avoid division by zero
        frequencies[0] = 1

        # Pink noise: amplitude decreases with sqrt(frequency)
        spectrum /= np.sqrt(frequencies)

        pink = np.fft.irfft(spectrum, n=samples)

        return pink


    def brown_noise(duration, sample_rate):
        """Generate brown noise using cumulative integration."""
        samples = int(duration * sample_rate)

        white = np.random.normal(0, 1, samples)

        brown = np.cumsum(white)

        return brown


    # --------------------------------------------------
    # WAV conversion
    # --------------------------------------------------

    def create_wav(audio, sample_rate):
        """Convert NumPy audio array to WAV bytes."""

        audio = normalize_audio(audio)

        # Convert from float [-1, 1] to 16-bit PCM
        audio_int16 = np.int16(audio * 32767)

        buffer = io.BytesIO()

        with wave.open(buffer, "wb") as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            wav_file.writeframes(audio_int16.tobytes())

        buffer.seek(0)

        return buffer


    # --------------------------------------------------
    # User interface
    # --------------------------------------------------

    noise_type = st.selectbox(
        "Noise type",
        [
            "White noise",
            "Pink noise",
            "Brown noise"
        ]
    )

    duration = st.slider(
        "Generated audio duration (seconds)",
        min_value=5,
        max_value=600,
        value=10,
        step=5
    )

    sample_rate = 44100


    # --------------------------------------------------
    # Generate button
    # --------------------------------------------------

    if st.button("Generate noise", type="primary"):

        with st.spinner("Generating noise..."):

            if noise_type == "White noise":
                audio = white_noise(
                    duration,
                    sample_rate
                )

            elif noise_type == "Pink noise":
                audio = pink_noise(
                    duration,
                    sample_rate
                )

            elif noise_type == "Brown noise":
                audio = brown_noise(
                    duration,
                    sample_rate
                )

            audio = normalize_audio(audio)

            wav_file = create_wav(
                audio,
                sample_rate
            )

            audio_data = wav_file.getvalue()

        st.success(f"{noise_type} generated successfully.")

        # Audio player
        st.audio(
            audio_data,
            format="audio/wav",
            loop=True
        )

        # Download button
        st.download_button(
            label="Download WAV",
            data=audio_data,
            file_name=f"{noise_type.lower().replace(' ', '_')}.wav",
            mime="audio/wav"
        )