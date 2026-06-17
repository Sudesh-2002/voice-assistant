"""
STEP 1: Text command -> AI -> structured result.

This is the smallest possible version of the assistant's "brain."
No voice yet, no router, no skills that actually do anything -
just proving that we can take a typed command and get back a
structured understanding of what the user wants.

Run it, type things like:
    set an alarm for 7 in the morning
    open chrome
    send an email

...and see how the AI breaks it down into intent + parameters.
"""
import json
import os
from dotenv import load_dotenv
from groq import Groq

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


def main():
    print("Voice Assistant - Step 1 (text only)")
    print("Type a command, or 'quit' to exit.\n")

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in ("quit", "exit"):
            break
        if not user_text:
            continue

        result = ask_ai(user_text)

        print(f"Intent:      {result.get('intent')}")
        print(f"Parameters:  {result.get('parameters')}")
        if result.get("missing_info"):
            print(f"Assistant asks: {result['missing_info']}")
        print()


if __name__ == "__main__":
    main()