# 🧠 MasterMind

**AI-powered learning platform with swappable course agents**

> *Aprende · Domina · Repite*

Live → **[fv-mastermind.com](https://fv-mastermind.com)**

---

## What it is

MasterMind is a personal AI tutor that adapts to any learning path. Instead of a generic chatbot, it uses a **modular agent architecture** where each subject has its own specialised agent with its own teaching strategy, progression rules, and source material.

Built for personal use — currently running CS50 (Harvard) and MoureDev — but the system scales to any course or student.

---

## How it works

```
AGENT.md  (router)
    │
    ├── CS50.md       ← enforces video → notes → exercises → problem set
    ├── Mouredev.md   ← Brais García method + katas + code reading
    └── YourCourse.md ← add your own
```

The router reads the student profile (`config/profile.json`), selects the right agent, and injects the relevant source material into the system prompt. **Mandatory progression** — the agent knows where you left off and picks up from there.

---

## Features

| Feature | Details |
|---|---|
| 🔀 Streaming responses | Token-by-token via SSE |
| 🎓 Multi-course agents | Each subject has its own teaching logic |
| 👤 Two-step login | Name → password (admin) or guest mode |
| ⏱ Pomodoro timer | 25/5 with beep, integrated in the UI |
| 🎨 8 themes | Harvard, Dracula, Cyberpunk, Barbie and more |
| 🤖 Triple AI provider | Guests → Groq (free, unlimited). Admin → Gemini or Claude |
| 📓 Session logs | Markdown logs auto-read on next session |
| 📱 PWA | Installable on Android/iOS, works offline for the shell |

---

## AI models

| Mode | Model | Notes |
|---|---|---|
| Guest | **Qwen 3.8 27B** via [Groq](https://groq.com) | Free, unlimited, fast. Good enough for most learning tasks. |
| Admin | **Gemini 2.5 Flash** (default) or **Claude Sonnet** | Full context: transcripts, lecture notes, session logs. Switchable via `AI_PROVIDER` env var. |

---

## Tech stack

- **Backend** — Python · Flask · Gemini API · Claude API · Groq API
- **Frontend** — Vanilla JS · CSS custom properties · SSE streaming
- **Infrastructure** — Google Cloud Run · Docker · GitHub Actions (auto-deploy) · Cloudflare · custom domain

---

## Project structure

```
MasterMind/
├── trainer/
│   ├── agent/
│   │   ├── AGENT.md        ← router: reads profile, selects course agent
│   │   ├── CS50.md         ← CS50 teaching strategy + progression rules
│   │   └── Mouredev.md     ← MoureDev teaching strategy
│   ├── config/
│   │   └── profile.json    ← student state: course, week, topic, progress
│   └── web/
│       ├── app.py          ← Flask server + streaming endpoints
│       ├── app.js          ← frontend logic
│       ├── styles.css      ← themes + layout
│       ├── index.html      ← shell (162 lines)
│       ├── manifest.json   ← PWA manifest
│       └── sw.js           ← service worker
├── brain/                  ← Obsidian vault with source material (local only)
└── Dockerfile
```

---

## Adding a new course

1. Create `trainer/agent/YourCourse.md` with the teaching strategy
2. Add the entry in `trainer/agent/AGENT.md` routing table
3. Set `"course": "yourcourse"` in `config/profile.json`

---

## Running locally

```bash
git clone https://github.com/fvilpaz/MasterMind
cd MasterMind/trainer/web
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `trainer/web/` with:
```
ADMIN_PASSWORD=yourpassword
GEMINI_API_KEY=...       # for admin Gemini mode
ANTHROPIC_API_KEY=...    # for admin Claude mode
GROQ_API_KEY=...         # for guest mode
AI_PROVIDER=gemini       # or: claude
```

```bash
python app.py
# → http://localhost:5000
```

---

## Deployment

Every push to `main` triggers an automatic deploy to Cloud Run via GitHub Actions.

Built by [Fernando Vilas Paz](https://fvilpaz.github.io/cv/) · [fv-mastermind.com](https://fv-mastermind.com)
