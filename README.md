# Atlas — Personal Voice Assistant

A custom AI-powered voice assistant for Windows that listens for your
voice, understands what you want, and actually does it. Built entirely
with free tools and open-source models.

---

## How it works

Say **"Hey Atlas"** → hear a chime → say your command → Atlas does it
and speaks the result back. Everything runs locally on your machine
except the AI inference calls (Groq / Gemini / DeepSeek).

```
Your voice
   │
   ▼
Whisper (local STT)
   │
   ▼
3-tier AI router ──► Groq (fast, free)
   │                 Gemini Flash (smarter, free)
   │                 DeepSeek (cheap fallback)
   ▼
Skill dispatcher ──► set_alarm / open_app / send_email / ...
   │
   ▼
Piper (local TTS) → spoken reply
   │
   ▼
Dashboard (live status + history)
```

---

## Features

- **Wake word** — always listening for "Hey Atlas" in the background
- **3-tier AI router** — automatically escalates to a smarter model if
  the first one isn't confident enough
- **Real skills** — alarm via Windows Task Scheduler with toast notification
- **System tray** — runs silently, right-click → Quit to stop
- **Dashboard** — live status badge + scrollable command history
- **Fully local voice** — Whisper STT + Piper TTS, no cloud voice APIs

---

## Setup

### 1. Clone and install dependencies

```powershell
git clone https://github.com/Sudesh-2002/voice-assistant.git
cd voice-assistant
pip install -r requirements.txt
```

### 2. Get API keys (all free or near-free)

| Provider | Where to get it | Cost |
|----------|----------------|------|
| Groq | https://console.groq.com/keys | Free |
| Gemini | https://aistudio.google.com/apikey | Free |
| DeepSeek | https://platform.deepseek.com/api_keys | Small top-up needed |

### 3. Create your .env file

```powershell
copy .env.example .env
```

Then open `.env` and fill in your real keys:

```
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 4. Install ffmpeg (required for Whisper)

```powershell
winget install ffmpeg
```

Close and reopen PowerShell after installing, then verify:

```powershell
ffmpeg -version
```

### 5. Download the Piper voice model (one-time, ~63 MB)

```powershell
mkdir voice\models
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx" -OutFile "voice\models\en_US-amy-medium.onnx"
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json" -OutFile "voice\models\en_US-amy-medium.onnx.json"
```

Verify the `.onnx` file is ~63 MB:
```powershell
dir voice\models
```

### 6. Run

```powershell
python main.py
```

The dashboard window opens. A blue "A" appears in your system tray.
Wait for `[Atlas] Ready. Listening for 'Hey Atlas'...` in the terminal.

---

## Usage

| Say | What happens |
|-----|-------------|
| "Hey Atlas" | Chime plays, Atlas says "Yes?" |
| "Set an alarm for 7 AM" | Windows toast notification at 7:00 AM |
| "Hey Atlas" + any command | Routes through AI, speaks result |

Right-click the system tray icon → **Quit** to stop Atlas cleanly.

---

## Project structure

```
voice-assistant/
├── main.py           Entry point — launches dashboard, tray, listener
├── atlas.py          Always-listening wake word loop
├── dashboard.py      CustomTkinter GUI (live status + history)
├── state.py          Shared state between listener and dashboard
├── tray.py           System tray icon
├── router/
│   └── tiers.py      3-tier AI router (Groq → Gemini → DeepSeek)
├── skills/
│   ├── base.py       Skill interface
│   ├── alarm.py      Set alarm via Windows Task Scheduler
│   └── registry.py   Maps intent names to skill instances
├── voice/
│   ├── stt.py        Speech-to-text (local Whisper)
│   └── tts.py        Text-to-speech (local Piper)
│   └── models/       Piper voice model files (not in git)
├── .env.example      Copy to .env and fill in your API keys
└── requirements.txt
```

---

## Roadmap

- [x] Step 1: Text command → AI → structured intent (Groq only)
- [x] Step 2: Voice input (Whisper STT) + voice output (Piper TTS)
- [x] Step 3: 3-tier AI router (Groq → Gemini → DeepSeek)
- [x] Step 4: Real skills — alarm via Windows Task Scheduler
- [x] Step 5: Always-listening wake word + system tray
- [x] Step 6: Dashboard — live status + command history
- [ ] More skills: open app, send email, get directions
- [ ] Auto-start with Windows on boot
- [ ] Mobile version (Flutter)

---

## Known issues

- **ffmpeg PATH issue** — after `winget install ffmpeg`, you must close
  and reopen PowerShell (or reboot) before Whisper can find it.
  Run `ffmpeg -version` to confirm it's on your PATH before running Atlas.
