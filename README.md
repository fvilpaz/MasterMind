# 🧠 MasterMind

**AI-powered learning platform with swappable course agents**

> *Aprende · Domina · Repite*

Live demo → **[fv-mastermind.com](https://fv-mastermind.com)**

---

## What it is

MasterMind is a personal AI tutor that adapts to any learning path. Instead of a generic chatbot, it uses a **modular agent architecture** where each subject has its own specialised agent with its own teaching strategy, progression rules, and source material.

I built it for my own learning — currently running CS50 (Harvard), MoureDev, Google paths, and 42 material — but the system is designed to scale to any content or student.

---

## How it works

```
AGENT.md  (router)
    │
    ├── CS50.md       ← enforces video → notes → exercises → problem set
    ├── Mouredev.md   ← in progress
    └── YourCourse.md ← add your own
```

The router reads the student profile (`config/profile.json`), selects the right agent, and injects the relevant source material into the system prompt — transcriptions, lecture notes, and session logs.

**Mandatory progression** — the agent doesn't ask what you want to study. It knows where you left off and picks up from there.

---

## Features

| Feature | Details |
|---|---|
| 🔀 Streaming responses | Token-by-token via SSE — no waiting, no blank screen |
| 🎓 Multi-course agents | Each subject has its own teaching logic |
| 👤 Two-step login | Name → password (admin) or guest mode |
| ⏱ Pomodoro timer | 25/5 with beep, integrated in the UI |
| 🎨 8 themes | Harvard, Dracula, Cyberpunk, Barbie and more |
| 🤖 Triple AI provider | Guests → Groq / Llama 3.3 70B (free, unlimited). Admin → Gemini or Claude via env var |
| 📓 Session logs | Markdown logs auto-read on next session |
| 📱 Responsive | Mobile-first, works on any screen |

---

## AI models

| Mode | Model | Notes |
|---|---|---|
| Guest | **Llama 3.3 70B** via [Groq](https://groq.com) | Free, unlimited, open-source. Fast inference. Slightly less capable than frontier models on complex reasoning — perfectly fine for CS50 Week 1. |
| Admin | **Gemini 2.5 Flash** (default) or **Claude Sonnet** | Full context: transcripts, lecture notes, session logs. Switchable via `AI_PROVIDER` env var. |

> Guest mode uses open-source AI intentionally — it keeps the platform free and unlimited for anyone to try. If you want the full experience with richer explanations and session memory, request admin access.

---

## Tech stack

- **Backend** — Python · Flask · Gemini API · Claude API (Anthropic) · Groq API
- **Frontend** — Vanilla JS · CSS custom properties · SSE streaming
- **Infrastructure** — Google Cloud Run · Docker · Cloudflare · custom domain

---

## Project structure

```
MasterMind/
├── trainer/
│   ├── agent/
│   │   ├── AGENT.md        ← router: reads profile, selects course agent
│   │   ├── CS50.md         ← CS50 teaching strategy + progression rules
│   │   └── Mouredev.md     ← (in progress)
│   ├── config/
│   │   └── profile.json    ← student state: course, week, topic, progress
│   └── web/
│       ├── app.py          ← Flask server + streaming endpoints
│       └── index.html      ← UI
├── brain/                  ← Obsidian vault with source material (local only)
└── Dockerfile
```

---

## Adding a new course

1. Create `trainer/agent/YourCourse.md` with the teaching strategy
2. Add the entry in `trainer/agent/AGENT.md` routing table
3. Set `"course": "yourcourse"` in `config/profile.json`

That's it. The system picks it up automatically.

---

## Running locally

```bash
git clone https://github.com/fvilpaz/MasterMind
cd MasterMind/trainer/web
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env with your keys
cp .env.example .env

python app.py
# → http://localhost:5000
```

---

## Deployment

Deployed on **Google Cloud Run** from the repo root (so the `brain/` vault is included in the container). Custom domain via **Cloudflare** DNS → Cloud Run managed SSL.

```bash
gcloud run deploy mastermind \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

---

Built by [Fernando Vilas Paz](https://fvilpaz.github.io/cv/) · [fv-mastermind.com](https://fv-mastermind.com)
