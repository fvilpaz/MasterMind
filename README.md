# 🧠 MasterMind

**AI-powered learning platform with swappable course agents**

> *Aprende · Domina · Repite*

Live → **[fv-mastermind.com](https://fv-mastermind.com)**

---

## What it is

MasterMind is a personal AI tutor that adapts to any learning path. Instead of a generic chatbot, it uses a **modular agent architecture** where each subject has its own specialised agent with its own teaching strategy, progression rules, and source material.

Built for personal use — currently running CS50 (Harvard), MoureDev (Java), 42 Málaga (C), Mandarin
Chinese and Japanese — but the system scales to any course or student. Anyone can create a free account
with their own AI key: their progress lives in their browser, never on the server.

---

## How it works

```
AGENT.md  (router)
    │
    ├── CS50.md       ← enforces video → notes → exercises → problem set
    ├── Mouredev.md   ← Brais García method + katas + code reading
    ├── 42malaga.md   ← 42 Exam Rank 02 (C): same hybrid method, adapted to studying on a phone
    ├── Chino.md      ← Pinyin → tones → characters → HSK1, ear and mouth before sight
    ├── Japones.md    ← no syllabus: you type what you heard in an anime, it decodes it
    └── YourCourse.md ← add your own
```

The router reads the student profile — `config/profile.json` for the admin, or the one the browser sends
for everyone else — selects the right agent, and injects the relevant source material into the system
prompt. **Mandatory progression**: the agent knows where you left off and picks up from there.

Two shapes of course: most follow **lessons** (`exNN`/`weekNN` folders, exam before advancing), while a
*notebook* course like Japanese has no lessons at all — one document that keeps growing with whatever
the student brings, handed back whole on every change so nothing is ever lost.

---

## Features

| Feature | Details |
|---|---|
| 🔀 Streaming responses | Token-by-token via SSE |
| 🎓 Multi-course agents | Each subject has its own teaching logic (CS50, MoureDev/Java, 42 Málaga, Mandarin Chinese, Japanese) |
| 🎌 Learn by ear | Japanese taught the way it's actually encountered — you hear a phrase in anime, type it as it sounded, the tutor decodes it and explains the grammar it carries. No fixed curriculum: the notebook grows with whatever you bring. It lives in your browser, travels with every message, and the tutor always hands back the full thing (never a summary) so nothing gets lost between sessions |
| 👤 Three ways in | Password (admin), create a free account (any course, your own AI key, progress in your browser), or try as a guest — same course picker, capped at 15 messages, lifted instantly by pasting your own key. After one successful password login the app remembers your name and only asks for the password |
| 🗂 Course picker | Admin gets a varied greeting ("¿A qué le atacamos hoy?") and one coloured card per course; the last one used is tagged |
| 🧭 Course dashboard | After the password, a full-screen panel (the course you used last comes first, tagged "last"): one card per course with topics mastered (`9 / 10`), a progress bar, what you are on now and the last mastered / next topic, plus an **Achievements** section (first topic, 5 / 10 topics, half a course…) computed from your real progress. One card per screen on a phone, with a two-icon switch to **swipe** sideways or **stack** vertically and page dots (when swiping, Achievements sit below the carousel, not as one more slide); on a computer the cards sit in columns (and, with more than 3 courses, a switch makes them a 3-at-a-time slider). Numbers count up and the "Now / Next" line rotates (all off with *reduce motion*). If the panel fails, the small cards above appear. Fed by `GET /dashboard` (admin only) |
| 📚 Review room | After picking a course, a greeting asks: **review what you learned** or **continue the course**. Review is a free chat about any topic you already mastered — no exam, nothing saved, progress never moves — and the top bar says "Entrenamiento" instead of the lesson. Leave with the "Ir al curso" button or by typing something like "vamos con el curso". Admin only |
| 💾 Save your progress | Each course keeps its own progress (`config/progress/<course>.json`). You only move on when the tutor **passes you in an exam** (several rounds or phases, getting harder, ending with a changed requirement; trivial answers don't pass): it tags its reply and the app saves your progress and moves on to the next lesson by itself (no button; the chat restarts with the new lesson). The top bar shows the real lesson (`Ej. 3 · Data Types`, `Week 2 · Arrays`) |
| ⌨️ Chat commands | `/help` (all commands), `/ls` (your lessons: ✅ mastered · 👉 current · 🔒 locked), `/kata` (a short warm-up exercise on the current topic; not available during the exam — the tutor tags exam replies with a hidden mark and the app hides `/kata` and `/read` until it ends), `/read` (read a short invented snippet and say what it does; half the time it has a bug, half the time it is fine, and the tutor never says which); `/back` coming. Handled by the app |
| ⏱ Pomodoro timer | 25/5 with beep, as a compact counter in the top bar (green on break, red + pulse when time is up) with a thin progress line — never covers the chat. It counts against the real clock and is saved in the browser, so it survives reloads, closed tabs and sleeping tabs |
| 🗓 Session plan | Pick 1 h / 1 h 30 / 2 h and the app keeps a plan of 2 / 3 / 4 pomodoros. While it runs, a new lesson does **not** ask for your time again; it asks again when you finish the plan or after 4 h (admin only; per browser) |
| 🎨 8 themes | Harvard, Dracula, Cyberpunk, Barbie and more — every text and button checked for contrast (≥ 3:1) in all of them |
| ⌨️ Code editor | CodeMirror panel (`</>`) with syntax colours per category (types, keywords, strings…) for Python, **Java**, **C**, JS, HTML, CSS and Bash; its theme follows the app theme (eclipse on light themes, darcula / dracula / monokai on dark ones) |
| 🤖 Triple AI provider | Guests → Groq (free, unlimited). Admin → Gemini or Claude |
| 👥 Your own account, on your own device | "Crear cuenta" asks only for a name: your progress lives in **your browser**, never on the server, and travels with each message so the tutor gets the right material. You pick any course, advance when the tutor passes you, and reloading takes you straight back. ⚙ → **Tus datos** exports it as a JSON (your AI key is deliberately left out) and imports it on another device. Logging out wipes it, so it warns you first |
| 🔑 Bring your own AI key | Paste your own key in ⚙ (or when creating an account) and the answers run on **your** quota, not the server's. The prefix picks the provider: `gsk_` Groq, `AIza` Gemini, `sk-ant-` Claude. Free Groq keys cap at 8 000 tokens/min, so course material is trimmed for them — **Gemini is the recommended free option**. A "how do I get one?" panel walks through both, with real screenshots |
| ☕ Support | A coffee cup in the footer opens PayPal and USDC (Polygon/Base, Solana) with copy buttons |
| 📓 Session logs | Markdown logs auto-read on next session |
| 📱 PWA | Installable on Android/iOS, works offline for the shell |

---

## AI models

| Mode | Model | Notes |
|---|---|---|
| Guest | **Qwen 3.8 27B** via [Groq](https://groq.com) | Free, unlimited, fast. Good enough for most learning tasks. |
| Admin | **Gemini 2.5 Flash** (default) or **Claude Sonnet** | Full context: transcripts, lecture notes, session logs. Switchable via `AI_PROVIDER` env var. |
| With your own key | Whatever your key is for | Groq, Gemini or Claude, picked from the key's prefix. Keys stay in your browser and are never stored server-side. Free Groq tiers cap at 8 000 tokens/min, which the full prompt exceeds — material gets trimmed, so answers are weaker there. Gemini handles it comfortably. |

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
│   │   ├── 42malaga.md     ← 42 Exam Rank 02 teaching strategy (C)
│   │   ├── Chino.md        ← Mandarin: Pinyin → Tones → Characters → HSK1
│   │   └── Japones.md      ← Japanese by ear: no syllabus, a notebook that grows
│   ├── config/
│   │   ├── profile.json    ← who you are: name, chosen course, mode, language
│   │   └── progress/       ← one file per course: { "current": lesson folder, "mastered": [...] }
│   ├── tests/              ← 8 plain scripts, no pytest (see "Tests" below)
│   └── web/
│       ├── app.py          ← Flask server + streaming endpoints
│       ├── app.js          ← frontend logic
│       ├── styles.css      ← themes + layout
│       ├── index.html      ← shell: login steps, chat, settings, guide and café panels
│       ├── manifest.json   ← PWA manifest
│       └── sw.js           ← service worker
├── docs/                   ← screenshots used by the in-app "how do I get a key?" guide
├── brain/                  ← Obsidian vault with source material (cs50/, Moure/, 42/, chino/: one folder per lesson, `exNN_name/sources/`)
└── Dockerfile
```

---

## Adding a new course

1. Create `trainer/agent/YourCourse.md` with the teaching strategy
2. Add the entry in `trainer/agent/AGENT.md` routing table
3. It shows up on its own as a card in the course picker (admin). Optional: a display name in
   `COURSE_LABELS` (`trainer/web/app.js`) and a colour with
   `.course-card[data-course="yourcourse"] { --course-color: … }` (`trainer/web/styles.css`)
4. Lessons go in `brain/<root>/exNN_name/sources/` (or `weekNN-name`). Map the root folder in `COURSE_ROOTS`
   (`trainer/web/app.py`) **only if** it differs from the course id. No need to seed
   `trainer/config/progress/<course>.json`: picking the course the first time sets `current` to the first
   lesson by itself
5. Name the agent file so the lookup finds it (`NAME.md`, `Name.md` or `name.md`): case matters on Linux
   (Cloud Run) even if it works on Windows
6. **Or skip lessons entirely** and make it a *notebook* course, like `Japones.md`: no `exNN` folders, no
   exam, no `[[DOMINADO]]`. The tutor keeps one document that grows with the student, handed back whole
   between `[[CUADERNO]]`/`[[/CUADERNO]]` and stored in their browser. Add the course id to
   `CURSOS_CUADERNO` (`trainer/web/app.js`) and that's it

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
ADMIN_PASSWORD=yourpassword   # never leave this empty: an empty one lets anyone in as admin
GEMINI_API_KEY=...            # for admin Gemini mode
ANTHROPIC_API_KEY=...         # for admin Claude mode
GROQ_API_KEY=...              # for guests and for anyone who brings no key of their own
AI_PROVIDER=gemini            # or: claude
SECRET_KEY=...                # signs the session cookie (defaults to a dev value if unset)
MASTERMIND_PATH=...           # absolute path to brain/ — without it, courses find no material
PORT=5000                     # optional (Cloud Run sets its own)
GITHUB_TOKEN=...              # production only (optional): the app commits progress/profile to the repo
```

Users who paste **their own** key in ⚙ never touch the keys above: their requests run on their quota,
and the key only ever lives in their browser.

```bash
python app.py
# → http://localhost:5000
```

### Tests

No dependencies (no pytest needed), 8 plain scripts. From the repo root — `MASTERMIND_PATH` is required
or the ones reading `brain/` will fail:

```bash
for t in greet profile courses dashboard groq_key perfil_local cuaderno rutas; do
  printf "%-14s " "$t"; MASTERMIND_PATH=$PWD/brain python trainer/tests/test_$t.py | tail -1
done
```

| File | Covers |
|---|---|
| `test_greet` | Opening greeting: admin/guest, guest name, varied style |
| `test_profile` | Profile + per-course progress: isolation, save/next, `/ls`, first-pick init, security |
| `test_courses` | `GET /courses`: who sees which courses, ordering, `.md` filtering |
| `test_dashboard` | Course panel, achievements, and the service worker's cache version |
| `test_groq_key` | Bring-your-own key: which provider a key belongs to, whose quota is spent |
| `test_perfil_local` | Browser-side profile: validation against real topics, **path traversal** |
| `test_cuaderno` | The notebook course: travels whole, trimmed for Groq, never stored server-side |
| `test_rutas` | `/login`, `/logout`, `/save-session`, `/docs/<file>` + path traversal |

Exit code `0` = all pass. Each file ends with a **control** check that proves it can actually fail —
a green suite that cannot fail proves nothing. They work on temporary copies and never touch the real
`profile.json`, progress or session logs; several assert that explicitly at the end.

---

## Deployment

Every push to `main` triggers an automatic deploy to Cloud Run via GitHub Actions — except commits that only touch
`trainer/config/progress/**`, `trainer/config/profile.json` or `trainer/sessions/**` (`paths-ignore` in
`deploy.yml`).

**Where progress lives.** Only the admin's progress reaches the server at all — everyone else's stays in
their own browser and travels with each message, so there is nothing of theirs to store, back up or leak
(see "Your own account, on your own device" above). For the admin: with `GITHUB_TOKEN` set on the Cloud Run service (project `mastermind-trainer`,
region `europe-west1`), the app saves progress and profile as commits on `main` (`update: progress/…`,
`update: profile.json`). Without it, it falls back to files on the container's disk, which are lost on every
restart. So: **`git pull --rebase` before pushing from your PC**, and don't commit those files by hand. On Cloud
Run, add variables with `--update-env-vars` (`--set-env-vars` replaces all of them). Moving progress out of git
into a storage bucket is planned (`ROADMAP.md`, point 17).

Built by [Fernando Vilas Paz](https://fvilpaz.github.io/cv/) · [fv-mastermind.com](https://fv-mastermind.com)
