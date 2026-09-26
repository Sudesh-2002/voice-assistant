import threading
import tempfile
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav

from state import (
    app_state,
    STATUS_IDLE,
    STATUS_LISTENING,
    STATUS_WAKE_DETECTED,
    STATUS_RECORDING,
    STATUS_THINKING,
    STATUS_SPEAKING,
)

SAMPLE_RATE = 16000
CHUNK_SECONDS = 2
COMMAND_SECONDS = 6
WAKE_WORD = "atlas"


def _record(duration: float) -> str:
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.int16,
    )
    sd.wait()
    path = tempfile.mktemp(suffix=".wav")
    write_wav(path, SAMPLE_RATE, audio)
    return path


def _play_chime():
    for freq, dur in [(880, 0.12), (1100, 0.12)]:
        t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
        tone = (np.sin(2 * np.pi * freq * t) * 32767 * 0.4).astype(np.int16)
        sd.play(tone, samplerate=SAMPLE_RATE)
        sd.wait()


def listen_loop(api_keys: dict, models: dict, stop_event: threading.Event):
    import whisper
    from router.tiers import route_command
    from skills.registry import dispatch
    from voice.tts import speak

    print("[Atlas] Loading Whisper model...")
    model = whisper.load_model("base")

    app_state.status = STATUS_LISTENING
    print("[Atlas] Ready. Listening for 'Hey Atlas'...")

    while not stop_event.is_set():
        try:
            app_state.status = STATUS_LISTENING
            chunk_path = _record(CHUNK_SECONDS)
            result = model.transcribe(chunk_path, fp16=False)
            transcript = result["text"].lower()

            if WAKE_WORD not in transcript:
                continue

            app_state.status = STATUS_WAKE_DETECTED
            print(f"[Atlas] Wake word detected!")
            _play_chime()

            app_state.status = STATUS_SPEAKING
            speak("Yes?")

            app_state.status = STATUS_RECORDING
            print(f"[Atlas] Listening for command...")
            command_path = _record(COMMAND_SECONDS)

            app_state.status = STATUS_THINKING
            command_result = model.transcribe(command_path, fp16=False)
            command_text = command_result["text"].strip()

            if not command_text:
                app_state.status = STATUS_SPEAKING
                speak("I didn't catch that. Say 'Hey Atlas' to try again.")
                continue

            print(f"[Atlas] Command: {command_text}")

            routed = route_command(command_text, api_keys, models)
            intent = routed.get("intent", "unknown")
            tier = routed.get("_tier", "none")
            print(f"[Atlas] Intent: {intent} | Tier: {tier}")

            if routed.get("missing_info"):
                reply = routed["missing_info"]
            elif intent == "unknown":
                reply = "Sorry, I didn't understand that."
            else:
                reply = dispatch(intent, routed.get("parameters", {}))

            print(f"[Atlas] Reply: {reply}")

            app_state.add_history(
                user_command=command_text,
                intent=intent,
                tier=tier,
                reply=reply,
            )

            app_state.status = STATUS_SPEAKING
            speak(reply)

            time.sleep(1.5)

        except Exception as e:
            print(f"[Atlas] Error: {e}")
            time.sleep(1)

    app_state.status = STATUS_IDLE
    print("[Atlas] Listener stopped.")