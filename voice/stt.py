"""
Speech-to-text using local Whisper. Runs on your machine, no API
cost, no internet needed once the model is downloaded the first time.
"""
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import whisper

WHISPER_MODEL_SIZE = "base"  # tiny / base / small / medium / large
SAMPLE_RATE = 16000

_model = None  # loaded lazily so importing this file is instant


def _get_model():
    global _model
    if _model is None:
        print(f"(loading Whisper '{WHISPER_MODEL_SIZE}' model - first run only)")
        _model = whisper.load_model(WHISPER_MODEL_SIZE)
    return _model


def transcribe(audio_path: str | None) -> str:
    """Converts a recorded WAV file into text. Returns empty string
    if there's no audio to transcribe."""
    if audio_path is None:
        return ""
    model = _get_model()
    result = model.transcribe(audio_path, fp16=False)
    return result["text"].strip()


def listen_and_transcribe() -> str:
    """Convenience wrapper: record via push-to-talk, then transcribe."""
    audio_path = record_until_enter()
    return transcribe(audio_path)