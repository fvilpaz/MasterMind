# Roadmap — pendiente tras la sesión del 2026-09-24

Todo lo de aquí es sobre código que **ya funciona hoy**, no bloquea el uso normal — son mejoras
para la próxima sesión con calma.

## 1. Editor de código en el chat (mejora de comodidad, sobre todo móvil)

**Ampliado (2026-09-27):** Java y C en el selector (modo `clike`); tema del editor a juego con el de la
app vía `MutationObserver` sobre `data-theme` (`code-editor.js`). Elegidos midiendo 25 temas con código
Java: eclipse (claros), darcula (dark), dracula, monokai (cyberpunk) — los únicos con color propio para
los tipos y contraste ≥ 3. El botón `</>` ya no es blanco sobre blanco en los temas claros.
Además, auditoría de contraste de los 8 temas: nada por debajo de 3:1 (variables nuevas por tema:
`--accent-text`, `--primary-on-surface`, `--nav-chip-bg/-border`; mint y dracula con texto oscuro sobre
su primario).

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

## ~~4. El panel "Actualizar progreso" no sirve para MoureDev~~ — HECHO (2026-10-02)

Se quitó el panel (selector de Week, tema y botón) y su código: el progreso avanza solo al aprobar
(punto 5). `/update-profile` se queda: lo usan las tarjetas de curso.

## 5. `profile.json` es un único perfil plano, no por curso — EN GRAN PARTE HECHO (2026-09-28)

**Hecho:**
- Progreso por curso en su propio archivo: `config/progress/<curso>.json` (`{"current", "mastered"}`),
  en GitHub en producción. Funciones `get_progress` / `save_progress` / `folder_label`, `course_topics`.
  Guardar un curso nunca toca otro; nombres de curso raros rechazados (path traversal).
- La IA recibe el material del progreso de **su** curso (`_topic_folder`). Arreglado de paso: CS50
  inventaba `week0N-c`, que no existe desde la semana 2.
- `/update-profile` ya no borra la partida al elegir curso (leía la copia vieja de la imagen).
- Barra de arriba con la lección real (`Ej. N · Tema` / `Week N · Tema`), vía `/profile`.
- **Guardar la partida al aprobar:** la IA termina con `[[DOMINADO]]` (Mouredev.md / CS50.md), la app
  la oculta y llama sola a `POST /progress/next` (de uno en uno, sin saltos; **sin botón** desde
  2026-10-02, y se quitó el panel "Actualizar progreso"). Al guardar, el chat empieza de cero con el
  enunciado del tema nuevo. Falta ver un examen real → marca → guardado automático.

**Pendiente:**
- Ver el **primer guardado real de progreso** en producción (`update: progress/…` en GitHub): el
  `GITHUB_TOKEN` ya está en Cloud Run (punto 18) y el commit de perfil se comprobó, el de progreso no.
  Y `/back exN` (punto 8) por si la IA aprueba por error.
- Quitar de `profile.json` los campos viejos (`current_week`, `current_folder`, `current_topic`,
  `weeks_completed`, `topics_mastered`) cuando nadie los use: aún los usan la carpeta de sesiones de CS50
  (`week{current_week}-c`, en `build_system_prompt`) y el nombre del archivo de `/save-session`. El prompt ya
  no se fía de ellos: `current_folder` y `current_topic` salen del progreso (2026-10-02).
- Pasar la carpeta de sesiones al progreso por curso.

Si cambias de CS50 a MoureDev y vuelves, `current_topic`/`current_week`/`topics_mastered` se pisan
entre cursos — no hay estado independiente por curso. Para llevar los dos en paralelo de verdad,
haría falta anidar el perfil por curso (`profile.mouredev.current_folder`, `profile.cs50.current_week`, etc.).

**Lo que quiere Nando (2026-09-27)** — cada curso con su propio progreso, y la barra de arriba
reflejando **la lección real en curso**:

- `MasterMind · mouredev` en la barra: bien como está.
- Debajo, en vez de `Week 1 · Hello World · explain` fijo:
  - **CS50** → `Week N · tema`; **MoureDev** → el ejercicio/tema en curso (p. ej. `Ej. 8 · Bucles`).
    Hoy la palabra `Week` está fija (`app.js:8`) y `current_week` no significa nada en MoureDev.
  - El modo (`explain`, o el que se use) se mantiene tal cual: está bien.
- **Si pasamos a bucles, tiene que verse bucles.**

**Lo que se descubrió al mirarlo (y es más grave que el badge):**
- **La lección de MoureDev no puede avanzar desde la app.** `/update-profile` no admite
  `current_folder` (no está en `allowed`, `app.py:502`), y el panel "Actualizar progreso" solo manda
  `current_topic` y `current_week` (`app.js:482`). Hoy solo se avanza editando `profile.json` a mano.
- **El tutor tampoco actualiza el perfil** al cambiar de tema en el chat. `Mouredev.md` le dice en
  `exam` *"Si pasa: actualiza `topics_mastered` en `config/profile.json`"*, pero es un modelo de chat:
  **no tiene herramienta para escribir ese archivo** y ningún código lee su respuesta. La instrucción
  existe y nadie la ejecuta. "Guardar sesión" tampoco: solo escribe el log en `sessions/`.
  (Por eso a veces *parece* que avanza: el saludo lee el log y "recuerda" el tema, pero el perfil,
  el badge y las fuentes siguen donde estaban.)
- Y `current_folder` es lo que decide **qué fuentes recibe el tutor** (`app.py:84`): si en el chat se
  pasa a bucles pero el perfil sigue en `ex1_HelloWorld`, el tutor sigue recibiendo el material de
  Hello World.

Por tanto van juntos: **perfil por curso (este punto) + control de progreso por curso (punto 4) +
badges que lean la lección real**. Decidir antes cómo se avanza:
  1. a mano (selector de ejercicio leído de `brain/Moure/<ruta>/`);
  2. el tutor propone "¿pasamos a Bucles?" y un botón de la app lo confirma y guarda;
  3. **al aprobar un `exam`**, como ya pide `Mouredev.md` — pero haciéndolo la **app** (p. ej. el
     tutor termina con una marca que el backend detecta), no el modelo.

**DECIDIDO (Nando, 2026-09-27): opción 3 — se avanza solo cuando se domina.** Diseño propuesto:
  - En `exam`, al aprobar, el tutor termina con una marca (p. ej. `[[DOMINADO]]`).
  - La app la detecta, la oculta del chat y muestra un botón **"✅ Dominado — pasar a Ej. N · Tema"**.
    **Confirma Nando** (el modelo se puede equivocar al decir "aprobado").
  - Al confirmar: `topics_mastered` del curso + siguiente ejercicio (orden `exN_` de
    `brain/Moure/<ruta>/`) + la barra se actualiza.
  - **Requisito previo:** perfil por curso (este punto), para que MoureDev no pise a CS50.
  - Pasos: pruebas de caracterización del perfil → perfil por curso (con migración del actual) →
    `/advance` → marca + botón → instrucciones en `Mouredev.md`/`CS50.md` → barra con la lección real. Enlaza con
el punto 10 (rutas de MoureDev).

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

## 8. Comandos en el chat: `/kata`, `/read`, `/ls`, `/back`… (apuntado 2026-09-27)

**Hecho (2026-09-28):** `/help` y `/ls`. La lista vive en `COMMANDS` (`app.js`): `/help` la enseña
entera (los que faltan salen como "próximamente"). Pista fija "💡 Escribe /help…" encima de la caja de
escribir. **Hecho (2026-10-04):** `/kata` — manda a la IA una instrucción oculta; no sale en el examen (ver "Hecho el 2026-10-04").
**Hecho (2026-10-05): `/read`.** Código inventado por la IA (el real de GitHub queda aparcado). **La trampa es
aleatoria** (decidido por Nando): a veces el código está bien y a veces falla algo, y el tutor nunca avisa de cuál.
Si siempre hubiera fallo, leería buscándolo en vez de entender. **La moneda la tira la app** (`Math.random() < 0.5`
en `runCommand`) y se lo dice a la IA en la instrucción oculta (`READ_PROMPT`): el modelo "al azar" casi siempre
pondría fallo. Pregunta neutra ("¿qué hace? ¿ves algo raro?"); si no había fallo y se inventa uno, se lo dice.
`Mouredev.md` ya no habla de "fragmento real de GitHub". Bloqueado en el examen como `/kata`.
Probado con la IA real en producción (2026-10-05): fragmento neutro, sin avisar del caso. **Sin comprobar:** que
alguna vez salga uno *sin* fallo (los dos vistos lo tenían); Nando lo da por bueno, ya que en la conversación el
tutor corrige igual si estaba bien o mal.
**Siguiente:** `/back exN` (necesita `POST /progress/back`). `/read` ya nace bloqueado en el examen (`EXAM_BLOCKED` en `app.js`).

**Nombres decididos por Nando (2026-09-27):** `/kata`, **`/read`** (lectura de código ajeno; no
`/lectura`), **`/ls`** (lista de ejercicios: ✅ dominados, 👉 actual, 🔒 bloqueados) y **`/back exN`**
(volver a un ejercicio **ya dominado** para repasar). Para **avanzar no hay comando**: solo el botón que
sale cuando el tutor aprueba el examen (ver punto 5). Los comandos los intercepta la app, no van al modelo.
En el perfil: `progress` → por curso `{ "current": …, "mastered": [...] }`.

Escribir `/kata` en el chat y que salga una kata; `/read` para un ejercicio de lectura de código
ajeno (los dos ya son parte del método de `Mouredev.md`, pero hoy solo se llega a ellos pidiéndolo
con palabras). Hoy el chat no tiene ningún comando con `/`: todo lo que se escribe va al modelo tal
cual. El único mensaje especial es `__greet__` (saludo inicial, `app.js:140` → `app.py:180`), que
sirve de modelo para interceptar un mensaje antes de mandarlo.

Se hará con la metodología de aprender construyendo (pasos pequeños, "¿qué crees que hace?").

## 9. Inicio: saludo en vez de `select` de curso (apuntado 2026-09-27) — EN PARTE HECHO

**Hecho (2026-09-27):** el `select` es ahora una tarjeta por curso con su color (CS50 carmesí
Harvard, MoureDev azul), nombre bonito (`COURSE_LABELS`), chip "último" en el que usaste y una frase
de saludo aleatoria encima (`COURSE_GREETINGS` en `app.js`). Solo lo ve el admin; el invitado sigue
entrando directo a CS50. **Hecho también:** el saludo *del tutor* varía — `_resolve_greet` añade
al final un estilo al azar de `GREET_STYLES` (entrenador, compañero, mini reto, curiosidad, humor)
sin tocar el texto de `GREET_*` (el `replace` del nombre del invitado depende de él; comprobado con
15 pruebas de caracterización antes y después). **Falta:** `/kata` y `/read` como opciones (punto 8).

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

Material para katas / `/read` (punto 8) ya presente en los ejercicios de Nando:
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

## ~~13. Pomodoro: que no tape el chat en móvil/tablet~~ — HECHO (2026-09-27)

**Hecho:** el círculo flotante pasa a ser una **pastilla en la barra de arriba** (`25:00 ▶ ↺`, junto a
⚙) y una **línea de progreso** fina bajo la barra, en móvil y en escritorio. Ya no flota: no tapa
mensajes ni la caja de escribir. `pomoReposition()` eliminada (ya no hace falta). Se conservan
verde en descanso y rojo + latido al terminar. Probado en 390 px y escritorio con el checklist de
comportamiento (▶, ⏸, ↺, fin → rojo, ▶ → descanso verde). La línea se **llena** (el círculo se vaciaba).
*Lo que había apuntado antes:*

Hoy el pomodoro es un círculo **flotante** (`#pomodoro`, `position: fixed`, abajo a la derecha;
`styles.css:244`, y en móvil `:285` con 96 px). `pomoReposition()` (`app.js:325`) lo sube por encima
del footer recalculando su `bottom` al redimensionar y al escribir. En pantallas pequeñas queda
encima de los mensajes y "mancha" el efecto visual.

**Idea de Nando:** en móvil/tablet, sacarlo del modo flotante y meterlo **en el flujo**, en una
franja entre el chat y el footer (flex), para que no tape nada. En escritorio puede seguir flotante.
Ojo al hacerlo: `pomoReposition()` fija `style.bottom` en línea y ganaría al CSS; habrá que
desactivarlo (o que no haga nada) en ese modo. Probar en móvil vertical, horizontal y tablet.

## 14. Invitados en un mundo aparte (`vguest`) → varios usuarios (apuntado 2026-09-27)

**Idea de Nando:** los invitados deberían vivir en su propio espacio (p. ej. `vguest/` o `users/guest/`),
con su perfil, progreso y sesiones, igual que Nando tiene el suyo. Hoy ya están bastante aislados (no
guardan nada: perfil fijo `GUEST_PROFILE` en el código, sin material, sin progreso, sin sesiones — todo eso
exige admin), pero no tienen "mundo" propio. Es el primer paso hacia **varios usuarios**
(`users/<nombre>/profile.json` + `progress/<curso>.json`), cada uno en lo suyo.

## 15. CS50: faltan materiales de casi todas las semanas (visto 2026-09-27)

Solo `week01-c` (3 archivos) y `week04-memory` (2) tienen algo en `sources/`; las semanas 2, 3 y 5–10
están **vacías**: al llegar ahí, el tutor no tendrá material de apoyo (antes ni se notaba, porque la app
buscaba `week0N-c` y nunca encontraba nada desde la semana 2). Rellenar con fuentes libres
(notas oficiales de CS50, transcripciones), igual que la semana 1.

## 16. Curso "42 Málaga" — HECHO (2026-10-02), con cosas pendientes

**Hecho:** curso nuevo en el selector. Tutor `agent/42malaga.md` (híbrido MoureDev + CS50, adaptado al
móvil: traza a mano, nunca pide compilar). 54 ejercicios de Exam Rank 02 en
`brain/42/exNN_nombre/sources/subject.md` (enunciado en inglés, sin soluciones, ordenados por nivel
`part_0`→`part_4`: ex01–12, 13–26, 27–41, 42–48, 49–54). Progreso propio (`config/progress/42malaga.json`) y
`COURSE_ROOTS['42malaga'] = '42'`. Copia de `exams_by_beltran/` en `brain/42/` (repo abierto de Beltran, con
soluciones y scripts: el tutor **no** lo lee; se guardó ahí para tenerlo en cualquier PC). El archivo del tutor va
en minúsculas porque Linux distingue mayúsculas al buscarlo.

**Pendiente:**
- **Criterio de aprobado.** En la primera sesión el tutor dio `[[DOMINADO]]` sin que Nando escribiera el
  programa final (con errores de sintaxis) y le dictó casi todo. Opciones: (1) tal cual · (2) flexible con las
  erratas del móvil pero **siempre** el programa completo en un mensaje y sin dictar líneas · (3) estricto.
  Recomendada la 2. Mirar si `Mouredev.md` tiene el mismo hueco (no comprobado).
- Que el tutor muestre el `subject.md` tal cual en el primer paso (en la prueba no lo hizo).
- **`/42`**: un reto suelto "off topic" dentro de otro curso, elegido por la app (no inventado por la IA) y
  pasado al tutor como instrucción oculta. Mismo mecanismo que `/kata` (punto 8). Sin hacer.
- Contrastar unos pocos enunciados con una segunda fuente: solo se cruzó inglés/francés dentro del mismo
  repo (`inter` da un aviso falso: el ejemplo francés está traducido con otras palabras y es correcto).
- **Océano** (divulgador, lista de YouTube): Nando quiere aprovechar algo de él; falta decir qué idea. La lista
  no se pudo leer (pantalla de consentimiento de YouTube).
- La barra de arriba enseña el nombre interno `42malaga`, no el bonito "42 Málaga". El orden dentro de cada
  nivel es alfabético (arbitrario).

## 17. El progreso vive dentro del repo del código → llevarlo a un bucket (apuntado 2026-10-02)

**Hoy:** la app guarda progreso y perfil como **commits en `main`** (con `GITHUB_TOKEN`). Consecuencias:
commits de la app mezclados con los de Nando, `git pull --rebase` antes de cada push desde el PC, y un
`paths-ignore` en `deploy.yml` para que esos commits no desplieguen. Antes no se notaba porque el token no
estaba en Cloud Run: nada llegaba a GitHub y el avance se perdía al reiniciar la instancia.

**Propuesta:** `GCS_BUCKET` (Cloud Storage, `europe-west1`, acceso uniforme, sin acceso público, rol *Storage
Object Admin* para la cuenta de servicio de Cloud Run). Con la variable, progreso y perfil se leen y escriben
ahí; sin ella, como ahora (GitHub o local). Bucket vacío → valor inicial = archivos del repo (sin migrar a
mano). Dependencia `google-cloud-storage`. `GITHUB_TOKEN` seguiría solo para los logs de sesión. Unas ~40
líneas en `app.py` + pruebas con un cliente falso; el primer guardado real se verifica en producción. Nando
haría: crear el bucket, el permiso y la variable. Coste prácticamente cero.

## 18. Operación en producción (2026-10-02)

- El servicio `mastermind-trainer` está en el proyecto de Google Cloud **`mastermind-trainer`** (no en "My
  First Project"), región `europe-west1`. `fv-mastermind.com` apunta ahí (dominio asignado a Cloud Run).
- `GITHUB_TOKEN` añadido a Cloud Run (token fine-grained `mastermind-sessions`: solo `fvilpaz/MasterMind`,
  Contents lectura y escritura, sin caducidad). Comprobado: la app hace `update: profile.json` y ese commit
  **no** lanza despliegue. Sin comprobar aún: guardado real de progreso.
- `ADMIN_PASSWORD` rotada (2026-10-02): la temporal que se usó para probar en producción ya no entra (comprobado: 401).
- Al tocar variables desde `gcloud`, usar `--update-env-vars` y no `--set-env-vars` (este reemplaza todas;
  es una sospecha de por qué el token desapareció, no está comprobado).
- Antes de que el token estuviera, la app **fingía guardar**: `save_progress` y `/update-profile` se tragan el
  error de GitHub (solo un `[WARN]` en los logs) y devuelven `ok`.

## 19. Refactor y pruebas pendientes (apuntado 2026-10-02)

Siguiendo la regla del final: **pruebas antes de refactorizar**, nunca a ciegas.

**Pruebas que faltan**
- Frontend: nada con tests (`saveProgress`, `greet`, login que recuerda el nombre, `COMMANDS`). Todo se
  comprobó a mano con el navegador (MCP de Chrome DevTools).
- Servidor: `[[DOMINADO]]` real de punta a punta, `build_system_prompt` con el curso 42, y qué pasa cuando
  GitHub falla en `get_admin_profile` / `/update-profile` / `save_progress`.
- CI: `deploy.yml` despliega **sin pasar los tests**. Añadir un paso que ejecute `test_greet.py` y
  `test_profile.py` antes de desplegar.

**Candidatos a refactor** (solo con pruebas antes)
- `app.py` mezcla rutas, acceso a GitHub (`github_get` / `github_put`), progreso y construcción del prompt.
  Separar el acceso a datos (patrón *Repository*: un solo sitio que sabe dónde se guardan los datos) haría
  trivial el bucket del punto 17.
- `app.js` (575 líneas) junta login, chat, comandos, pomodoro y ajustes.
- Que `save_progress` avise al usuario cuando no puede subir a GitHub, en vez de decir `ok`.
- Quitar los campos viejos de `profile.json` (punto 5).

## 20. Exámenes más largos: que aprobar no sea gratis (apuntado 2026-10-05)

**Problema (idea de Nando):** hoy el `exam` es **un único ejercicio** y el que decide si se aprueba es el
modelo (`Mouredev.md`, `CS50.md`, `42malaga.md`, sección `exam`). Un ejercicio bien resuelto, o el modelo
siendo generoso, y sale `[[DOMINADO]]` (pasó con 42 el 2026-10-02). Como `[[DOMINADO]]` avanza **sin vuelta
atrás** (aún no hay `/back`), aprobar de más sale caro.

**HECHO el paso 1 (2026-10-05), solo en las reglas de los tutores:** `Mouredev.md` → examen en **3 rondas** con
ejercicios inventados (básico → combinando lo del tema → cambio de requisito + dato inesperado); `CS50.md` y
`42malaga.md` → **4 fases** sobre el ejercicio del problem set / `subject.md` (código completo → traza a mano → caso
límite → cambio de requisito). Si la respuesta es trivial, dudosa o de memoria, no se avanza: otra variante.
Equivale a la opción 3 (MoureDev) y a la 2 (CS50 y 42, donde el ejercicio viene fijado). Las reglas de `[[EXAM]]` y
`[[DOMINADO]]` no se tocaron. **Es solo prompt:** el modelo cuenta las rondas y puede saltárselas; sin comprobar con la
IA real. **Falta:** el contador en la app, el `temario.md` por tema y la puerta de katas/reads (abajo).

**Opciones que se barajaron:**
1. **Varios ejercicios seguidos** (p. ej. 3–5), dificultad creciente; se aprueba solo con todos. Es la idea
   de Nando ("siguiente ejercicio… siguiente…"). Ojo con una decena: en el móvil, 10 ejercicios a ~20 min
   cada uno no caben en un pomodoro ni en un trayecto.
2. **Un ejercicio, pero por fases obligatorias:** código completo en un mensaje → traza a mano → caso límite
   → cambio de requisito ("ahora que además haga X") → explicar por qué funciona. Cada fase se pasa o no.
3. **Mixto:** 3 ejercicios cortos + una fase de "cambio de requisito" en el último.

**Ampliado por Nando (2026-10-05): no es solo la duración, es la profundidad.** Ejemplo real: en operadores
pasó el examen con cosas "muy muy simples", y mañana puede aparecer `cond && cond || cond` (¿da true o false?)
y no estar preparado. El examen aprueba **lo que se preguntó**, no **todo el tema**. Lo que pide:
- **Cubrir el tema entero, no un ejemplo:** el tutor lleva una lista de lo que abarca el tema (en operadores:
  aritméticos, comparación, `&&` / `||` / `!`, **precedencia y combinaciones**, cortocircuito…) y no da por
  bueno el examen hasta haber tocado todo, con casos que combinan cosas.
- **Aprender por repetición antes de examinar:** varios ejercicios, katas y lecturas cortas del mismo
  concepto con dificultad creciente, y solo entonces el examen. Hoy `Mouredev.md` ya pide "3 seguidas" en
  `socratic` y katas antes de `exam`, pero es una guía que el modelo puede acortar si ve respuestas fáciles.
- **Que lo fácil no cuente como dominado:** si las respuestas son muy simples, subir la dificultad, no
  aprobar.

**Puerta antes del examen (idea de Nando, 2026-10-05):** exigir haber hecho **X katas y X `/read`** del tema
antes de poder entrar en `exam`. Cuenta la **app**, no el modelo (cada `/kata` y `/read` lanzado suma al tema
actual; el contador **en el progreso del servidor** (`config/progress/<curso>.json`), no en `localStorage`:
así, si te bajas del tren a mitad, al volver (desde el móvil o el PC) sigue "llevas 2 de 3 katas"). Cosas a
decidir:
- **`/read` aún no existe** (punto 8, aparcado): sin él, la puerta solo puede pedir katas. Orden natural:
  `/read` primero, puerta después.
- **Qué cuenta como "hecha":** pedir una kata no es resolverla. Contar solo las que el tutor da por
  buenas (marca nueva, como `[[EXAM]]`), no las pedidas.
- **X por tema**, no global: en operadores 3 katas pueden ser mucho y en punteros poco. Podría ir en el
  `temario.md`.
- **Qué pasa si se intenta examinar antes:** el tutor dice "te faltan 2 katas y 1 lectura" y propone la
  siguiente. Sin salida de emergencia: lo hecho se queda guardado y se sigue otro día.
- Choca con los **pomodoros**: más ejercicios previos = más tiempo; que el plan de la sesión lo tenga en cuenta.

Idea de implementación (sugerencia): una lista de subtemas **por tema** en `brain/<curso>/exN_…/` (p.
`sources/temario.md`), que se pasa al tutor y contra la que se comprueba el examen. Sin eso, "todo el tema" es
lo que el modelo crea que es. Es trabajo de contenido tema a tema, no solo de código.

**Dónde está el fallo de fondo:** el modelo no sabe contar de forma fiable ("llevas 3 de 5"). Lo sólido es que
la **app lleve la cuenta**, como ya hace con `[[EXAM]]`: una marca nueva por ejercicio superado (nombre sin
decidir) y la app solo deja dar `[[DOMINADO]]` cuando se ha llegado al número. Sin eso, es otra regla de
prompt que el modelo puede saltarse.

**Lo que se tocaría:** las 3 secciones `exam` de `agent/*.md` + el mensaje oculto de la app + un contador
(`localStorage` o progreso). Enlaza con el criterio de aprobado de 42 (punto 16) y con `/back` (punto 8).

## 21. Pantalla intermedia tras elegir curso: resumen + repasar o seguir (apuntado 2026-10-05) — HECHO (2026-10-05)

**Hecho:** al pulsar una tarjeta sale la sala (`#step-room`): saludo con el nombre, "Vas por Ej. N · Tema" y dos
botones, **Repasar lo aprendido** / **Seguir con el curso** (este último, como antes). Repasar entra al chat con
una instrucción oculta (`ROOM_PROMPT`) que lleva la lista de temas dominados; charla libre, sin examen. Se sale con
el botón "Ir al curso ▶" (barra de arriba) **o** escribiendo "vamos/volvamos/sigamos/seguimos … curso"
(`ROOM_EXIT`): vacía el chat y lanza el saludo normal con la pregunta de los pomodoros. Mientras `roomActive`, la
app **ignora** `[[DOMINADO]]` (`send()`). La barra de arriba dice "Entrenamiento" en vez de la lección del curso
(`roomBadges`; idea de Nando tras verlo en producción) y la recupera al salir. Solo admin; el invitado entra directo, como antes. Solo `index.html` y
`app.js`, sin tocar `app.py`. Probado en navegador con IA falsa y copia aislada: sala, Repasar, guard del
`[[DOMINADO]]` (con control: en el curso sí avanza), salida por frase y por botón, "Seguir con el curso".
**Sin comprobar:** que la IA real haga caso de `ROOM_PROMPT` (sin examen, sin marcas); el móvil real.
**Limitaciones conocidas:** el tutor sigue recibiendo el material del tema *actual* y no el del repasado
(`_topic_folder`, `app.py`); `/kata` y `/read` dentro de la sala se refieren al tema actual; "Guardar sesión" en la
sala guarda esa charla como log del curso. **Pendiente:** el resumen redactado por el tutor (opción (b)).

*Lo apuntado antes de hacerlo:*

**Idea de Nando:** hoy, al pulsar la tarjeta de un curso, se entra directo al chat y el tutor saluda
(punto 9). En su lugar, una **pantalla intermedia**:

1. **Saludo y resumen de dónde estoy:** tema actual, lo dominado, qué se ha visto (el "repaso de lo que llevo").
2. **Dos caminos:** "Seguir con el curso" (como hoy) o "Repasar".
3. **Repasar:** lista lo ya hecho (✅ de `mastered`) y eliges; p. ej. estando en Strings ej. 4, "repasar
   operadores lógicos". Entonces el tutor pregunta, propone ejercicios, katas y lecturas **solo de ese tema**.

**Aclarado por Nando (2026-10-05): la pantalla es una "sala previa" y el repaso es charla libre, "en seco".**
Como un tema off-topic o hablar con ChatGPT: te pone un ejercicio, habláis, trabajáis. **No hay examen, ni
`[[DOMINADO]]`, ni `[[EXAM]]`, no se guarda nada y no toca el progreso.** Cuando acaba, le dices "vamos con el
curso" y salta al flujo de hoy (el saludo con la pregunta de los pomodoros). Es una sala **antes** de lo que ya
existe, no un cambio dentro de ello.

**Qué hay ya que sirve:** `mastered` / `current` del progreso por curso (`/progress`, `/ls`), la barra con la
lección real, `/kata`, el saludo con estilos (`GREET_STYLES`) y los logs de `sessions/<curso-tema>/`.

**Lo que falta o hay que decidir:**
- **"Qué he aprendido" no está guardado como texto:** el progreso solo sabe *qué* temas están dominados, no qué
  se vio dentro. Opciones: (a) resumen solo con los nombres de los temas (barato, sin IA); (b) que el tutor lo
  redacte leyendo los logs de sesión del tema (más rico, gasta una llamada y los logs pueden no existir).
- **El tutor no debe emitir marcas en la sala.** Con la regla de `Mouredev.md` / `CS50.md` / `42malaga.md`
  (`exam` → `[[DOMINADO]]`) el modelo podría examinarte por inercia. La sala necesita su propio prompt, sin
  `exam` ni marcas, y la app, aun así, debería **ignorar** un `[[DOMINADO]]` llegado desde la sala (cinturón y
  tirantes: el modelo se equivoca). No es `/back exN` (punto 8): aquello rehace un tema; esto solo practica.
- **Material del tutor en la sala:** `_topic_folder` toma el tema del progreso (`current`); aquí habría que
  pasarle el tema elegido. Un tema que no es de la lista (off-topic libre) iría sin material.
- **Sin guardar:** "Guardar sesión" no se ofrece en la sala (o se deja, pero sin tocar el progreso).
- **Invitado:** no guarda nada ni ve material → entraría directo, sin la sala.
- **Salir de la sala:** "vamos con el curso" lo puede interceptar la app (como un comando, tipo `/ls`) en vez
  de depender de que el modelo lo entienda; al salir, vacía el chat y lanza el saludo de hoy (`__greet__` o
  `__greet_plan__`, el que pregunta los pomodoros).

**Orden razonable:** pantalla con resumen por nombres (a) y los dos botones → modo repaso con el tema elegido
→ y solo si hace falta, el resumen redactado por el tutor (b). Enlaza con los puntos 8 (`/ls`, `/back`), 9
(saludo) y 20 (si el examen se alarga, repasar antes de examinarse cobra más sentido).

## Hecho el 2026-10-04

- **Reloj del pomodoro con hora real** (`0fe971d`): guarda la hora de fin y recalcula, en vez de restar 1 por segundo
  (el navegador frena `setInterval` en segundo plano, y por eso "se pausaba"). Estado en `localStorage`
  (`pomo-state`): sobrevive a recargar y a cerrar la pestaña; si acaba mientras no estás, sale 00:00 sin pitido.
- **Plan de pomodoros** (`1702d9b`): los botones ⏱ guardan `pomo-plan` `{total, done, at}`. Cada pomodoro de trabajo
  completo suma uno (el descanso no). Con plan en marcha el saludo de un tema nuevo va por `__greet_plan__` y **no**
  pregunta el tiempo; al cumplirlo, o a las 4 h, vuelve a preguntar. Solo admin y por navegador.
- **`/kata` y marca `[[EXAM]]`** (`7af4cb4`): la IA pone `[[EXAM]]` en cada mensaje mientras dura el examen (regla en
  `Mouredev.md`, `CS50.md` y `42malaga.md`); la app la oculta y bloquea `/kata` y `/read` (y los quita de `/help`)
  hasta que un mensaje no la lleve. No hay marca de fin: la última respuesta manda.
- Probado en navegador real (copia aislada + IA falsa, ver `MEMORY.md`): reloj tras recargar y en pausa, plan en
  marcha y plan cumplido, `/kata` dentro y fuera del examen. Los 3 despliegues terminaron en `success`.
- **Sin comprobar:** que la IA real ponga `[[EXAM]]` en cada mensaje del examen; el modo invitado y el móvil.

## 💡 Aparcado (2026-10-04)

- Plan de pomodoros en el servidor para compartirlo entre PC y móvil (hoy es por navegador).
- Si se escribe "tengo 1 hora" en vez de pulsar el botón ⏱, no se guarda plan: se podría leer del texto.
- Comando `/tiempo` para reiniciar el plan a mitad.
- Curso de pruebas rápido (idea de Nando: "churros") para probar la app de punta a punta con datos absurdos.
- Código real de GitHub en `/read`.
- (2026-10-05) Que el tutor recuerde en qué se equivocó Nando la última vez (p. ej. "falló `&&` con `||`") y lo
  retome al volver, guardando los fallos del tema en el progreso. Hoy solo lo sabe si Nando se lo dice.

## Hecho el 2026-10-02

- **El progreso avanza solo al aprobar**: sin botón "Guardar y pasar a…". Al guardar sale "💾 Partida
  guardada…", la barra pasa al tema nuevo, el chat empieza de cero y la IA da el enunciado nuevo.
- Quitado el panel "Actualizar progreso" (punto 4). Lo que se decidió el 2026-09-25 (mantenerlo separado de
  "Guardar sesión") queda superado: "Guardar sesión" sigue, "Actualizar progreso" ya no existe.
- **Bug del enunciado que se quedaba en el ej. 1**, tres causas a la vez: el perfil del prompt decía ex1
  (ahora el prompt toma `current_folder` / `current_topic` del progreso), el historial del ejercicio anterior
  seguía en el chat (ahora se vacía) y `Mouredev.md` mandaba empezar siempre por `ex1_HelloWorld` cuando no
  había sesiones previas del tema (ahora empieza por el tema del progreso).
- **Login que recuerda el nombre** (`localStorage` `mm-name`, solo tras entrar con contraseña): salta directo a
  la contraseña con "¡Hola, Nando!".
- Curso **42 Málaga** (punto 16).
- `deploy.yml`: `paths-ignore` para los commits de la app (`trainer/config/progress/**`,
  `trainer/config/profile.json`, `trainer/sessions/**`).
- Producción: `GITHUB_TOKEN` en Cloud Run (punto 18); partida de 42 restaurada a ex02 (first_word dominado) y
  MoureDev en ex2.

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
