from flask import Flask, request, jsonify, send_from_directory, session, Response, stream_with_context
import hashlib, json, os, random, re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'mastermind-dev-key')
ROOT = Path(__file__).parent.parent

GUEST_PROFILE = {
    "student": "invitado",
    "course": "cs50",
    "current_week": 1,
    "current_topic": "",
    "mode": "explain",
    "language": "es",
    "weeks_completed": [],
    "topics_mastered": {"week1": []},
    "notes": ""
}


def github_get(repo_path):
    import urllib.request, base64
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        return None
    api_url = f"https://api.github.com/repos/fvilpaz/MasterMind/contents/{repo_path}"
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
            if isinstance(data, list):
                return data
            return base64.b64decode(data['content']).decode()
    except Exception:
        return None


def get_last_session_log(sessions_folder):
    """`sessions_folder` identifica el curso/tema (ej. 'week4-c' para CS50,
    'Moure_java_ex2_VariablesAndConstants' para MoureDev). Todos los logs viven bajo
    trainer/sessions/<sessions_folder>/, para no ensuciar la raíz de trainer/ con una carpeta por
    tema."""
    token = os.environ.get('GITHUB_TOKEN', '')
    if token:
        entries = github_get(f"trainer/sessions/{sessions_folder}")
        if entries and isinstance(entries, list):
            mds = sorted([e for e in entries if e['name'].endswith('.md')], key=lambda x: x['name'], reverse=True)
            if mds:
                content = github_get(f"trainer/sessions/{sessions_folder}/{mds[0]['name']}")
                if content:
                    return f"\n\n## Última sesión registrada\n{content}"
        return ""
    sessions_dir = ROOT / "sessions" / sessions_folder
    if not sessions_dir.exists():
        return ""
    logs = sorted(sessions_dir.glob("*.md"), reverse=True)
    if not logs:
        return ""
    return f"\n\n## Última sesión registrada\n{logs[0].read_text(encoding='utf-8')}"


def get_admin_profile():
    token = os.environ.get('GITHUB_TOKEN', '')
    if token:
        content = github_get("trainer/config/profile.json")
        if content:
            return json.loads(content)
    return json.loads((ROOT / 'config/profile.json').read_text(encoding='utf-8'))


def _progress_path(course):
    """Ruta (dentro de trainer/) del progreso de un curso. Solo nombres simples: sin esto, un curso
    llamado '../profile' leería o escribiría otro archivo."""
    if not re.fullmatch(r'[a-z0-9_-]+', course or ''):
        raise ValueError(f"Nombre de curso no válido: {course!r}")
    return f'config/progress/{course}.json'


def get_progress(course):
    """Progreso de UN curso ({'current': carpeta, 'mastered': [...]}). Como el perfil: en producción
    vive en GitHub; en local, el archivo. Si el curso aún no tiene archivo, progreso vacío."""
    path = _progress_path(course)
    if os.environ.get('GITHUB_TOKEN', ''):
        content = github_get(f'trainer/{path}')
        if content:
            return json.loads(content)
    local = ROOT / path
    if local.exists():
        return json.loads(local.read_text(encoding='utf-8'))
    return {'current': None, 'mastered': []}


def save_progress(course, progress):
    """Guarda el progreso de UN curso (solo su archivo: nunca toca el de otro curso)."""
    path = _progress_path(course)
    text = json.dumps(progress, indent=2, ensure_ascii=False)
    local = ROOT / path
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_text(text, encoding='utf-8')
    if os.environ.get('GITHUB_TOKEN', ''):
        try:
            github_put(f'trainer/{path}', text, f'update: progress/{course}.json')
        except Exception as e:
            print(f"[WARN] No se pudo sincronizar progress/{course}.json con GitHub: {e}")


def folder_label(folder):
    """Nombre legible de una carpeta de tema: ex1_HelloWorld → 'Hello World', week02-arrays → 'Week 2 · Arrays'."""
    if not folder:
        return ''
    m = re.match(r'ex\d+_(.+)$', folder)
    if m:
        return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', m.group(1))
    m = re.match(r'week(\d+)-(.+)$', folder)
    if m:
        return f"Week {int(m.group(1))} · {m.group(2).replace('-', ' ').title()}"
    return folder


def _brain_path():
    """Carpeta brain/ (misma regla que build_system_prompt: local.json > MASTERMIND_PATH > ../brain)."""
    default_mm = str(ROOT.parent / 'brain')
    local_path = ROOT / 'config/local.json'
    if local_path.exists():
        local = json.loads(local_path.read_text(encoding='utf-8'))
        return Path(local.get('mastermind_path', os.environ.get('MASTERMIND_PATH', default_mm)))
    return Path(os.environ.get('MASTERMIND_PATH', default_mm))


def course_topics(course):
    """Temas del curso en orden, leídos de sus carpetas en brain/ (exN_Tema en MoureDev, weekNN-tema
    en CS50). Ordenados por NÚMERO: alfabéticamente, ex10 iría justo detrás de ex1."""
    root = _brain_path() / COURSE_ROOTS.get(course, course)
    if not root.is_dir():
        return []
    topics = []
    for d in root.iterdir():
        m = re.match(r'(?:ex|week)(\d+)', d.name)
        if d.is_dir() and m:
            topics.append({'folder': d.name, 'n': int(m.group(1)), 'topic': folder_label(d.name).split(' · ')[-1]})
    return sorted(topics, key=lambda t: t['n'])


# Carpeta raíz dentro de brain/ para cada curso, cuando no coincide con el nombre del curso tal cual.
COURSE_ROOTS = {'cs50': 'cs50', 'mouredev': 'Moure/java', '42malaga': '42'}


def _topic_folder(course):
    """Carpeta del tema en curso (dentro de la raíz del curso en brain/), leída SOLO del progreso de ese
    curso. Antes salía del perfil común: current_folder de MoureDev pisaba a CS50, y CS50 inventaba
    'week0N-c', que no existe desde la semana 2 (las carpetas son week02-arrays, week03-algorithms…)."""
    return get_progress(course).get('current')


# El invitado (demo pública de CS50) siempre en la semana 1: no debe seguir el progreso de Nando.
GUEST_TOPIC_FOLDER = 'week01-c'


def build_system_prompt(is_admin=False):
    profile = get_admin_profile() if is_admin else GUEST_PROFILE
    course = profile.get('course', '').lower()
    agent_dir = ROOT / 'agent'
    course_file = None
    for name in [f"{course.upper()}.md", f"{course.capitalize()}.md", f"{course}.md"]:
        candidate = agent_dir / name
        if candidate.exists():
            course_file = candidate
            break
    claude_md = course_file.read_text(encoding='utf-8') if course_file else (agent_dir / 'AGENT.md').read_text(encoding='utf-8')
    local_path = ROOT / 'config/local.json'
    sources_text = ""
    default_mm = str(ROOT.parent / 'brain')
    if local_path.exists():
        local = json.loads(local_path.read_text(encoding='utf-8'))
        mm = Path(local.get('mastermind_path', os.environ.get('MASTERMIND_PATH', default_mm)))
    else:
        mm = Path(os.environ.get('MASTERMIND_PATH', default_mm))
    course_root = COURSE_ROOTS.get(course, course)
    topic_folder = _topic_folder(course) if is_admin else GUEST_TOPIC_FOLDER
    if mm.exists() and topic_folder:
        sources_dir = mm / course_root / topic_folder / "sources"
        if sources_dir.exists():
            parts = []
            for md_file in sorted(sources_dir.glob("*.md")):
                text = md_file.read_text(encoding='utf-8')
                if md_file.name == "transcripcion_video.md":
                    start = text.find("## Source Code")
                    text = text[start if start != -1 else 0:][:15000]
                    label = "Transcripción del vídeo (fuente principal — sigue este orden exacto)"
                elif md_file.name == "lecture_notes.md":
                    text = text[:3000]
                    label = "Lecture notes"
                else:
                    label = md_file.stem.replace("_", " ")
                parts.append(f"\n\n## {label}\n{text}")
            sources_text = "".join(parts)
    if not is_admin:
        sources_text = ""
    session_folder = f"{course_root.replace('/', '_')}_{topic_folder}" if topic_folder else None
    if course == 'cs50' and topic_folder:
        # Compatibilidad exacta con el formato de sesiones ya guardadas de CS50 (trainer/week{N}-c/sessions).
        session_folder = f"week{profile.get('current_week', 1)}-c"
    session_log = get_last_session_log(session_folder) if is_admin and session_folder else ""
    has_sessions = bool(session_log)
    if is_admin and topic_folder:
        # El tema en curso lo manda el progreso: el perfil puede seguir diciendo el ejercicio anterior.
        profile = {**profile, 'current_folder': topic_folder,
                   'current_topic': folder_label(topic_folder).split(' · ')[-1]}
    student_status = (
        "## Estado del estudiante (NUEVO — sin sesiones previas)\n"
        if not has_sessions else
        "## Estado del estudiante\n"
    )
    return (
        f"{claude_md}\n\n"
        f"{student_status}```json\n{json.dumps(profile, indent=2)}\n```"
        f"{sources_text}"
        f"{session_log}"
    )


def call_claude(messages, system):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=messages
    )
    return response.content[0].text


def call_gemini(messages, system, model_name='gemini-flash-latest'):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    history = [
        types.Content(role=m['role'].replace('assistant', 'model'),
                      parts=[types.Part(text=m['content'])])
        for m in messages[:-1]
    ]
    response = client.models.generate_content(
        model=model_name,
        contents=history + [types.Content(role='user', parts=[types.Part(text=messages[-1]['content'])])],
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=4096)
    )
    return response.text


def _resolve_greet(messages, is_admin, guest_name_val):
    if messages and messages[-1]['content'] == '__greet__':
        if is_admin:
            messages[-1]['content'] = GREET_ADMIN
        elif guest_name_val:
            messages[-1]['content'] = GREET_GUEST.replace(
                "llámale 'aprendiz'", f"llámale '{guest_name_val}', que es su nombre real"
            )
        else:
            messages[-1]['content'] = GREET_GUEST
        # Para que el saludo no sea siempre igual: un estilo al azar, AÑADIDO al final
        # (no se toca el texto de GREET_*: el replace de arriba depende de él).
        messages[-1]['content'] += f" Esta vez, arranca {random.choice(GREET_STYLES)}."
    return messages


def stream_claude(messages, system):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {json.dumps(text)}\n\n"


def stream_groq(messages, system, model_name='qwen/qwen3.8-27b'):
    from groq import Groq
    client = Groq(api_key=os.environ['GROQ_API_KEY'])
    groq_messages = [{"role": "system", "content": system}] + [
        {"role": m['role'], "content": m['content']} for m in messages
    ]
    stream = client.chat.completions.create(
        model=model_name,
        messages=groq_messages,
        max_tokens=1024,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield f"data: {json.dumps(delta)}\n\n"


BREVITY_REMINDER = "\n\n(Recuerda: máximo 3 frases. Un concepto. Una pregunta. Sin listas ni subtítulos.)"


def stream_gemini(messages, system, model_name='gemini-flash-latest', max_tokens=4096, is_greet=False):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    history = [
        types.Content(role=m['role'].replace('assistant', 'model'),
                      parts=[types.Part(text=m['content'])])
        for m in messages[:-1]
    ]
    last_content = messages[-1]['content'] if is_greet else messages[-1]['content'] + BREVITY_REMINDER
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=history + [types.Content(role='user', parts=[types.Part(text=last_content)])],
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens)
    ):
        if chunk.text:
            yield f"data: {json.dumps(chunk.text)}\n\n"


@app.route('/')
def index():
    resp = send_from_directory('.', 'index.html')
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return resp


# La interfaz se sirve con 'no-cache': el navegador puede guardarla, pero pregunta SIEMPRE si ha cambiado (si no,
# el servidor contesta 304 y no se descarga nada). Sin esto, el móvil decidía por su cuenta cuánto tiempo usar el
# CSS/JS viejo tras un despliegue.
def _sin_cache(resp):
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/styles.css')
def styles():
    return _sin_cache(send_from_directory('.', 'styles.css'))


@app.route('/app.js')
def app_js():
    return _sin_cache(send_from_directory('.', 'app.js'))


@app.route('/code-editor.js')
def code_editor_js():
    return _sin_cache(send_from_directory('.', 'code-editor.js', mimetype='application/javascript'))


# --- PWA ---
# Mimetypes puestos a mano: en Windows el registro puede mapear .js a text/plain, y el
# navegador rechaza registrar un service worker que no llegue como JavaScript.

@app.route('/manifest.json')
def manifest():
    return _sin_cache(send_from_directory('.', 'manifest.json', mimetype='application/manifest+json'))


# Archivos cuyo contenido decide la versión de la caché del service worker
_ARCHIVOS_INTERFAZ = ('index.html', 'styles.css', 'app.js', 'code-editor.js', 'manifest.json', 'sw.js')


def _version_interfaz():
    """Huella del contenido de la interfaz: cambia sola con cualquier cambio en HTML, CSS o JS. Así ya no hay que
    subir a mano 'mastermind-v3' -> 'v4' en cada despliegue (y si se olvidaba, el móvil seguía con lo viejo)."""
    h = hashlib.sha1()
    for nombre in _ARCHIVOS_INTERFAZ:
        ruta = os.path.join(app.root_path, nombre)
        if os.path.exists(ruta):
            with open(ruta, 'rb') as f:
                h.update(f.read())
    return h.hexdigest()[:12]


@app.route('/sw.js')
def service_worker():
    with open(os.path.join(app.root_path, 'sw.js'), encoding='utf-8') as f:
        codigo = f.read().replace('__VERSION__', _version_interfaz())
    resp = Response(codigo, mimetype='application/javascript')
    # Que el navegador compruebe siempre si hay una versión nueva del service worker
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/icons/<path:filename>')
def icons(filename):
    return send_from_directory('icons', filename)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get('password', '')
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    if password == admin_password:
        session['is_admin'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Contraseña incorrecta'}), 401


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.route('/guest-name', methods=['POST'])
def guest_name():
    name = request.json.get('name', '').strip()
    if name:
        session['guest_name'] = name
    return jsonify({'ok': True})


GREET_ADMIN = (
    "Arranca la sesión con energía. Saluda al estudiante por su nombre, "
    "recuérdale exactamente en qué punto quedamos la última sesión (usa el log), "
    "y pregúntale cuánto tiempo tiene hoy: 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros). "
    "Sé motivador y directo, estilo entrenador personal. Máximo 3 frases."
)

GREET_STYLES = [
    "como un entrenador en el vestuario antes del partido",
    "como un compañero de estudio que se alegra de verte",
    "planteando un mini reto de calentamiento sobre el tema en curso",
    "con una curiosidad breve de programación relacionada con el tema",
    "con un toque de humor ligero, sin pasarte",
]

GREET_GUEST = (
    "Da la bienvenida a un nuevo estudiante que acaba de llegar a CS50. "
    "No uses su nombre — llámale 'aprendiz'. "
    "Dile que empieza desde cero y que vas a guiarle paso a paso. "
    "Pregúntale cuánto tiempo tiene hoy: 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros). "
    "Máximo 3 frases, con energía."
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data['messages']
    model = data.get('model', 'gemini-flash-latest')
    provider = os.environ.get('AI_PROVIDER', 'gemini')
    is_admin = session.get('is_admin', False)
    system = build_system_prompt(is_admin=is_admin)
    messages = _resolve_greet(messages, is_admin, session.get('guest_name', ''))
    try:
        reply = call_claude(messages, system) if provider == 'claude' else call_gemini(messages, system, model)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    messages = data['messages']
    is_admin = session.get('is_admin', False)
    is_greet = messages and messages[-1]['content'] == '__greet__'
    system = build_system_prompt(is_admin=is_admin)
    messages = _resolve_greet(messages, is_admin, session.get('guest_name', ''))

    if not is_admin:
        model = 'gemini-flash-latest'
        max_tokens = 500 if is_greet else 300
    else:
        model = data.get('model', 'gemini-flash-latest')
        max_tokens = 4096

    provider = os.environ.get('AI_PROVIDER', 'gemini')

    def generate():
        try:
            if not is_admin:
                yield from stream_groq(messages, system)
            elif provider == 'claude':
                yield from stream_claude(messages, system)
            else:
                yield from stream_gemini(messages, system, model, max_tokens, is_greet=is_greet)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@app.route('/courses')
def courses():
    if not session.get('is_admin', False):
        return jsonify({'courses': ['cs50']})
    agent_dir = ROOT / 'agent'
    found = []
    for f in sorted(agent_dir.glob('*.md')):
        if f.stem.upper() == 'AGENT':
            continue
        found.append(f.stem.lower())
    return jsonify({'courses': found})


def _progress_view(course, progress):
    """El progreso listo para la barra de arriba: carpeta, número (ex3 → 3, week02 → 2) y tema."""
    current = progress.get('current')
    m = re.match(r'(?:ex|week)(\d+)', current or '')
    return {**progress, 'course': course, 'n': int(m.group(1)) if m else None,
            'topic': folder_label(current).split(' · ')[-1]}   # 'Week 2 · Arrays' → 'Arrays'


@app.route('/profile')
def profile():
    is_admin = session.get('is_admin', False)
    if is_admin:
        p = get_admin_profile()
        course = p.get('course', '').lower()
        return jsonify({**p, 'progress': _progress_view(course, get_progress(course))})
    return jsonify({**GUEST_PROFILE, 'progress': _progress_view('cs50', {'current': GUEST_TOPIC_FOLDER, 'mastered': []})})


@app.route('/progress')
def progress_list():
    """/ls del chat: temas del curso elegido, cada uno 'mastered' (✅), 'current' (👉) o 'locked' (🔒)."""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Solo con contraseña'}), 403
    course = get_admin_profile().get('course', '').lower()
    prog = get_progress(course)
    topics = [{**t, 'status': 'mastered' if t['folder'] in prog.get('mastered', [])
               else 'current' if t['folder'] == prog.get('current') else 'locked'}
              for t in course_topics(course)]
    return jsonify({'course': course, 'topics': topics})


@app.route('/progress/next', methods=['POST'])
def progress_next():
    """Guardar la partida tras aprobar el examen: el tema actual pasa a dominado y el SIGUIENTE a
    actual. Siempre de uno en uno y desde el actual: no acepta un destino (no se puede saltar)."""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Solo con contraseña'}), 403
    course = get_admin_profile().get('course', '').lower()
    prog = get_progress(course)
    folders = [t['folder'] for t in course_topics(course)]
    if prog.get('current') not in folders:
        return jsonify({'error': 'No se reconoce el tema actual'}), 400
    i = folders.index(prog['current'])
    if i == len(folders) - 1:
        return jsonify({'error': 'Ya estás en el último tema del curso'}), 400
    mastered = prog.setdefault('mastered', [])
    if prog['current'] not in mastered:
        mastered.append(prog['current'])
    prog['current'] = folders[i + 1]
    save_progress(course, prog)
    return jsonify({'ok': True, 'progress': _progress_view(course, prog)})


def github_put(repo_path, content_str, commit_msg):
    import urllib.request, base64
    token = os.environ.get('GITHUB_TOKEN', '')
    repo = 'fvilpaz/MasterMind'
    api_url = f"https://api.github.com/repos/{repo}/contents/{repo_path}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json'
    }
    encoded = base64.b64encode(content_str.encode()).decode()
    sha = None
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read())['sha']
    except Exception:
        pass
    body = {'message': commit_msg, 'content': encoded}
    if sha:
        body['sha'] = sha
    req = urllib.request.Request(api_url, data=json.dumps(body).encode(), headers=headers, method='PUT')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


@app.route('/save-session', methods=['POST'])
def save_session():
    if not session.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    data = request.json
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Contenido vacío'}), 400
    profile = get_admin_profile()
    course = profile.get('course', '').lower()
    topic_folder = _topic_folder(course)
    session_folder = f"week{profile.get('current_week', 1)}-c" if course == 'cs50' and topic_folder \
        else (f"{COURSE_ROOTS.get(course, course).replace('/', '_')}_{topic_folder}" if topic_folder else 'sesiones_sueltas')
    import datetime
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M')
    topic = profile.get('current_topic', 'sesion').replace(' ', '_').replace(',', '') or 'sesion'
    filename = f"{timestamp}_{topic}.md"
    local_dir = ROOT / "sessions" / session_folder
    local_dir.mkdir(parents=True, exist_ok=True)
    (local_dir / filename).write_text(content, encoding="utf-8")
    if os.environ.get('GITHUB_TOKEN', ''):
        try:
            github_put(f"trainer/sessions/{session_folder}/{filename}", content, f"session: {filename}")
        except Exception as e:
            print(f"[WARN] No se pudo sincronizar la sesión con GitHub: {e}")
    return jsonify({'ok': True})


@app.route('/update-profile', methods=['POST'])
def update_profile():
    if not session.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    data = request.json
    profile_path = ROOT / 'config/profile.json'
    # El perfil de verdad: en producción vive en GitHub (el archivo local es la copia de la imagen, vieja).
    # Antes se leía el archivo local y, al elegir curso, se subía encima → se perdía la partida guardada.
    profile = get_admin_profile()
    allowed = {'course', 'current_topic', 'current_week', 'mode', 'topics_mastered', 'weeks_completed', 'notes'}
    for key, value in data.items():
        if key in allowed:
            profile[key] = value
    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding='utf-8')
    if os.environ.get('GITHUB_TOKEN', ''):
        try:
            github_put('trainer/config/profile.json', json.dumps(profile, indent=2, ensure_ascii=False), 'update: profile.json')
        except Exception as e:
            # El guardado local ya se hizo bien; que falle la sincronización con GitHub (sin
            # token, o sin red) no debe tumbar la petición entera.
            print(f"[WARN] No se pudo sincronizar profile.json con GitHub: {e}")
    return jsonify({'ok': True, 'profile': profile})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
