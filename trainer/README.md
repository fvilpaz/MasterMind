# CS50 Trainer

Personal training system to master CS50 — not just pass it.

Built around the idea that you don't move forward until you genuinely understand the current topic. Each week has lecture sources, problem sets, and structured AI-guided sessions that adapt to your level.

## Philosophy

David Malan stops at every concept — loops, pointers, debugging tools — and makes sure it clicks before moving on. This system tries to replicate that for self-study.

- **No skipping.** Progress is gated by demonstrated understanding, not time spent.
- **Multiple modes.** Explain, Socratic, Debug, and Exam modes adapt to where you are.
- **Token-efficient.** Sessions are structured so the AI gets only the context it needs.

## Structure

```
cs50_trainer/
├── CLAUDE.md              # AI behavior instructions
├── config/
│   ├── profile.json       # Progress: week, topic, mastered topics
│   └── local.json         # Device-specific paths (gitignored)
├── weekN-c/
│   └── sessions/          # Training session logs
└── tester.c               # Scratchpad for exercises (gitignored)
```

## Modes

| Mode | What it does |
|------|-------------|
| `explain` | Breaks down a concept from scratch with analogies and step-by-step execution tracing |
| `socratic` | Asks questions instead of giving answers |
| `debug` | Teaches you to find bugs yourself using gdb/valgrind |
| `exam` | Tests you — won't let you pass until you get it right |

## Multi-device

Uses Git to sync progress. `profile.json` is shared across devices. Device-specific paths (MasterMind location) go in `config/local.json`, which is gitignored — each device sets its own once.

## Weeks

- [x] Week 1 — C
- [ ] Week 2 — Arrays
- [ ] Week 3 — Algorithms
- [ ] Week 4 — Memory
- [ ] Week 5 — Data Structures
- [ ] Week 6 — Python
- [ ] Week 7 — SQL
- [ ] Week 8 — HTML/CSS/JS
- [ ] Week 9 — Flask
- [ ] Week 10 — Cybersecurity

---

## Vision & Roadmap

This project started as a personal CS50 tutor but is designed as a **content-agnostic learning engine**. The trainer (CLAUDE.md logic) is fully decoupled from the knowledge base (MasterMind). Swap the content, keep the engine.

### What it could become

**Phase 1 — Current (local CLI)**
- CS50 trainer running in VS Code + WSL via Claude Code
- MasterMind (Obsidian vault on GitHub) as the knowledge source
- Session logs track daily progress

**Phase 2 — Extended curriculum**
- Add off-topic blocks per session: Bash basics + Cybersecurity intro
- Pomodoro-aware session structure (ask time available → build session plan)
- picoCTF and Google CTF resources as cybersecurity material
- Progress tracked per block in session logs

**Phase 3 — Web interface**
- Minimal chat UI (HTML + API) so it works on mobile without VS Code
- Same CLAUDE.md logic as system prompt
- profile.json synced via GitHub (same repo, same flow)
- Works as a PWA — open in Chrome on any device

**Phase 4 — Platform**
- Backend on Google Cloud Run (already familiar stack)
- MasterMind files read from GitHub or Cloud Storage
- Any Markdown-based knowledge base becomes a course
- Today CS50, tomorrow Python, SQL, Google Cloud certification, or an onboarding manual for a team

### Why this architecture works

The engine (AI behavior) and the content (Markdown files) are separate. To teach a new subject: create a folder in MasterMind, point `local.json` at it, done. No reprogramming. No new infrastructure. The tutor already knows how to explain, question, debug, and examine — it just needs new material.

