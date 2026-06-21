# Voice Assistant (Personal Project)

A custom voice assistant that can understand spoken/typed commands and
eventually control apps (alarms, maps, email, scheduling, etc.) using a
free, multi-tier AI router (Groq -> Gemini Flash -> DeepSeek).

This project is being built in incremental steps.

## Current status: Step 3 - 3-tier AI router

Same voice loop as step 2 (press Enter, speak, press Enter again), but
the single Groq call is now a router with automatic escalation:

1. **Groq** (Llama 3.3 70B) tries first - fast and free, handles most commands.
2. **Gemini** (3 Flash) is tried next if Groq fails or isn't confident -
   smarter, still free, better at ambiguous or multi-step commands.
3. **DeepSeek** (v4-flash) is the final fallback if both above fail -
   very cheap but not fully free (needs a small balance top-up).

The console prints which tier actually answered each command, useful
for seeing the router in action.

Still no real actions yet - that's step 4.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add all three API keys:
   - Groq (free): https://console.groq.com/keys
   - Gemini (free): https://aistudio.google.com/apikey
   - DeepSeek (small paid top-up required): https://platform.deepseek.com/api_keys

3. Make sure the Piper voice model is downloaded (see step 2 setup below
   if you haven't done this yet).

4. Run it:
   ```
   python main.py
   ```

5. Press Enter, speak a command, press Enter again, and watch which
   tier handles it.

### Notes
- If you only have a Groq key and leave Gemini/DeepSeek as placeholders,
  the app will fail on startup - all three keys are currently required.
  We can make tiers optional in a later step if you want to test with
  just one provider.
- ffmpeg must be installed and on your PATH for speech-to-text to work
  (Whisper depends on it internally to decode audio).

## Piper voice model setup (from step 2, if not already done)

Run from your project folder in PowerShell:
```powershell
mkdir voice\models
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx" -OutFile "voice\models\en_US-amy-medium.onnx"
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json" -OutFile "voice\models\en_US-amy-medium.onnx.json"
```



## Roadmap

- [x] Step 1: Text command -> AI -> structured intent (Groq only)
- [x] Step 2: Add voice input (speech-to-text) and voice output (text-to-speech)
- [x] Step 3: Add the full 3-tier AI router (Groq -> Gemini -> DeepSeek) with escalation
- [ ] Step 4: Add real skills that execute actions (set alarm, open app, send email, etc.)
- [ ] Step 5: Run as a background service with always-listening wake word