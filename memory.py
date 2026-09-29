import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
MAX_HISTORY = 10


def _empty() -> dict:
    return {"preferences": {}, "history": []}


def load() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return _empty()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("preferences", {})
        data.setdefault("history", [])
        return data
    except (json.JSONDecodeError, OSError):
        return _empty()


def save(memory: dict):
    tmp = MEMORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    os.replace(tmp, MEMORY_FILE)


def add_history(memory: dict, user_text: str, atlas_reply: str):
    memory["history"].append({
        "role": "user",
        "content": user_text,
        "time": datetime.now().strftime("%H:%M"),
    })
    memory["history"].append({
        "role": "atlas",
        "content": atlas_reply,
        "time": datetime.now().strftime("%H:%M"),
    })
    memory["history"] = memory["history"][-(MAX_HISTORY * 2):]
    save(memory)


def set_preference(memory: dict, key: str, value: str):
    memory["preferences"][key] = value
    save(memory)
    print(f"[Memory] Saved preference: {key} = {value}")


def build_memory_context(memory: dict) -> str:

    parts = []

    if memory["preferences"]:
        prefs = "\n".join(
            f"  - {k}: {v}" for k, v in memory["preferences"].items()
        )
        parts.append(f"User preferences (use these to fill in missing info):\n{prefs}")

    if memory["history"]:
        recent = memory["history"][-6:]   # last 3 exchanges only, to keep prompt short
        hist = "\n".join(
            f"  {e['role'].capitalize()} ({e['time']}): {e['content']}"
            for e in recent
        )
        parts.append(f"Recent conversation (for resolving follow-up commands):\n{hist}")

    if not parts:
        return ""

    return "\n\n[Memory]\n" + "\n\n".join(parts)