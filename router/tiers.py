"""
The 3-tier AI router.

Tier 1: Groq (Llama 3.3 70B)     -> fast, free, handles most commands
Tier 2: Gemini (3 Flash)         -> smarter, free, for ambiguous/multi-step
Tier 3: DeepSeek (v4-flash)      -> cheap reasoning fallback if tier 2 is down
                                     or its free daily quota is used up

How escalation works: we try one tier. If it errors out (network issue,
quota exceeded, bad key) OR comes back with low confidence, we
automatically try the next tier instead of giving up.
"""
import json
from groq import Groq
from google import genai
from openai import OpenAI

SYSTEM_PROMPT = """You are the brain of a voice assistant. Given a user's
command, extract:
1. "intent" - one of: set_alarm, open_app, send_email, get_directions,
   schedule_event, unknown
2. "parameters" - a dict of relevant details already given. For any time
   mentioned, always convert it to 24-hour "HH:MM" format (e.g. "07:00",
   not "7 AM").
3. "missing_info" - if something REQUIRED is missing, a short question to
   ask the user. Otherwise null.
4. "confidence" - a number 0.0 to 1.0, how sure you are that you understood
   the command correctly.

Respond ONLY with valid JSON. No markdown, no explanation. Example:
{"intent": "set_alarm", "parameters": {"time": "07:00"}, "missing_info": null, "confidence": 0.95}
"""

# If a tier returns confidence below this, we don't trust it - escalate instead.
CONFIDENCE_THRESHOLD = 0.6


def _clean_json(raw_text: str) -> dict:
    """Models sometimes wrap JSON in ```json fences despite instructions
    not to. Strip that before parsing."""
    cleaned = raw_text.strip()
    cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


def _call_groq(transcript: str, api_key: str, model: str) -> dict:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content
    result = _clean_json(raw)
    result["_tier"] = "groq"
    return result


def _call_gemini(transcript: str, api_key: str, model: str) -> dict:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM_PROMPT}\n\nUser command: {transcript}",
    )
    raw = response.text
    result = _clean_json(raw)
    result["_tier"] = "gemini"
    return result


def _call_deepseek(transcript: str, api_key: str, model: str) -> dict:
    # DeepSeek's API is OpenAI-compatible, so we reuse the OpenAI SDK
    # pointed at DeepSeek's base URL instead of OpenAI's.
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content
    result = _clean_json(raw)
    result["_tier"] = "deepseek"
    return result


def route_command(transcript: str, keys: dict, models: dict) -> dict:
    """
    Main entry point. Tries Groq first, then Gemini, then DeepSeek,
    moving to the next tier if one fails or isn't confident enough.

    keys:   {"groq": "...", "gemini": "...", "deepseek": "..."}
    models: {"groq": "...", "gemini": "...", "deepseek": "..."}
    """
    tiers = [
        ("groq", _call_groq),
        ("gemini", _call_gemini),
        ("deepseek", _call_deepseek),
    ]

    last_error = None
    for tier_name, tier_fn in tiers:
        try:
            result = tier_fn(transcript, keys[tier_name], models[tier_name])
            confidence = result.get("confidence", 1.0)
            if confidence >= CONFIDENCE_THRESHOLD:
                return result
            last_error = f"{tier_name} confidence too low ({confidence})"
            print(f"(escalating: {last_error})")
        except Exception as e:
            last_error = f"{tier_name} failed: {e}"
            print(f"(escalating: {last_error})")
            continue

    # Every tier failed or was unsure - return a clear "unknown" instead
    # of crashing the whole assistant.
    return {
        "intent": "unknown",
        "parameters": {},
        "missing_info": "Sorry, I couldn't understand that. Could you try again?",
        "confidence": 0.0,
        "_tier": "none",
        "_error": last_error,
    }