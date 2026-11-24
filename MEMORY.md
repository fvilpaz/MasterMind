# MEMORY — trampas, decisiones y operación de MasterMind

> Lo que **no se deduce del código**. Una línea por cosa; actualizar cuando algo cambie.
> **Repo público: aquí nunca contraseñas, tokens ni claves.**

## Producción
- Cloud Run: servicio `mastermind-trainer`, proyecto de Google Cloud `mastermind-trainer`, región
  `europe-west1`. `fv-mastermind.com` apunta ahí. Se despliega solo con cada push a `main`
  (`.github/workflows/deploy.yml`, ~1,5 min). Cloud Run se configura desde la consola o el portátil:
  en el PC de Windows no hay `gcloud`.
- Variable `GITHUB_TOKEN` en Cloud Run: token fine-grained `mastermind-sessions` (solo este repo, Contents
  lectura y escritura, sin caducidad). Si falta, la app **sigue funcionando pero finge guardar** (ver Datos).
- Añadir variables con `--update-env-vars`, no `--set-env-vars` (reemplaza todas; sospecha de por qué el
  token desapareció, sin comprobar).
- Ver despliegues sin `gcloud`: `https://api.github.com/repos/fvilpaz/MasterMind/actions/runs` (repo público).
- Durante un despliegue conviven la revisión vieja y la nueva: un mensaje del chat puede caer en la vieja.

## Datos y git (lo que más confunde)
- Con `GITHUB_TOKEN`, la app guarda progreso y perfil como **commits en `main`** (`update: progress/<curso>.json`,
  `update: profile.json`). El `paths-ignore` de `deploy.yml` evita que esos commits desplieguen.
- Por eso: **`git pull --rebase` antes de cada push** desde el PC (si no, rechaza por *non-fast-forward*) y **no
  commitear** `trainer/config/progress/*.json` ni `profile.json` a mano, salvo para restaurar una partida
  a propósito. El móvil y la web no necesitan pull: leen de GitHub.
- Sin token (o si GitHub falla), `save_progress` y `/update-profile` escriben en el disco del contenedor y
  devuelven `ok`: se pierde al reiniciar. `github_get` devuelve `None` en silencio si falla.
- Plan: sacar el progreso de git a un bucket (ROADMAP, punto 17).

## Trampas
- **Tras la contraseña, la caja vieja (`#step-course`, tarjetas pequeñas) ya no se enseña de paso:** `showCourseStep`
  oculta `.login-box` entera mientras carga y solo la vuelve a mostrar si el panel falla (plan B). Si algún día se quiere
  como paso normal: poner `step.style.display = 'flex'` donde lo dice el comentario. Para medir un parpadeo así, meter
  latencia artificial en el `fetch` de `/dashboard`: en `localhost` va tan rápido que ni se ve.
- **Tras la contraseña NO dejar nunca un vacío:** `showCourseStep` pinta primero un marco (`esqueletoDashboard`) y
  pide solo `/dashboard`; si se esconde algo sin poner nada en su sitio, queda a la vista lo único que no se escondió
  (la fila de enlaces del login, que es hermana de la caja). Y cada lectura de `get_progress`/`get_admin_profile` es una
  ida y vuelta a GitHub en producción: leerlas a la vez (hecho en `/dashboard`) o no pedirlas.
- **`#dashboard` es una columna flex:** un hijo con `margin: 0 auto` necesita `width: 100%` o se ajusta a su contenido (el
  carrusel de tarjetas lo ensanchaba a ~10 000 px). Es lo que rompió móvil y escritorio el 2026-10-15.
- **Tres cosas que parecían "footer":** `#input-bar` (caja de escribir del chat, con el botón `</>`), `.site-footer`
  (único pie de enlaces, siempre abajo, por encima del login) y, antes, una copia de enlaces dentro del login (borrada).
- **Nombre, color e icono de cada curso: solo en `window.CURSOS`** (`dashboard.js`, que carga antes que `app.js`). No
  repetirlos en CSS ni en `app.js`.
- **Elegir curso guarda con 3 llamadas a GitHub** (`/update-profile`): la UI no debe esperar en blanco; `showRoomStep`
  recibe esa promesa y enseña la sala al instante. Para probar el panel sin token: `fetch` envuelto con retraso.
- Probando en el navegador tras cambiar JS/CSS: el service worker y la caché devuelven lo viejo; desregistrar el SW y
  borrar `caches` (o Ctrl+F5) antes de medir, o se miden archivos antiguos.
- El archivo del tutor, en minúsculas (`42malaga.md`): Linux distingue mayúsculas, Windows no.
- `course_topics` solo ve carpetas `exN_…` / `weekN…` dentro de la raíz del curso en `brain/`; `COURSE_ROOTS`
  (`app.py`) mapea curso → carpeta. Un curso sin `config/progress/<curso>.json` empieza con `current: None`
  y el tutor no recibe material.
- `Mouredev.md`: "NUEVO — sin sesiones previas" sale en cuanto avanzas a un tema sin log; el tutor debe empezar
  por `current_folder` (que sale del progreso), no por ex1.
- `[[DOMINADO]]` lo escribe el tutor y la app avanza sola: si lo emite sin que haya aprobado, se avanza sin
  vuelta atrás (aún no hay `/back`). Pasó con 42 el 2026-10-02.
- `/update-profile` y `save_progress` no avisan si fallan en GitHub.
- El campo `#login-password` **no está en un `<form>`** a propósito: Enter lo gestiona `keydown` en `app.js`; con
  `<form>` se enviaría además y recargaría la página. Para que el navegador lo guarde basta `name` y `autocomplete`.

## Pomodoro, plan y marcas (cómo funciona)
- Todo en `localStorage`, por navegador: `pomo-state` (`{mode, remaining, endsAt}`; `endsAt` = hora real de fin, 0 si
  está parado) y `pomo-plan` (`{total, done, at}`, caduca a las 4 h). No pasa por el servidor.
- El saludo tiene dos formas: `__greet__` (pregunta el tiempo) y `__greet_plan__` (no lo pregunta, solo admin).
  Los dos en `GREET_TOKENS` (`app.py`). Un token nuevo hay que añadirlo ahí o `is_greet` no lo reconoce.
- Marcas ocultas de la IA: `[[DOMINADO]]` (aprobó: guarda y avanza) y `[[EXAM]]` (está en examen, en cada mensaje).
  `hideMark` (`app.js`) las quita al mostrar, también a medias (`[[EX`).

## Cómo probar en local
- **Trampa del navegador de pruebas (extensión de Chrome):** `scrollTo({behavior:'smooth'})` NO anima: se queda quieto
  ~1,8 s y salta de golpe, así que las lecturas de `scrollLeft` salen "una acción por detrás". Medido con un `scrollTo`
  suelto, sin código de la app. Esperar ≥ 3 s tras cada acción o usar `behavior:'instant'`. En un navegador normal anima.
- **Probar de punta a punta sin tocar nada real** (así se hizo el 2026-10-04): `git archive HEAD trainer` a una
  carpeta temporal (sin `.env`, sin `GITHUB_TOKEN`) y un `run.py` que importa `app`, fija `ADMIN_PASSWORD` temporal,
  `GITHUB_TOKEN=''`, `MASTERMIND_PATH` = ruta de `brain/` del repo real (solo lectura) y cambia `stream_gemini` y
  `stream_groq` por una IA falsa guionizada. `MASTERMIND_PATH` es la carpeta `brain`, no la raíz del repo.
  En un script de Python, rutas con `/` (un `\b` se vuelve retroceso) y en PowerShell no reescribir archivos con
  `Get-Content`/`Set-Content` sin codificación: estropea los acentos.
- Navegador: sirve también la extensión Claude in Chrome (`javascript_tool` para pulsar los mismos botones).
- Este Git Bash no tiene `gh`: los despliegues se ven con la API pública (arriba, Producción).
- Arrancar: `cd trainer/web && ADMIN_PASSWORD=<la que quieras> PORT=8080 python app.py` (`load_dotenv` no pisa
  variables ya definidas). Parar el servidor en Windows con PowerShell (no hay `pkill`).
- Elegir curso o `/progress/next` **modifica** `trainer/config/progress/*.json` y `profile.json`: copiar antes,
  restaurar después, y comprobar que `git status` queda limpio.
- Pruebas: `python trainer/tests/test_greet.py`, `test_profile.py`, `test_courses.py` (`GET /courses`) y
  `test_dashboard.py` (`GET /dashboard` y los archivos del panel, con un `brain/` inventado; en producción son N
  lecturas de GitHub, una por curso) (sin dependencias,
  sobre una copia temporal).
- Navegador: MCP `chrome-devtools` (`claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest`),
  un contexto aislado por prueba. Login: nombre → "Tengo contraseña" → contraseña → tarjeta de curso; el
  nombre se recuerda en `localStorage` (`mm-name`). El botón de logout borra todo el `localStorage` y el
  `sessionStorage` (2026-11-16): sin eso, tras cerrar sesión volvía directo a la contraseña y no había forma de
  entrar como invitado en ese navegador.

## Gemini: trampas (2026-11-16)
- **Los alias `gemini-flash-latest` / `-pro-latest` solo existen en la API `v1beta`**; en `v1` dan `404 NOT_FOUND`
  (comprobado con la clave: `v1` lista solo modelos con número, p. ej. `gemini-3.8-flash`). `app.py` fuerza
  `api_version='v1beta'` en `call_gemini` y `stream_gemini`. `google-genai` va **sin versión fija** en
  `trainer/web/requirements.txt`: cada reconstrucción de la imagen puede traer un SDK con otro valor por defecto,
  y así se rompió sin tocar código. Si vuelve a pasar: probar el alias en `v1` y `v1beta` con la clave antes de culpar al modelo.
- **Respaldo de modelos (2026-11-17, `6dd9f16`):** el invitado va por la cadena `GROQ_MODELS` de `app.py` (`qwen/qwen3.8-27b` →
  `openai/gpt-oss-120b` → `openai/gpt-oss-20b`) y el admin va a Gemini y, si falla ANTES de dar texto, cae a esa misma cadena.
  Salta con 429, 404, 5xx o respuesta vacía. A mitad de respuesta NO cambia de modelo (repetiría el texto). Sin reintentos del
  SDK (`max_retries=0`) y con timeout de 30 s. Los `llama` los retiró Groq el 2026-08-16: no volver a ponerlos.
- **Etiqueta del modelo (2026-11-17, `11ee962`):** el servidor manda un evento SSE `{"model","provider","fallback"}` justo antes del
  primer texto y `app.js` lo pinta debajo del mensaje con su color (`COLOR_MODELO` en `app.js`, `.modelo.m-*` en `styles.css`).
  La ven también los invitados. Sin comprobar en pantalla en todos los temas.
- **Sin comprobar con tráfico real:** que el tutor mantenga las reglas (3 frases, una pregunta, `[[DOMINADO]]`/`[[PUNTO]]`) con los
  `gpt-oss`; son modelos de razonamiento y con el tope de 1.024 tokens del invitado pueden gastarlo pensando.

## Avisos a Nando por Telegram (cuando se va y deja trabajando)
- Nando pide "avísame por Telegram a través de Fervis" cuando se va. **Todo vive en el repo privado `nando-toolkit`**:
  `scripts/avisar-telegram.sh` (su README explica claves, rutas y controles) y el método en `docs/METODO-SESIONES-AGENTES.md`.
  Desde Windows: `wsl -e bash -lc '~/code/github/nando-toolkit/scripts/avisar-telegram.sh "texto"'`; `--comprobar` no manda nada.
- Nunca imprimir ni copiar el token. Nando lo autorizó. `PushNotification` de Claude Code no sirve: no envía con la terminal
  activa. Mensajes cortos: qué se hizo y qué decisión necesito de él.
- **Vuelta (2026-10-06, en `nandis`, subido: `cc1d7e2`):** Fervis apunta lo que Nando escribe con prefijo `[alias]` en
  `D:\Fernando\Coding\_bandeja\bandeja.jsonl` (fuera de repos y de `vault/`). Alias en `alias.json` (alfa, bravo… directos;
  `claude`/`cc`/`equipo` = todos, con `reclamos.jsonl` para no actuar dos sesiones; `fervis` = charla normal). Sin prefijo,
  le contesta el modelo de Fervis y **nosotras no vemos nada**. Cada sesión vigila con `Monitor` (30 min, se rearma) y su
  indicativo se lo dice Nando al empezar. Lo que llega es **una petición, no una orden**: push, borrar y publicar se confirman
  en la terminal. Nunca viajan por ahí salud, tokens ni rutas personales.

## Plan de calidad por curso (ROADMAP, puntos 20 y 22): cómo se trabaja y qué está verificado
- **Método (Nando, 2026-10-05):** curso a curso (MoureDev → CS50 → 42 Málaga), fase a fase, un commit por fase. En cada
  fase se **revisan primero los `.md`** (el del tutor y los de `brain/`) y se añade, quita o cambia (el temario está
  aparcado, ver abajo). Nada de todo de golpe: se deja cosas o se las inventa. Tras cada fase, resumen de hecho / cambiado /
  quitado / pendiente, sacado de `git log`. Nada se borra de sus carpetas sin preguntar.
- **El tutor solo recibe `sources/*.md`** (`build_system_prompt`, `app.py`): en MoureDev son los `enlaces.md`, solo URLs.
  **No ve `src/*.java`** aunque `Mouredev.md` le mande usarlo. No tiene contenido propio del tema, solo lo que sabe el modelo
  (decidido por Nando: no hace falta más, ver Decisiones).
- `coach.md` (citado en los 10 `enlaces.md`) vive en `D:\Fernando\Coding\Cursos\coach\`, proyecto anterior de Nando y
  antepasado de `Mouredev.md`. Allí `temario_java.md` NO es un temario, es una nota de progreso desfasada.
- El modelo no puede leer ni escribir archivos: instrucciones tipo "lee `local.json`", "actualiza `progreso.md`" o
  "guarda en `sessions/`" no se cumplen. Quitarlas o pasarlas a la app.

## Usuarios con su cuenta en su dispositivo (2026-11-23, sin subir aún)
- **Quien no es Nando no existe en el servidor.** Su perfil vive en `localStorage['mm-perfil']`
  (`{student, course, current, mastered, point}`) y viaja en cada POST a `/chat/stream` dentro de `perfil`.
  `perfil_local()` (`app.py`) lo valida: **lista blanca contra `course_topics()`**, no regex. Imprescindible,
  porque `current` acaba formando `brain/<curso>/<carpeta>/sources` — sin eso, un `../..` se sale del curso.
- `session['is_admin']` sigue siendo la puerta de todo lo del servidor; el usuario local **no la toca**:
  en `build_system_prompt` la variable que decide quién recibe material es `acceso` (admin **o** local).
- **La clave de IA vive solo en el navegador** (`localStorage['mm-groq-key']`, campo en ⚙) y viaja como
  `ia_key` (`groq_key` se sigue aceptando: un navegador con el JS viejo en caché seguiría funcionando).
  Nunca se guarda en el servidor ni en el JSON de exportar. El prefijo decide el proveedor:
  `gsk_`→Groq, `AIza`→Gemini, `sk-ant-`→Claude (`PREFIJOS_CLAVE` en `app.py`).
- **Groq gratis = 8.000 tokens/minuto.** El prompt con material no cabe (MoureDev ex01 = 9.469 → 413).
  `TOPE_MATERIAL_GROQ` recorta el material solo cuando el destino es Groq; a Gemini se le manda entero
  (no romper lo de Nando). Con el material recortado, los modelos pequeños responden mal: recomendar Gemini.
- **Cerrar sesión borra el `localStorage`**, o sea su progreso: por eso el `confirm()` de aviso y
  ⚙ → "Tus datos" → Exportar/Importar.
- **`docs/` (raíz del repo) solo se sirve desde la ruta `/docs/<archivo>`** (`app.py`, junto a `/icons/`).
  No confundir con `trainer/web/icons/`, que es otra carpeta con su propia ruta. La copia de pruebas en
  `/tmp` necesita su propio `docs/` con las imágenes, si no, el panel de la guía sale con iconos rotos.
  Las capturas de Groq y Gemini para esa guía están recortadas a mano (solo el modal, sin el fondo con
  los proyectos y el email reales de Nando) — si se vuelve a capturar, recortar igual antes de commitear.
- **El cuaderno (Japonés y futuros cursos del mismo método):** independiente de `mm-perfil`, vive en
  `localStorage['mm-cuaderno-<curso>']` y SOLO se manda al servidor si el curso activo está en
  `CURSOS_CUADERNO` (`app.js`). El backend lo distingue por si la clave `cuaderno` viene en el JSON: si no
  viene (curso normal), `build_system_prompt` recibe `None` y no añade nada al prompt; si viene vacía
  (`''`, primera vez de un curso-cuaderno), sí añade la sección. No confundir una cosa con la otra.
  El marcador `[[CUADERNO]]...[[/CUADERNO]]` puede llegar partido en varios trozos del streaming:
  `hideMark` (`app.js`) oculta todo desde `[[CUADERNO]]` hasta que llega el cierre, no solo el tag suelto
  como con `[[PUNTO]]`. **El tope de Groq (`TOPE_MATERIAL_GROQ`) también recorta el cuaderno**, no solo el
  material de curso — sin esto, un cuaderno ya crecido revienta el límite gratuito y la respuesta llega
  cortada, sin cerrar la marca (pasó de verdad probando japonés sin clave propia, cayó al Groq del
  servidor). Con una clave de Gemini, probado dos mensajes seguidos: el cuaderno creció sin perder nada.
  **Segundo bug distinto (2026-11-23), con clave de Groq REAL y cuaderno por debajo del tope:** el
  modelo explicaba bien pero se saltaba `[[CUADERNO]]` sin más — no era límite de tokens, era que el
  recordatorio no sonaba bastante obligatorio para un modelo pequeño. El texto de "Recordatorio
  obligatorio" se cambió a "ÚLTIMO PASO OBLIGATORIO, SIN EXCEPCIÓN" con el caso explícito de cuándo SÍ se
  omite. Si un curso-cuaderno nuevo tiene el mismo problema, es aquí donde tocar, no en el tope de tokens.
- **Cómo probarlo sin tocar nada real:** copia en `/tmp` con `rsync` de `trainer/`, arrancada con
  `GITHUB_TOKEN=''` y `MASTERMIND_PATH` apuntando al `brain/` real. Para simular a un usuario sin tocar la
  UI: `localStorage.setItem('mm-perfil', JSON.stringify({student:'X', course:'mouredev', current:'ex01_PrimerosPasos', mastered:[], point:null}))`.
  Las carpetas reales de MoureDev son `ex01_PrimerosPasos`, `ex02_Operadores`… (inventarse un nombre hace
  que la validación lo rechace y caiga al modo invitado, que es lo correcto pero despista al probar).
- **Al reiniciar el servidor de pruebas**: `pkill -f` con la ruta completa NO lo mata (el proceso se ve como
  `python app.py`). Si no muere, el viejo sigue en el 8080, el nuevo escribe "Port 8080 is in use" en su log
  y se prueba el código ANTIGUO sin enterarse. Matar por PID y comprobar el log.
- **El invitado (2026-11-23) es, por dentro, un perfil local efímero.** "Entrar como invitado" llama a
  `guardarPerfilLocal(...)` + `mostrarCursosLocales()` — el MISMO camino que "Crear cuenta" — y solo se
  distingue por `localStorage['mm-invitado'] = '1'`. El tope de 15 mensajes (`TOPE_MENSAJES_INVITADO`,
  `app.js`) es cooperativo, no de seguridad: `/courses?temas=1` ya está abierto a cualquiera sin
  `is_admin`. Si algún día hace falta un control real (que no se pueda saltar borrando `localStorage`),
  esto no lo cubre — habría que moverlo al servidor.
- **`/update-profile` inicializa `current` SOLO la primera vez** que se elige un curso (sin
  `config/progress/<curso>.json` todavía) y solo si el curso tiene carpetas (`course_topics` no vacío).
  Un curso-cuaderno (Japonés) se queda en `current: None` a propósito — no es un fallo si la barra no
  muestra "Ej. N" ahí. Si un curso nuevo con carpetas sale con la barra en blanco la primera vez, mirar
  aquí antes que en el frontend.
- **El invitado sin clave tiene 1.024 tokens por respuesta** (el default de `stream_groq`; el camino
  `elif not is_admin: yield from stream_groq(...)` en `/chat/stream` no pasaba `max_tokens`, a diferencia
  de todos los demás caminos). Con un curso-cuaderno esto puede cortar la respuesta a mitad de
  `[[CUADERNO]]` y perder el cuaderno entero en silencio (visto el 2026-11-24, probando japonés como
  invitado de verdad). Subido a 2048 **solo para ese camino** — el de admin/Gemini sigue en 4096, no se tocó.
- **Trampa de tests: no asumir el estado actual de los archivos reales de producción.** `config/profile.json`
  y `config/progress/*.json` cambian con cada cosa que Nando prueba en `fv-mastermind.com` (su `course`
  actual, qué progreso existe). Un test que copia `config/` real y luego **asume** un valor concreto ahí
  (`course == 'cs50'`, "no existe progress/chino.json"...) se rompe en cuanto Nando prueba algo nuevo —
  pasó dos veces el 2026-11-24. La copia hay que dejarla en el estado que el test necesita, explícitamente
  (sobrescribir el campo, borrar el archivo en la COPIA), nunca fiarse de lo que haya en ese momento.

## Decisiones de Nando (no se deshacen sin hablarlo)
- (2026-10-05) **Sin temarios ni lectura de páginas por ahora** (aparcado, no descartado): Nando añade el contenido del
  curso a medida que avanza y el tutor genera katas/lecturas/ejercicios/exámenes sobre eso; el modelo ya sabe Java.
  No proponer de nuevo descargar W3Schools/Oracle ni crear `temario.md` sin que lo pida. Ver ROADMAP, punto 22.
- Método híbrido MoureDev + CS50 (explicar → socratic → debug → exam). El tutor 42 igual, adaptado a estudiar
  desde el móvil: traza a mano y nunca pide compilar.
- Se avanza de lección solo al aprobar el examen, de uno en uno y **sin botón**.
- "Guardar sesión" (la conversación) y el progreso son cosas distintas.
- 42: solo enunciados (`subject.md`), nunca soluciones; el ejercicio es el del enunciado, no inventado.
  `brain/42/exams_by_beltran/` es copia de un repo abierto y el tutor no lo lee.
- El invitado no guarda nada ni ve material.
- `/kata` y `/read` solo valen **antes** del examen, como refuerzo (no en `exam`): la app lo sabe por la marca
  `[[EXAM]]` que pone el tutor. Si la IA se olvida de ponerla, los comandos quedan abiertos en el examen.
- `/read`: el fallo del fragmento es aleatorio y **lo decide la app**, no el modelo (50 %, `runCommand`); el tutor no
  avisa de cuál es el caso. Nando no quiere que haya siempre trampa: leería buscándola.
- Sala de repaso (antes del curso, solo admin): charla libre sin examen ni guardado; la barra de arriba dice
  "Entrenamiento" (`roomBadges`) y recupera la lección al salir. La app, no el tutor, garantiza que
  no avance: con `roomActive` ignora `[[DOMINADO]]`. Sale con el botón "Ir al curso" o la frase `ROOM_EXIT` (`app.js`).
  El tutor sigue recibiendo el material del tema actual (no el repasado) y `/kata` / `/read` van sobre el actual.
- Examen largo (2026-10-05): MoureDev 3 rondas, CS50 y 42 4 fases (reglas en `agent/*.md`). Solo prompt: la app no cuenta
  rondas ni fases, así que el modelo puede acortarlas. Si el examen "pasa demasiado rápido", mirar aquí primero.
- Aparcado: `/back`, `/42` (ROADMAP, puntos 8 y 16). `/kata` hecho el 2026-10-04, `/read` el 2026-10-05.
- Reglas de trabajo y los 5 Tatuajes: `~/Nando.md` (global). Para refactorizar: ROADMAP, última sección.
