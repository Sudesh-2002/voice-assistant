import threading
import tempfile
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav

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
    print("[Atlas] Ready. Listening for 'Hey Atlas'...")

    while not stop_event.is_set():
        try:
            chunk_path = _record(CHUNK_SECONDS)
            result = model.transcribe(chunk_path, fp16=False)
            transcript = result["text"].lower()

            if WAKE_WORD not in transcript:
                continue

            print(f"[Atlas] Wake word detected! ({transcript.strip()})")
            _play_chime()
            speak("Yes?")

            print(f"[Atlas] Listening for command ({COMMAND_SECONDS}s)...")
            command_path = _record(COMMAND_SECONDS)
            command_result = model.transcribe(command_path, fp16=False)
            command_text = command_result["text"].strip()

            if not command_text:
                speak("I didn't catch that. Say 'Hey Atlas' to try again.")
                continue

            print(f"[Atlas] Command: {command_text}")

            routed = route_command(command_text, api_keys, models)
            print(f"[Atlas] Intent: {routed.get('intent')} "
                  f"| Tier: {routed.get('_tier')} "
                  f"| Params: {routed.get('parameters')}")

            if routed.get("missing_info"):
                reply = routed["missing_info"]
            elif routed.get("intent", "unknown") == "unknown":
                reply = "Sorry, I didn't understand that."
            else:
                reply = dispatch(routed["intent"], routed.get("parameters", {}))

            print(f"[Atlas] Reply: {reply}")
            speak(reply)
            time.sleep(1.5)

        except Exception as e:
            print(f"[Atlas] Error in listen loop: {e}")
            time.sleep(1)

    print("[Atlas] Listener stopped.")