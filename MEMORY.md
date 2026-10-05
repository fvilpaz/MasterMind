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
- El archivo del tutor, en minúsculas (`42malaga.md`): Linux distingue mayúsculas, Windows no.
- `course_topics` solo ve carpetas `exN_…` / `weekN…` dentro de la raíz del curso en `brain/`; `COURSE_ROOTS`
  (`app.py`) mapea curso → carpeta. Un curso sin `config/progress/<curso>.json` empieza con `current: None`
  y el tutor no recibe material.
- `Mouredev.md`: "NUEVO — sin sesiones previas" sale en cuanto avanzas a un tema sin log; el tutor debe empezar
  por `current_folder` (que sale del progreso), no por ex1.
- `[[DOMINADO]]` lo escribe el tutor y la app avanza sola: si lo emite sin que haya aprobado, se avanza sin
  vuelta atrás (aún no hay `/back`). Pasó con 42 el 2026-10-02.
- `/update-profile` y `save_progress` no avisan si fallan en GitHub.

## Pomodoro, plan y marcas (cómo funciona)
- Todo en `localStorage`, por navegador: `pomo-state` (`{mode, remaining, endsAt}`; `endsAt` = hora real de fin, 0 si
  está parado) y `pomo-plan` (`{total, done, at}`, caduca a las 4 h). No pasa por el servidor.
- El saludo tiene dos formas: `__greet__` (pregunta el tiempo) y `__greet_plan__` (no lo pregunta, solo admin).
  Los dos en `GREET_TOKENS` (`app.py`). Un token nuevo hay que añadirlo ahí o `is_greet` no lo reconoce.
- Marcas ocultas de la IA: `[[DOMINADO]]` (aprobó: guarda y avanza) y `[[EXAM]]` (está en examen, en cada mensaje).
  `hideMark` (`app.js`) las quita al mostrar, también a medias (`[[EX`).

## Cómo probar en local
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
- Pruebas: `python trainer/tests/test_greet.py` y `python trainer/tests/test_profile.py` (sin dependencias,
  sobre una copia temporal).
- Navegador: MCP `chrome-devtools` (`claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest`),
  un contexto aislado por prueba. Login: nombre → "Tengo contraseña" → contraseña → tarjeta de curso; el
  nombre se recuerda en `localStorage` (`mm-name`).

## Decisiones de Nando (no se deshacen sin hablarlo)
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
- Sala de repaso (antes del curso, solo admin): charla libre sin examen ni guardado. La app, no el tutor, garantiza que
  no avance: con `roomActive` ignora `[[DOMINADO]]`. Sale con el botón "Ir al curso" o la frase `ROOM_EXIT` (`app.js`).
  El tutor sigue recibiendo el material del tema actual (no el repasado) y `/kata` / `/read` van sobre el actual.
- Aparcado: `/back`, `/42` (ROADMAP, puntos 8 y 16). `/kata` hecho el 2026-10-04, `/read` el 2026-10-05.
- Reglas de trabajo y los 5 Tatuajes: `~/Nando.md` (global). Para refactorizar: ROADMAP, última sección.
