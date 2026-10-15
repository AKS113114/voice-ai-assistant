

import io
import os
import subprocess
import tempfile
import time
from pathlib import Path

import requests
import streamlit as st
from faster_whisper import WhisperModel
from dotenv import load_dotenv




PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


MODEL_NAME = "gemma3:4b"
BASE_URL = "http://localhost:11434"


PIPER_EXE = "piper"
VOICE_MODEL = PROJECT_DIR / "voices" / "en_US-lessac-medium.onnx"

WHISPER_MODEL_NAME = "base"




st.set_page_config(
    page_title="Offline Voice AI Assistant",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Offline Voice AI Assistant")
st.caption(
    "Speech recognition + local Gemma LLM + Piper speech synthesis"
)




@st.cache_resource
def load_whisper():
    return WhisperModel(
        WHISPER_MODEL_NAME,
        device="cpu",
        compute_type="int8",
    )


try:
    whisper_model = load_whisper()
except Exception as exc:
    st.error(f"Could not load the Whisper model: {exc}")
    st.stop()




def ask_ollama(user_text, conversation_history):
    """Generate a response using the local Ollama model."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly voice AI assistant. "
                "Give clear, concise answers suitable for speech. "
                "Use previous messages to understand follow-up "
                "questions and references."
            ),
        }
    ]

    messages.extend(conversation_history)

    messages.append({
        "role": "user",
        "content": user_text,
    })

    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()

    answer = response.json()["message"]["content"].strip()

    if not answer:
        raise RuntimeError("The local model returned an empty response.")

    return answer




def generate_speech(text):
    """Convert text to speech using the local Piper voice."""

    if not VOICE_MODEL.exists():
        raise FileNotFoundError(
            f"Piper voice model not found: {VOICE_MODEL}"
        )

    
    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    ) as audio_file:
        output_path = Path(audio_file.name)

    try:
        result = subprocess.run(
            [
                PIPER_EXE,
                "--model",
                str(VOICE_MODEL),
                "--output_file",
                str(output_path),
            ],
            input=text,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Piper failed. Check that Piper is installed and "
                f"available in PATH.\n{result.stderr}"
            )

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("Piper did not generate an audio file.")

        return output_path.read_bytes()

    finally:
       
        try:
            output_path.unlink(missing_ok=True)
        except OSError:
            pass




if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "chat_display" not in st.session_state:
    st.session_state.chat_display = []


with st.sidebar:
    st.subheader("Settings")
    st.write(f"**LLM:** `{MODEL_NAME}`")
    st.write("**STT:** Faster-Whisper base (CPU int8)")
    st.write("**TTS:** Piper Lessac medium")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.chat_display = []
        st.rerun()



for message in st.session_state.chat_display:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("audio"):
            st.audio(message["audio"], format="audio/wav")




st.subheader("Speak to your assistant")
recorded_audio = st.audio_input("Record your message")

if recorded_audio is not None:
    
    audio_bytes = recorded_audio.getvalue()

    if st.session_state.get("last_audio_bytes") != audio_bytes:
        st.session_state.last_audio_bytes = audio_bytes

        audio_buffer = io.BytesIO(audio_bytes)

        total_start = time.perf_counter()

        stt_seconds = 0.0
        llm_seconds = 0.0
        tts_seconds = 0.0

        try:
            with st.spinner("Processing your voice..."):

                
                stt_start = time.perf_counter()

                with tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False,
                ) as input_file:
                    input_file.write(audio_buffer.getvalue())
                    input_path = Path(input_file.name)

                try:
                    segments, info = whisper_model.transcribe(
                        str(input_path)
                    )
                    user_text = " ".join(
                        segment.text for segment in segments
                    ).strip()
                finally:
                    input_path.unlink(missing_ok=True)

                stt_seconds = time.perf_counter() - stt_start

                if not user_text:
                    st.warning(
                        "I couldn't recognize any speech. "
                        "Please try recording again."
                    )
                    st.stop()

                
                st.markdown("### You said")
                st.write(user_text)

                
                llm_start = time.perf_counter()

                answer = ask_ollama(
                    user_text,
                    st.session_state.conversation_history,
                )

                llm_seconds = time.perf_counter() - llm_start

                
                tts_start = time.perf_counter()

                speech_bytes = generate_speech(answer)

                tts_seconds = time.perf_counter() - tts_start

                total_seconds = time.perf_counter() - total_start

            
            st.session_state.conversation_history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": answer},
            ])

            st.session_state.chat_display.extend([
                {"role": "user", "content": user_text},
                {
                    "role": "assistant",
                    "content": answer,
                    "audio": speech_bytes,
                },
            ])

            
            st.markdown("### Assistant")
            st.write(answer)
            st.audio(speech_bytes, format="audio/wav")

           
            st.markdown("### ⏱️ Processing time")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Speech recognition", f"{stt_seconds:.2f} s")
                st.metric("LLM response", f"{llm_seconds:.2f} s")

            with col2:
                st.metric("Speech generation", f"{tts_seconds:.2f} s")
                st.metric("Total processing", f"{total_seconds:.2f} s")

            st.caption(
                "Timings measure local processing after the recording "
                "is submitted. They exclude the time spent recording."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. Make sure Ollama is running "
                "and the local model is available."
            )

        except requests.exceptions.Timeout:
            st.error(
                "Ollama took too long to respond. Try again when the "
                "model is ready."
            )

        except Exception as exc:
            st.error(f"Processing failed: {exc}")

st.divider()
st.caption("Runs speech recognition, LLM inference, and speech synthesis locally.")




