import os
import threading
from dotenv import load_dotenv

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


def main():
    from atlas import listen_loop
    from tray import run_tray

    stop_event = threading.Event()

    listener_thread = threading.Thread(
        target=listen_loop,
        args=(API_KEYS, MODELS, stop_event),
        daemon=True,
        name="AtlasListener",
    )
    listener_thread.start()

    print("[Atlas] Starting. Look for the tray icon in the bottom-right corner.")
    print("[Atlas] Right-click the tray icon and select Quit to stop.\n")

    run_tray(stop_event)

    listener_thread.join(timeout=3)
    print("[Atlas] Goodbye.")


if __name__ == "__main__":
    main()