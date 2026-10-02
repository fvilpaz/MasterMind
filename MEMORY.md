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

## Cómo probar en local
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
- Aparcado: `/back`, `/kata`, `/read`, `/42` (ROADMAP, puntos 8 y 16).
- Reglas de trabajo y los 5 Tatuajes: `~/Nando.md` (global). Para refactorizar: ROADMAP, última sección.
