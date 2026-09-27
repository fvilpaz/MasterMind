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
- **El contenedor corre como `root`** (auditoría con trivy, 2026-09-27, DS-0002 HIGH): el
  `Dockerfile` no tiene `USER`. No tiene que ver con el login admin/invitado (eso es dentro de la
  app): es con qué usuario de Linux corre `python app.py`. Si alguien explotara un fallo de la app,
  lo ejecutaría como `root`. Arreglo: `RUN useradd -m app` + `USER app` antes del `CMD`.
- **Falta `.dockerignore`**: `COPY . .` mete toda la carpeta en la imagen. Hoy no hay fuga porque
  Cloud Run se construye desde el checkout de GitHub Actions (sin `.env`), pero un `docker build .`
  en local metería `trainer/web/.env` (con `GEMINI_API_KEY`) dentro de la imagen. Añadir un
  `.dockerignore` con al menos `.env`, `**/.env`, `.git`, `__pycache__`.

## ~~7. PWA instalable~~ — HECHO (2026-09-25)

- `manifest.json`, `sw.js` e iconos en `trainer/web/`. Instalada y probada en Pixel 10 (Chrome).
- El service worker solo cachea la interfaz (css, js, manifest, iconos) con red primero.
- `theme_color` se sincroniza dinámicamente con el tema activo al cargar y al cambiar.
- Para forzar que los móviles recojan una versión nueva del SW: subir `CACHE = 'mastermind-vN'`.
- Opcional más adelante: **TWA** (Bubblewrap → APK para Play Store). Para uso propio la PWA basta.

## 8. Comandos en el chat: `/kata`, `/lectura`… (apuntado 2026-09-27)

Escribir `/kata` en el chat y que salga una kata; `/lectura` para un ejercicio de lectura de código
ajeno (los dos ya son parte del método de `Mouredev.md`, pero hoy solo se llega a ellos pidiéndolo
con palabras). Hoy el chat no tiene ningún comando con `/`: todo lo que se escribe va al modelo tal
cual. El único mensaje especial es `__greet__` (saludo inicial, `app.js:140` → `app.py:180`), que
sirve de modelo para interceptar un mensaje antes de mandarlo.

Se hará con la metodología de aprender construyendo (pasos pequeños, "¿qué crees que hace?").

## 9. Inicio: saludo en vez de `select` de curso (apuntado 2026-09-27) — EN PARTE HECHO

**Hecho (2026-09-27):** el `select` es ahora una tarjeta por curso con su color (CS50 carmesí
Harvard, MoureDev azul), nombre bonito (`COURSE_LABELS`), chip "último" en el que usaste y una frase
de saludo aleatoria encima (`COURSE_GREETINGS` en `app.js`). Solo lo ve el admin; el invitado sigue
entrando directo a CS50. **Falta:** que el saludo *del tutor* en el chat también varíe (abajo) y
añadir kata/lectura como opciones de la pantalla (punto 8).

Hoy al entrar hay un `<select id="course-select">` (`index.html:46`, `app.js:386`). La idea: que
MasterMind **salude y pregunte qué quiero hacer hoy**, y enseñe todas las opciones a la vista
(cursos, kata, lectura…) en vez de esconderlas en un desplegable.

**Que el saludo no sea siempre el mismo** (apuntado 2026-09-27): variar la pregunta de arranque —
"¿a qué le atacamos hoy?", "¿qué te apetece aprender?"… Hoy el saludo lo genera el modelo a partir
de `GREET_ADMIN` / `GREET_GUEST` (`app.py:340` y `:347`), que le dan instrucciones fijas; habría que
pedirle variedad o darle una lista de arranques para elegir.

## 10. MoureDev no es solo Java (apuntado 2026-09-27)

`COURSE_ROOTS = {'cs50': 'cs50', 'mouredev': 'Moure/java'}` (`app.py:77`): MoureDev está
**hardcodeado a Java**. En `Coding\Cursos\MoureDev\` ya hay también **`bash`** (en el repo, en
`brain/Moure/`, de momento solo está `java`) y habrá más rutas en el futuro. Al elegir MoureDev
debería preguntar **qué ruta** (Java, Bash…), leyendo las que existan en vez de tenerlas escritas a
mano. Relacionado con los puntos 4 y 5: el progreso tendrá que ser por ruta, no solo por curso.

## 11. Ruta de Bash en `brain/Moure/bash/`, más rica que la de Java (apuntado 2026-09-27)

Mismo patrón que Java (`exN_Tema/src/` con el código de Nando + `sources/enlaces.md` solo con
fuentes libres, nada de MoureDev Pro), pero ampliando con material abierto de GitHub. Los scripts de
práctica de `Coding\Cursos\MoureDev\bash\` se agrupan de forma natural en:

| Tema | Scripts de Nando |
|---|---|
| `ex1_PrimerScript` | `1st_script.sh`, `script.sh` (echo, variables, `read`, aritmética) |
| `ex2_Parametros` | `param_script.sh` (`$0`, `$1`, `$#`, `$@`) |
| `ex3_Condicionales` | `conditional_script.sh` (`if`/`elif`, `case`, `-z`/`-n`/`-e`) |
| `ex4_Bucles` | `loops.sh` (`for`, `while`, `until`) |
| `ex5_Errores` | `errors_script.sh` (`$?`, `\|\|`, `&&`) |
| `ex6_Cron` | `ejercicios/*.sh` + `guia_cron` |

Fuentes candidatas (todas comprobadas el 2026-09-27 que existen; falta revisar licencia y contenido
antes de usarlas):

- Oficial: GNU Bash Reference Manual — https://www.gnu.org/software/bash/manual/bash.html
- Referencia libre: W3Schools Bash — https://www.w3schools.com/bash/
- BashGuide (Greg's Wiki) — https://mywiki.wooledge.org/BashGuide
- Google Shell Style Guide — https://google.github.io/styleguide/shellguide.html
- GitHub: `denysdovhan/bash-handbook`, `Idnan/bash-guide`, `dylanaraps/pure-bash-bible`,
  `jlevy/the-art-of-command-line`, `onceupon/Bash-Oneliner`, `awesome-lists/awesome-bash`
- Herramienta: `koalaman/shellcheck` (linter de bash: detecta solo fallos como el de abajo)

Material para katas / `/lectura` (punto 8) ya presente en los ejercicios de Nando:
`ejercicios/backup_diario.sh` guarda `log_file=...` **entre** el `tar` y el `if [ $? -eq 0 ]`, así
que el `$?` es el de la asignación y siempre dice "Backup exitoso" aunque `tar` falle. No se
corrige: es un ejercicio perfecto para `ex5_Errores`.

Orden: contenido tema a tema → adaptar `Mouredev.md` (hoy habla solo de Oracle/Java) → punto 10.

## 12. Plataforma en inglés o en castellano (apuntado 2026-09-27)

Poder elegir idioma: en inglés, toda la plataforma en inglés (botones, menús, mensajes **y** las
respuestas del tutor); en castellano, todo en castellano. Hoy está todo fijo en castellano:
`<html lang="es">` (`index.html:2`), los textos de la interfaz escritos a mano en HTML/JS, y los
prompts (`GREET_*`, `build_system_prompt`) en castellano. Ya existe un campo `"language": "es"` en el
perfil por defecto (`app.py:18`) que hoy nadie usa: puede ser el punto de partida.

**Por qué:** pedirle al tutor en el chat "¿practicamos en inglés?" ya funciona (el modelo cambia
solo), pero la interfaz sigue en castellano. Hace falta para **enseñar la app a alguien de habla
inglesa** sin que tenga que pedir nada.

## Hecho el 2026-09-25

- Separación de `index.html` en `styles.css` + `app.js` (punto 2).
- `profile.json` se guardaba en cp1252 en Windows → rompía con acentos. Ahora UTF-8.
- Los botones "Guardar sesión" y "Actualizar progreso" se quedan separados (decisión de Nando):
  sesión = la conversación a `sessions/`; progreso = tema/semana en `profile.json`.
- PWA instalable y probada en Pixel 10 / Chrome (punto 7).
- `theme_color` dinámico — el notch/barra de estado cambia con el tema activo.
- Deploy automático a Cloud Run vía GitHub Actions en cada push a main.

## Hecho el 2026-09-24 (para no repetir)

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
