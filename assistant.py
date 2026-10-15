
import os
import sys
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv
from faster_whisper import WhisperModel


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma4:31b:cloud")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://ollama.com").rstrip("/")


AUDIO_FILE = PROJECT_DIR / "sample.m4a"
VOICE_MODEL = PROJECT_DIR / "voices" / "en_US-lessac-medium.onnx"
OUTPUT_AUDIO = PROJECT_DIR / "response.wav"


def transcribe_audio(audio_path):
    """Convert the recorded audio into text."""
    print("\n[1/3] Transcribing your audio...")

    model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(str(audio_path))
    text = " ".join(segment.text.strip() for segment in segments).strip()

    if not text:
        raise RuntimeError("No speech was recognized in the audio.")

    print(f"You said: {text}")
    return text


def ask_ollama(user_text):
    """Send the recognized text to Ollama Cloud."""
    print("\n[2/3] Asking the AI assistant...")

    if not API_KEY:
        raise RuntimeError(
            "OLLAMA_API_KEY is missing. Check your .env file."
        )

    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful voice AI assistant. "
                        "Give clear, friendly answers suitable for "
                        "being spoken aloud. Keep answers concise."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()
    answer = response.json()["message"]["content"].strip()

    if not answer:
        raise RuntimeError("The AI returned an empty response.")

    print(f"Assistant: {answer}")
    return answer


def speak_response(text):
    """Convert the AI response into a WAV audio file."""
    print("\n[3/3] Generating spoken response...")

    if not VOICE_MODEL.exists():
        raise FileNotFoundError(
            f"Piper voice model not found: {VOICE_MODEL}"
        )

    command = [
        sys.executable,
        "-m",
        "piper",
        "--model",
        str(VOICE_MODEL),
        "--output_file",
        str(OUTPUT_AUDIO),
    ]

    subprocess.run(
        command,
        input=text,
        text=True,
        check=True,
        cwd=str(PROJECT_DIR),
    )

    print(f"Speech saved to: {OUTPUT_AUDIO}")


def main():
    print("=" * 45)
    print("       VOICE AI ASSISTANT")
    print("=" * 45)

    if not AUDIO_FILE.exists():
        raise FileNotFoundError(
            f"Audio file not found: {AUDIO_FILE}\n"
            "Place your recording in the project folder and "
            "name it sample.m4a."
        )

    transcribed_text = transcribe_audio(AUDIO_FILE)
    answer = ask_ollama(transcribed_text)
    speak_response(answer)

    print("\nSuccess! Your voice assistant completed all three steps.")
    print("Open response.wav to listen to the answer.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}")
        print("Check the error message above and try again.")

