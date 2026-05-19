from flask import Flask, request, jsonify, send_from_directory, session, Response, stream_with_context
import json, os
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


def get_last_session_log(current_week):
    token = os.environ.get('GITHUB_TOKEN', '')
    if token:
        entries = github_get(f"trainer/week{current_week}-c/sessions")
        if entries and isinstance(entries, list):
            mds = sorted([e for e in entries if e['name'].endswith('.md')], key=lambda x: x['name'], reverse=True)
            if mds:
                content = github_get(f"trainer/week{current_week}-c/sessions/{mds[0]['name']}")
                if content:
                    return f"\n\n## Última sesión registrada\n{content}"
        return ""
    sessions_dir = ROOT / f"week{current_week}-c/sessions"
    if not sessions_dir.exists():
        return ""
    logs = sorted(sessions_dir.glob("*.md"), reverse=True)
    if not logs:
        return ""
    return f"\n\n## Última sesión registrada\n{logs[0].read_text()}"


def get_admin_profile():
    token = os.environ.get('GITHUB_TOKEN', '')
    if token:
        content = github_get("trainer/config/profile.json")
        if content:
            return json.loads(content)
    return json.loads((ROOT / 'config/profile.json').read_text())


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
    claude_md = course_file.read_text() if course_file else (agent_dir / 'AGENT.md').read_text()
    local_path = ROOT / 'config/local.json'
    topic_notes = ""
    transcription = ""
    default_mm = str(ROOT.parent / 'brain')
    if local_path.exists():
        local = json.loads(local_path.read_text())
        mm = Path(local.get('mastermind_path', os.environ.get('MASTERMIND_PATH', default_mm)))
    else:
        mm = Path(os.environ.get('MASTERMIND_PATH', default_mm))
    if mm.exists():
        week_dir = mm / f"cs50/week0{profile['current_week']}-c"
        notes_path = week_dir / "sources/lecture_notes.md"
        trans_path = week_dir / "sources/transcripcion_video.md"
        if trans_path.exists():
            trans_text = trans_path.read_text()
            start = trans_text.find("## Source Code")
            if start == -1:
                start = 0
            transcription = f"\n\n## Transcripción del vídeo (fuente principal — sigue este orden exacto)\n{trans_text[start:start+15000]}"
        if notes_path.exists():
            topic_notes = f"\n\n## Lecture notes\n{notes_path.read_text()[:3000]}"
    session_log = get_last_session_log(profile['current_week']) if is_admin else ""
    has_sessions = bool(session_log)
    student_status = (
        "## Estado del estudiante (NUEVO — sin sesiones previas)\n"
        if not has_sessions else
        "## Estado del estudiante\n"
    )
    return (
        f"{claude_md}\n\n"
        f"{student_status}```json\n{json.dumps(profile, indent=2)}\n```"
        f"{transcription}"
        f"{topic_notes}"
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


def call_gemini(messages, system, model_name='gemini-2.5-flash'):
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


BREVITY_REMINDER = "\n\n(Recuerda: máximo 3 frases. Un concepto. Una pregunta. Sin listas ni subtítulos.)"


def stream_gemini(messages, system, model_name='gemini-2.5-flash', max_tokens=4096, is_greet=False):
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
    model = data.get('model', 'gemini-2.5-flash')
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
        model = 'gemini-2.5-flash'
        max_tokens = 500 if is_greet else 300
    else:
        model = data.get('model', 'gemini-2.5-flash')
        max_tokens = 4096

    provider = os.environ.get('AI_PROVIDER', 'gemini')

    def generate():
        try:
            if provider == 'claude':
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


@app.route('/profile')
def profile():
    is_admin = session.get('is_admin', False)
    if is_admin:
        return jsonify(get_admin_profile())
    return jsonify(GUEST_PROFILE)


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
    week = profile.get('current_week', 1)
    import datetime
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M')
    topic = profile.get('current_topic', 'sesion').replace(' ', '_').replace(',', '') or 'sesion'
    filename = f"{timestamp}_{topic}.md"
    repo_path = f"trainer/week{week}-c/sessions/{filename}"
    try:
        github_put(repo_path, content, f"session: {filename}")
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update-profile', methods=['POST'])
def update_profile():
    if not session.get('is_admin', False):
        return jsonify({'error': 'No autorizado'}), 403
    data = request.json
    profile_path = ROOT / 'config/profile.json'
    profile = json.loads(profile_path.read_text())
    allowed = {'current_topic', 'current_week', 'mode', 'topics_mastered', 'weeks_completed', 'notes'}
    for key, value in data.items():
        if key in allowed:
            profile[key] = value
    profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    try:
        github_put('trainer/config/profile.json', json.dumps(profile, indent=2, ensure_ascii=False), 'update: profile.json')
        return jsonify({'ok': True, 'profile': profile})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
