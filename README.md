# Voice Assistant (Personal Project)

A custom voice assistant that can understand spoken/typed commands and
eventually control apps (alarms, maps, email, scheduling, etc.) using a
free, multi-tier AI router (Groq -> Gemini Flash -> DeepSeek).

This project is being built in incremental steps.

## Current status: Step 1 - Text command -> AI -> structured intent

No voice yet, no real actions yet. This step just proves that a typed
command can be sent to an AI model and parsed into a structured
`intent` + `parameters` result.

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your free Groq API key
   (get one at https://console.groq.com/keys):
   ```
   GROQ_API_KEY=your_real_key_here
   ```

3. Run it:
   ```
   python main.py
   ```

4. Try typing commands like:
   ```
   set an alarm for 7 in the morning
   open chrome
   send an email
   ```

## Roadmap

- [x] Step 1: Text command -> AI -> structured intent (Groq only)
- [ ] Step 2: Add voice input (speech-to-text) and voice output (text-to-speech)
- [ ] Step 3: Add the full 3-tier AI router (Groq -> Gemini -> DeepSeek) with escalation
- [ ] Step 4: Add real skills that execute actions (set alarm, open app, send email, etc.)
- [ ] Step 5: Run as a background service with always-listening wake word