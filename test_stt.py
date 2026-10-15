'''

from faster_whisper import WhisperModel

print("Loading speech recognition model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Model loaded successfully!")
print("Next: transcribe a sample WAV audio file.")

'''





from faster_whisper import WhisperModel

print("Loading speech recognition model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Model loaded. Transcribing audio...")

segments, info = model.transcribe("sample.m4a")

print("\nRecognized text:")

for segment in segments:
    print(segment.text)

print("\nSpeech-to-text test complete!")

