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
3. Aparece solo como tarjeta en el selector de curso (admin), que guarda `"course"` en
   `config/profile.json`. Opcional: nombre bonito en `COURSE_LABELS` (`web/app.js`) y color con
   `.course-card[data-course="nombre"] { --course-color: … }` (`web/styles.css`)

## Tests

`python trainer/tests/test_greet.py` (desde la raíz del repo, sin pytest). Pruebas de
caracterización del saludo inicial: **pasarlas antes y después** de tocar `GREET_*` o
`_resolve_greet` (p. ej. al traducir, punto 12 del ROADMAP). Ojo: el `replace` del nombre del
invitado depende del texto exacto `llámale 'aprendiz'` de `GREET_GUEST`.

## Para correr la app

```bash
source venv/bin/activate
python web/app.py
```
