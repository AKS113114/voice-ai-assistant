# Offline Voice AI Assistant

An end-to-end voice AI assistant built using open-weight and locally running models. The application accepts voice input, converts speech to text, generates a response using a local large language model, and speaks the response aloud.

Developed as part of the **AI Internship Technical Assignment at Trikon Software Labs LLP**.

## Features

- **Speech-to-Text (STT):** Uses Faster-Whisper to transcribe recorded speech.
- **Large Language Model (LLM):** Uses Gemma 3 4B locally through Ollama.
- **Text-to-Speech (TTS):** Uses Piper TTS to generate spoken responses.
- **Conversation Memory:** Maintains conversation history for follow-up questions during the session.
- **Web Interface:** Provides a simple interface built with Streamlit.
- **Latency Measurement:** Displays the time taken by speech recognition, LLM response generation, speech synthesis, and total processing.
- **Offline Operation:** Core STT, LLM, and TTS inference runs locally after the required models and dependencies have been downloaded.

## Architecture

```text
User Voice
    |
    v
Streamlit Web Interface
    |
    v
Faster-Whisper (Speech-to-Text)
    |
    v
Recognized Text
    |
    v
Ollama + Gemma 3 4B (Local LLM)
    |
    v
Generated Response
    |
    v
Piper TTS (Text-to-Speech)
    |
    v
Spoken Audio Response
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Speech Recognition | Faster-Whisper |
| LLM Runtime | Ollama |
| Language Model | Gemma 3 4B |
| Speech Synthesis | Piper TTS |
| HTTP Client | Requests |

## Requirements

- Windows, Linux, or macOS (tested on Windows)
- Python installed
- Git
- Ollama installed
- Gemma 3 4B model downloaded in Ollama
- Piper TTS installed with the required voice model
- Internet access for initial installation and model downloads; internet is not required for inference once everything is available locally

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/voice-ai-assistant.git
cd voice-ai-assistant
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Download the local language model

Install Ollama, then run:

```powershell
ollama pull gemma3:4b
```

Ensure the Ollama service is running before starting the application.

### 5. Install Piper and configure the voice model

Install Piper TTS and download the required Lessac medium voice files. Place them in the `voices/` directory as expected by the application:

- `en_US-lessac-medium.onnx`
- `en_US-lessac-medium.onnx.json`

Ensure the Piper executable is accessible to the application.

### 6. Run the application

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Usage

1. Open the web application.
2. Record a voice message.
3. Wait for speech recognition and local response generation.
4. Read the assistant's response and play the generated audio.
5. Ask follow-up questions to test conversation memory.
6. Review the displayed latency measurements.

## Performance Evaluation

The application reports:

- Speech recognition latency
- LLM response latency
- Text-to-speech latency
- Total processing time

Record measurements from multiple test queries on your machine and add the actual results here. Performance can vary with model loading, audio length, hardware, and response length.

| Test | STT (seconds) | LLM (seconds) | TTS (seconds) | Total (seconds) |
|---|---:|---:|---:|---:|
| Test 1 | Add measured value | Add measured value | Add measured value | Add measured value |
| Test 2 | Add measured value | Add measured value | Add measured value | Add measured value |
| Test 3 | Add measured value | Add measured value | Add measured value | Add measured value |

## Hardware and Models

Tested hardware:

- CPU: AMD Ryzen 7 5800H
- RAM: 15.3 GB
- GPU: NVIDIA GeForce RTX 3050 with 4 GB VRAM

Models and configurations:

- STT: Faster-Whisper `base`, CPU, `int8`
- LLM: Gemma 3 4B through local Ollama
- TTS: Piper `en_US-lessac-medium`

## Demo Video

**Demo:** Add the link to your uploaded demonstration video here.

If the video is stored in this repository, link to it using its GitHub file URL or add a relative link such as:

`[Watch the demo video](demo/voice-ai-demo.mp4)`

## Project Structure

```text
voice-ai-assistant/
├── app.py
├── assistant.py
├── requirements.txt
├── .gitignore
├── test_ollama.py
├── test_stt.py
├── README.md
├── demo/
│   └── voice-ai-demo.mp4
└── voices/
    └── (downloaded voice models; not committed)
```

## Privacy and Security

- API keys and `.env` files should never be committed.
- Virtual environments, generated audio files, and large downloaded model files are excluded from version control.
- Core inference is performed locally after setup.

## Limitations

- Response speed depends on the available CPU/GPU resources and model size.
- The application currently processes recorded voice clips rather than continuous streaming audio.
- Recognition quality depends on audio clarity and supported language.
- The application requires the local Ollama service and Piper voice model to be available.

## Future Improvements

- Add voice activity detection (VAD).
- Implement streaming speech recognition and response generation.
- Support interruption while the assistant is speaking.
- Add multilingual speech recognition and synthesis.
- Improve latency through profiling and model optimization.

## Acknowledgements

Built using the open-source Faster-Whisper, Ollama, Gemma, Piper TTS, and Streamlit projects.
