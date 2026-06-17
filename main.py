"""
STEP 2: Voice in -> AI -> Voice out.

Same Groq "brain" as step 1, but now:
  - You press Enter, speak your command, press Enter again to stop.
  - Whisper transcribes what you said.
  - Groq parses it into intent + parameters (same as before).
  - Piper speaks a short reply back out loud.

Still no real actions yet (alarm doesn't actually get set) - that's
step 4. This step is only about closing the voice loop end to end.
"""
import json
import os
from dotenv import load_dotenv
from groq import Groq

from voice.stt import record_until_enter, transcribe
from voice.tts import speak

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY or "your_" in API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Copy .env.example to .env and paste your real key in."
    )

client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = """You are the brain of a voice assistant. Given a user's
command, extract:
1. "intent" - one of: set_alarm, open_app, send_email, get_directions,
   schedule_event, unknown
2. "parameters" - a dict of relevant details already given (e.g. time, app name)
3. "missing_info" - if something REQUIRED is missing, a short question to
   ask the user. Otherwise null.

Respond ONLY with valid JSON. No markdown, no explanation. Example:
{"intent": "set_alarm", "parameters": {"time": "07:00"}, "missing_info": null}
"""


def ask_ai(user_text: str) -> dict:
    """Sends the command to Groq and returns the parsed JSON result."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()

    # Defensive cleanup in case the model wraps output in ```json fences
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent": "unknown", "parameters": {}, "missing_info": None, "raw": raw}


def build_spoken_reply(result: dict) -> str:
    """Turns the structured AI result into a short sentence to speak."""
    if result.get("missing_info"):
        return result["missing_info"]

    intent = result.get("intent", "unknown")
    if intent == "unknown":
        return "Sorry, I didn't understand that."

    params = result.get("parameters", {})
    details = ", ".join(f"{k}: {v}" for k, v in params.items())
    return f"Got it. Intent is {intent.replace('_', ' ')}, with {details}."


def main():
    print("Voice Assistant - Step 2 (voice in, voice out)")
    print("Press Enter to start speaking, then Enter again to stop. Ctrl+C to quit.\n")

    while True:
        input("Press Enter to talk...")
        try:
            audio_path = record_until_enter()
            user_text = transcribe(audio_path)
        except KeyboardInterrupt:
            break

        if not user_text:
            print("(didn't catch anything, try again)\n")
            continue

        print(f"You said: {user_text}")

        result = ask_ai(user_text)
        print(f"Intent:      {result.get('intent')}")
        print(f"Parameters:  {result.get('parameters')}")

        reply = build_spoken_reply(result)
        print(f"Assistant: {reply}\n")
        speak(reply)


if __name__ == "__main__":
    main()