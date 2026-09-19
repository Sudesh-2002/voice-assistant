import os
from dotenv import load_dotenv

from voice.stt import record_until_enter, transcribe
from voice.tts import speak
from router.tiers import route_command
from skills.registry import dispatch

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value or "your_" in value:
        raise RuntimeError(
            f"Missing or placeholder value for '{key}' in your .env file."
        )
    return value


API_KEYS = {
    "groq":     _require("GROQ_API_KEY"),
    "gemini":   _require("GEMINI_API_KEY"),
    "deepseek": _require("DEEPSEEK_API_KEY"),
}

MODELS = {
    "groq":     os.getenv("GROQ_MODEL",     "llama-3.3-70b-versatile"),
    "gemini":   os.getenv("GEMINI_MODEL",   "gemini-3-flash"),
    "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
}


def handle_result(result: dict) -> str:

    if result.get("missing_info"):
        return result["missing_info"]

    intent = result.get("intent", "unknown")
    if intent == "unknown":
        return "Sorry, I didn't understand that. Could you try again?"

    return dispatch(intent, result.get("parameters", {}))


def main():
    print("Voice Assistant - Step 4 (real skills)")
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

        print(f"You said:    {user_text}")

        result = route_command(user_text, API_KEYS, MODELS)
        print(f"Handled by:  {result.get('_tier')}")
        print(f"Intent:      {result.get('intent')}")
        print(f"Parameters:  {result.get('parameters')}")

        reply = handle_result(result)
        print(f"Assistant:   {reply}\n")
        speak(reply)


if __name__ == "__main__":
    main()