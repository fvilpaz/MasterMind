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
    ├── 42malaga.md   ← 42 Exam Rank 02 (C): same hybrid method, adapted to studying on a phone
    └── YourCourse.md ← add your own
```

The router reads the student profile (`config/profile.json`), selects the right agent, and injects the relevant source material into the system prompt. **Mandatory progression** — the agent knows where you left off and picks up from there.

---

## Features

| Feature | Details |
|---|---|
| 🔀 Streaming responses | Token-by-token via SSE |
| 🎓 Multi-course agents | Each subject has its own teaching logic |
| 👤 Two-step login | Name → password (admin) or guest mode. After one successful password login the app remembers your name and only asks for the password |
| 🗂 Course picker | Admin gets a varied greeting ("¿A qué le atacamos hoy?") and one coloured card per course; the last one used is tagged |
| 💾 Save your progress | Each course keeps its own progress (`config/progress/<course>.json`). You only move on when the tutor **passes you in an exam**: it tags its reply and the app saves your progress and moves on to the next lesson by itself (no button; the chat restarts with the new lesson). The top bar shows the real lesson (`Ej. 3 · Data Types`, `Week 2 · Arrays`) |
| ⌨️ Chat commands | `/help` (all commands), `/ls` (your lessons: ✅ mastered · 👉 current · 🔒 locked), `/kata` (a short warm-up exercise on the current topic; not available during the exam — the tutor tags exam replies with a hidden mark and the app hides `/kata` and `/read` until it ends); `/back`, `/read` coming. Handled by the app |
| ⏱ Pomodoro timer | 25/5 with beep, as a compact counter in the top bar (green on break, red + pulse when time is up) with a thin progress line — never covers the chat. It counts against the real clock and is saved in the browser, so it survives reloads, closed tabs and sleeping tabs |
| 🗓 Session plan | Pick 1 h / 1 h 30 / 2 h and the app keeps a plan of 2 / 3 / 4 pomodoros. While it runs, a new lesson does **not** ask for your time again; it asks again when you finish the plan or after 4 h (admin only; per browser) |
| 🎨 8 themes | Harvard, Dracula, Cyberpunk, Barbie and more — every text and button checked for contrast (≥ 3:1) in all of them |
| ⌨️ Code editor | CodeMirror panel (`</>`) with syntax colours per category (types, keywords, strings…) for Python, **Java**, **C**, JS, HTML, CSS and Bash; its theme follows the app theme (eclipse on light themes, darcula / dracula / monokai on dark ones) |
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
│   │   ├── Mouredev.md     ← MoureDev teaching strategy
│   │   └── 42malaga.md     ← 42 Exam Rank 02 teaching strategy (C)
│   ├── config/
│   │   ├── profile.json    ← who you are: name, chosen course, mode, language
│   │   └── progress/       ← one file per course: { "current": lesson folder, "mastered": [...] }
│   └── web/
│       ├── app.py          ← Flask server + streaming endpoints
│       ├── app.js          ← frontend logic
│       ├── styles.css      ← themes + layout
│       ├── index.html      ← shell (182 lines)
│       ├── manifest.json   ← PWA manifest
│       └── sw.js           ← service worker
├── brain/                  ← Obsidian vault with source material (cs50/, Moure/, 42/: one folder per lesson, `exNN_name/sources/`)
└── Dockerfile
```

---

## Adding a new course

1. Create `trainer/agent/YourCourse.md` with the teaching strategy
2. Add the entry in `trainer/agent/AGENT.md` routing table
3. It shows up on its own as a card in the course picker (admin). Optional: a display name in
   `COURSE_LABELS` (`trainer/web/app.js`) and a colour with
   `.course-card[data-course="yourcourse"] { --course-color: … }` (`trainer/web/styles.css`)
4. Lessons go in `brain/<root>/exNN_name/sources/` (or `weekNN-name`); map the root folder in `COURSE_ROOTS`
   (`trainer/web/app.py`) and give the course a starting point in `trainer/config/progress/<course>.json`
5. Name the agent file so the lookup finds it (`NAME.md`, `Name.md` or `name.md`): case matters on Linux
   (Cloud Run) even if it works on Windows

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
GITHUB_TOKEN=...         # production only (optional): the app commits progress/profile to the repo
```

```bash
python app.py
# → http://localhost:5000
```

### Tests

No dependencies (no pytest needed). From the repo root:

```bash
python trainer/tests/test_greet.py   # opening greeting: admin/guest, guest name, varied style
python trainer/tests/test_profile.py # profile + per-course progress: isolation, save/next, /ls, security
```

Exit code `0` = all pass. Each test file includes a **control** check that proves it can fail.

---

## Deployment

Every push to `main` triggers an automatic deploy to Cloud Run via GitHub Actions — except commits that only touch
`trainer/config/progress/**`, `trainer/config/profile.json` or `trainer/sessions/**` (`paths-ignore` in
`deploy.yml`).

**Where your progress lives.** With `GITHUB_TOKEN` set on the Cloud Run service (project `mastermind-trainer`,
region `europe-west1`), the app saves progress and profile as commits on `main` (`update: progress/…`,
`update: profile.json`). Without it, it falls back to files on the container's disk, which are lost on every
restart. So: **`git pull --rebase` before pushing from your PC**, and don't commit those files by hand. On Cloud
Run, add variables with `--update-env-vars` (`--set-env-vars` replaces all of them). Moving progress out of git
into a storage bucket is planned (`ROADMAP.md`, point 17).

Built by [Fernando Vilas Paz](https://fvilpaz.github.io/cv/) · [fv-mastermind.com](https://fv-mastermind.com)
