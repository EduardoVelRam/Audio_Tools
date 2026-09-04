import streamlit as st
import whisper
import tempfile
import os


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Subtitle Generator",
    layout="centered"
)

st.title("Subtitle Generator")
st.write("Generate subtitles from audio or video using Whisper.")


# --------------------------------------------------
# Load Whisper model
# --------------------------------------------------

@st.cache_resource
def load_model():
    return whisper.load_model("base")


# --------------------------------------------------
# Convert seconds to SRT timestamp
# --------------------------------------------------

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds_int:02d},"
        f"{milliseconds:03d}"
    )


# --------------------------------------------------
# Generate SRT
# --------------------------------------------------

def generate_srt(segments):

    srt = ""

    for index, segment in enumerate(segments, start=1):

        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])

        text = segment["text"].strip()

        srt += f"{index}\n"
        srt += f"{start} --> {end}\n"
        srt += f"{text}\n\n"

    return srt


# --------------------------------------------------
# User interface
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload an audio or video file",
    type=[
        "mp3",
        "wav",
        "m4a",
        "mp4",
        "mpeg",
        "mpga",
        "webm"
    ]
)

language = st.selectbox(
    "Language",
    [
        "Auto detect",
        "Spanish",
        "English",
        "French",
        "German",
        "Italian",
        "Portuguese"
    ]
)


# --------------------------------------------------
# Generate subtitles
# --------------------------------------------------

if uploaded_file is not None:

    st.audio(
        uploaded_file
    )

    if st.button(
        "Generate subtitles",
        type="primary"
    ):

        # Save uploaded file temporarily
        suffix = os.path.splitext(
            uploaded_file.name
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(
                uploaded_file.read()
            )

            input_file = temp_file.name

        try:

            with st.spinner(
                "Transcribing audio..."
            ):

                model = load_model()

                # Whisper language parameter
                if language == "Auto detect":
                    result = model.transcribe(
                        input_file
                    )
                else:

                    language_codes = {
                        "Spanish": "es",
                        "English": "en",
                        "French": "fr",
                        "German": "de",
                        "Italian": "it",
                        "Portuguese": "pt"
                    }

                    result = model.transcribe(
                        input_file,
                        language=language_codes[language]
                    )

            # Generate SRT
            srt_content = generate_srt(
                result["segments"]
            )

            st.success(
                "Subtitles generated successfully."
            )

            # Show transcription
            st.subheader("Transcription")

            st.text_area(
                "Text",
                result["text"],
                height=200
            )

            # Show SRT
            st.subheader("SRT")

            st.code(
                srt_content,
                language="text"
            )

            # Download SRT
            st.download_button(
                label="Download SRT",
                data=srt_content,
                file_name="subtitles.srt",
                mime="text/plain"
            )

        except Exception as e:

            st.error(
                f"Error generating subtitles: {e}"
            )

        finally:

            if os.path.exists(input_file):
                os.remove(input_file)