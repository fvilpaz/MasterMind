# Roadmap — pendiente tras la sesión del 2026-09-24

Todo lo de aquí es sobre código que **ya funciona hoy**, no bloquea el uso normal — son mejoras
para la próxima sesión con calma.

## 1. Editor de código en el chat (mejora de comodidad, sobre todo móvil)

Ahora mismo escribir código en el chat es un `textarea` plano — sin resaltado, sin autoindentado,
y en el móvil no hay ni salto de línea cómodo. La idea: un botón "modo código" que abra un panel
con **CodeMirror** (librería ligera, se mete con un `<script>` sin build tools, encaja con cómo
está montado `index.html`). Da resaltado de sintaxis por lenguaje, autoindentado real (Enter tras
`{` salta con la tabulación puesta), y mejor comportamiento táctil que un `textarea` normal.

No es solo estética: ahora mismo Nando no puede escribir código con comodidad desde el tren/móvil,
que es el caso de uso principal de todo este proyecto.

## 2. ~~Separar `index.html` en `styles.css` + `app.js`~~ — HECHO (2026-09-25)

`index.html` pasa de 975 a 162 líneas. `styles.css` y `app.js` son idénticos a los bloques
`<style>`/`<script>` originales (comprobado con `diff` contra el commit anterior). `app.py` sirve
`/styles.css` y `/app.js` con rutas explícitas. Probado a mano por Nando en la web.

Esto desbloquea poder usar ESLint/Stylelint de verdad (ver punto 3).

## 3. `pre-commit` con seguridad y lint de Python

Acordado pero no montado: `detect-secrets` (para que no vuelva a pasar lo de los PDFs/API keys en
el historial), `bandit` (seguridad Flask/Python), `ruff` (lint + formato).

## 4. El panel "Actualizar progreso" no sirve para MoureDev

El selector de Week 1-5 + botón de progreso es específico de CS50 (manda `current_week`, no
`current_folder`). Para MoureDev, cambiar de tema desde la interfaz hoy no funciona — hay que
editar `config/profile.json` a mano. Hace falta un control de progreso genérico por curso.

## 5. `profile.json` es un único perfil plano, no por curso

Si cambias de CS50 a MoureDev y vuelves, `current_topic`/`current_week`/`topics_mastered` se pisan
entre cursos — no hay estado independiente por curso. Para llevar los dos en paralelo de verdad,
haría falta anidar el perfil por curso (`profile.mouredev.current_folder`, `profile.cs50.current_week`, etc.).

## 6. Seguridad — antes de que esto sea de verdad público

- `ADMIN_PASSWORD` actual es débil (puesta como prueba temporal) — cambiar antes de tomárselo en
  serio.
- Confirmar que `GROQ_API_KEY` está bien puesta en las variables de entorno de Cloud Run (el modo
  invitado depende de ella; en local no está configurada, así que no se pudo probar del todo aquí).

## Hecho hoy (para no repetir)

- Selector de curso al loguearse (CS50/MoureDev), leyendo `agent/*.md` reales.
- `Mouredev.md` completo: método Brais + Malan + katas + lectura de código ajeno + escalada
  explicar→verificar→cambiar ejemplo→bloqueo real.
- `build_system_prompt` generalizado (ya no depende de "cs50" a fuego).
- Bug de `local.json` (ruta de WSL rota) arreglado — ni CS50 cargaba fuentes bien antes de esto.
- Modelos de Gemini actualizados a los alias `-latest`; modelo de Groq (`llama-3.3-70b-versatile`,
  deprecado) cambiado a `openai/gpt-oss-20b`.
- Bug real de encoding (`UnicodeDecodeError` en Windows al leer `.md` con acentos) arreglado en
  todas las lecturas de texto.
- `/update-profile` y `/save-session` ya no fallan con 500 si no hay `GITHUB_TOKEN` — guardan en
  local siempre, GitHub es best-effort.
- Logs de sesión reorganizados bajo `trainer/sessions/<curso-tema>/` (antes ensuciaban la raíz de
  `trainer/`).
- Dropdown personalizado (`makeCustomSelect`, que existía sin usarse) conectado a los 4 selects
  reales, con estilos coherentes en todos los temas visuales.
- Render de markdown básico (negrita/cursiva/código) en el chat, escapando HTML para no abrir XSS
  en modo invitado.
- Limpieza legal: PDFs de pago de MoureDev purgados de todo el historial de git y del repo.
- Favicon del sitio (usaba el del navegador por defecto).

## Regla de trabajo para cualquier refactor futuro (no solo aquí)

Antes de refactorizar algo que ya funciona: identificar comportamientos actuales, escribir tests
(o al menos un checklist manual si no hay framework), y solo entonces tocar la implementación.
Nunca a ciegas. (Ver memoria de Claude: `refactor-legacy-con-tests`.)
