# Voice Assistant (Personal Project)

A custom voice assistant that can understand spoken/typed commands and
eventually control apps (alarms, maps, email, scheduling, etc.) using a
free, multi-tier AI router (Groq -> Gemini Flash -> DeepSeek).

This project is being built in incremental steps.

## Current status: Step 2 - Voice in, voice out

You press Enter, speak your command, press Enter again to stop. Whisper
transcribes it, Groq parses it into intent + parameters (same as step 1),
and Piper speaks a short reply back out loud. Still no real actions
yet - the alarm intent doesn't actually set an alarm. That's step 4.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your free Groq API key
   (get one at https://console.groq.com/keys):
   ```
   GROQ_API_KEY=your_real_key_here
   ```

3. **Download the Piper voice model** (one-time, ~63 MB). Run these in
   PowerShell from your project folder:
   ```
   mkdir voice\models
   cd voice\models
   curl -L -o en_US-amy-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx"
   curl -L -o en_US-amy-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
   cd ..\..
   ```
   If a file downloads but is only a few KB, the download failed silently -
   check your internet connection and try again. A real model file is ~63 MB.

4. Run it:
   ```
   python main.py
   ```

5. Press Enter, say something like "set an alarm for 7 in the morning",
   press Enter again, and listen for the spoken reply.

### Notes
- First run will download the Whisper "base" model automatically (~150 MB).
- If you don't have a voice model downloaded yet, the assistant will still
  work - it just prints what it *would* say instead of speaking it out loud.
- If `sounddevice` complains about no input device, check Windows sound
  settings to make sure a microphone is set as the default recording device.


## Roadmap

- [x] Step 1: Text command -> AI -> structured intent (Groq only)
- [x] Step 2: Add voice input (speech-to-text) and voice output (text-to-speech)
- [ ] Step 3: Add the full 3-tier AI router (Groq -> Gemini -> DeepSeek) with escalation
- [ ] Step 4: Add real skills that execute actions (set alarm, open app, send email, etc.)
- [ ] Step 5: Run as a background service with always-listening wake word