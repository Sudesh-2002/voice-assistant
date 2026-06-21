"""
STEP 3: 3-tier AI router (Groq -> Gemini -> DeepSeek).

Same voice loop as step 2, but the single Groq call is replaced with
a router that tries Groq first, and automatically escalates to Gemini
then DeepSeek if a tier fails or isn't confident in its answer.

Still no real actions yet (alarm doesn't actually get set) - that's
step 4.
"""
import os
from dotenv import load_dotenv

from voice.stt import record_until_enter, transcribe
from voice.tts import speak
from router.tiers import route_command

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value or "your_" in value:
        raise RuntimeError(
            f"Missing or placeholder value for '{key}' in your .env file."
        )
    return value


API_KEYS = {
    "groq": _require("GROQ_API_KEY"),
    "gemini": _require("GEMINI_API_KEY"),
    "deepseek": _require("DEEPSEEK_API_KEY"),
}

MODELS = {
    "groq": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    "gemini": os.getenv("GEMINI_MODEL", "gemini-3-flash"),
    "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
}


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
    print("Voice Assistant - Step 3 (3-tier router: Groq -> Gemini -> DeepSeek)")
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

        result = route_command(user_text, API_KEYS, MODELS)
        print(f"Handled by:  {result.get('_tier')}")
        print(f"Intent:      {result.get('intent')}")
        print(f"Parameters:  {result.get('parameters')}")

        reply = build_spoken_reply(result)
        print(f"Assistant: {reply}\n")
        speak(reply)


if __name__ == "__main__":
    main()