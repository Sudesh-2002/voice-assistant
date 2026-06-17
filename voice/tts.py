"""
Text-to-speech using Piper - local, free, and natural-sounding,
which is why it's the right choice for a production-grade assistant
rather than a robotic built-in OS voice.

Requires the 'piper' CLI (installed via pip install piper-tts) and a
downloaded voice model (.onnx + .onnx.json). See README for setup.
"""
import subprocess
import tempfile
import os
import sys

VOICE_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "en_US-amy-medium.onnx"
)


def speak(text: str) -> None:
    """Converts text to speech using Piper and plays it immediately."""
    if not text:
        return

    if not os.path.exists(VOICE_MODEL_PATH):
        print(f"(voice model not found at {VOICE_MODEL_PATH} - skipping speech)")
        print(f"Assistant would say: \"{text}\"")
        return

    temp_wav = tempfile.mktemp(suffix=".wav")

    result = subprocess.run(
        ["piper", "-m", VOICE_MODEL_PATH, "-f", temp_wav],
        input=text.encode("utf-8"),
        capture_output=True,
    )

    if result.returncode != 0:
        print(f"(TTS failed: {result.stderr.decode(errors='ignore')})")
        print(f"Assistant would say: \"{text}\"")
        return

    _play_wav(temp_wav)


def _play_wav(path: str) -> None:
    """Plays a WAV file using the OS's native player - avoids extra
    Python audio-playback dependencies that often cause install issues."""
    if sys.platform == "win32":
        # PowerShell's SoundPlayer plays synchronously and needs no extra installs.
        subprocess.run(
            [
                "powershell", "-c",
                f"(New-Object Media.SoundPlayer '{path}').PlaySync()",
            ],
            capture_output=True,
        )
    elif sys.platform == "darwin":
        subprocess.run(["afplay", path], capture_output=True)
    else:
        subprocess.run(["aplay", path], capture_output=True)