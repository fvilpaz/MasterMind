# MasterMind Trainer — Notas de desarrollo

Este archivo es para Claude Code (desarrollo del repo), no para el LLM de la app.

## Estructura

```
trainer/
├── agent/
│   ├── AGENT.md       ← system prompt principal (enrutador de cursos)
│   ├── CS50.md        ← instrucciones completas para CS50
│   └── Mouredev.md    ← instrucciones para Mouredev (pendiente)
├── config/
│   ├── profile.json   ← estado del estudiante (course, week, mode, topics_mastered)
│   └── local.json     ← rutas locales (mastermind_path)
├── web/
│   ├── app.py         ← servidor Flask, lee agent/AGENT.md como system prompt
│   └── ...
└── weekN-c/
    └── sessions/      ← logs de sesión generados por el agente
```

## Para añadir un nuevo curso

1. Crea `agent/NombreCurso.md` con las instrucciones del agente
2. Añade la entrada en la tabla de `agent/AGENT.md`
3. El estudiante configura `"course": "nombre"` en `config/profile.json`

## Para correr la app

```bash
source venv/bin/activate
python web/app.py
```
