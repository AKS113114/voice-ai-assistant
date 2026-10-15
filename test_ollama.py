
import subprocess

result = subprocess.run(
    [
        "ollama",
        "run",
        "gemma4:31b:cloud",
        "Explain AI in simple words. Answer in 3 sentences."
    ],
    capture_output=True,
    text=True,
    timeout=180
)

if result.returncode == 0:
    print(result.stdout)
else:
    print("Error:", result.stderr)

