from flask import Flask, request, jsonify, send_from_directory, session, Response, stream_with_context
import hashlib, json, os, random, re
from concurrent.futures import ThreadPoolExecutor
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


def perfil_local(datos):
    """Perfil de un usuario cuyos datos viven en SU navegador (no en el servidor): llega en cada petición.

    Todo lo que viene de aquí es NO CONFIABLE: `current` acaba en una ruta de disco
    (`brain/<curso>/<carpeta>/sources`), así que curso y carpeta se validan contra lo que existe de verdad
    —lista blanca, no regex— o un '../..' se saldría de la carpeta del curso. Devuelve None si no cuela."""
    if not isinstance(datos, dict):
        return None
    curso = str(datos.get('course', '')).lower()
    if curso not in _cursos_disponibles():
        return None
    carpeta = datos.get('current')
    if carpeta is not None and carpeta not in [t['folder'] for t in course_topics(curso)]:
        return None
    dominados = datos.get('mastered')
    dominados = [d for d in dominados if isinstance(d, str)][:200] if isinstance(dominados, list) else []
    punto = str(datos.get('point', ''))[:10] if datos.get('point') else None
    # El nombre va dentro del prompt: una línea y corto, para que no reescriba la sección del estudiante.
    nombre = ' '.join(str(datos.get('student', '')).split())[:40] or 'aprendiz'
    return {'student': nombre, 'course': curso, 'current': carpeta, 'mastered': dominados, 'point': punto}


# Groq en su capa gratuita topa en 8.000 tokens/minuto y el prompt entero (tutor + material del tema) no
# cabe: medido el 2026-11-23, MoureDev ex01 pedía 9.469 y daba 413. Con el material recortado sí entra, y
# el tutor sigue sabiendo del tema por sí mismo (decisión de Nando del 2026-10-05: el modelo ya sabe Java).
TOPE_MATERIAL_GROQ = 4000


CUADERNO_TOPE = 20000  # un cuaderno que no para de crecer, por si alguien lo deja volar varias sesiones


def build_system_prompt(is_admin=False, local=None, tope_material=None, cuaderno=''):
    """`local` = perfil de un usuario con sus datos en su navegador (ya validado por `perfil_local`).
    Tiene el mismo acceso al material que el admin, pero nada suyo se lee ni se guarda en el servidor.
    `tope_material` recorta las fuentes para los modelos con poco margen (ver TOPE_MATERIAL_GROQ).
    `cuaderno` = el documento que el tutor va construyendo con el alumno (p. ej. Japonés) y que vive en
    SU navegador, no en el servidor: viaja en cada petición y vuelve completo en la respuesta."""
    acceso = is_admin or local is not None      # quién recibe material del curso (el invitado no)
    if local:
        profile = {'student': local['student'], 'course': local['course'], 'mode': 'explain', 'language': 'es'}
    else:
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
    if local:
        prog = {'current': local['current'], 'mastered': local['mastered'], 'point': local['point']}
    else:
        prog = get_progress(course) if is_admin else {}    # una sola lectura: carpeta actual y punto de dentro
    topic_folder = prog.get('current') if acceso else GUEST_TOPIC_FOLDER
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
    if not acceso:
        sources_text = ""
    elif tope_material and len(sources_text) > tope_material:
        sources_text = (sources_text[:tope_material] +
                        "\n\n(Material recortado por el límite del modelo: continúa con lo que sabes del tema.)")
    session_folder = f"{course_root.replace('/', '_')}_{topic_folder}" if topic_folder else None
    if course == 'cs50' and topic_folder:
        # Compatibilidad exacta con el formato de sesiones ya guardadas de CS50 (trainer/week{N}-c/sessions).
        session_folder = f"week{profile.get('current_week', 1)}-c"
    session_log = get_last_session_log(session_folder) if is_admin and session_folder else ""
    has_sessions = bool(session_log)
    if acceso and topic_folder:
        # El tema en curso lo manda el progreso: el perfil puede seguir diciendo el ejercicio anterior.
        profile = {**profile, 'current_folder': topic_folder,
                   'current_topic': folder_label(topic_folder).split(' · ')[-1]}
    student_status = (
        "## Estado del estudiante (NUEVO — sin sesiones previas)\n"
        if not has_sessions else
        "## Estado del estudiante\n"
    )
    point_text = (f"\n\n## Dónde va dentro de la sección\nÚltima marca guardada: `[[PUNTO {prog['point']}]]`. "
                  "Sigue desde ahí (lo siguiente a esa marca), sin repetir lo ya visto salvo una pregunta rápida de repaso."
                  if prog.get('point') else "")
    # Recordatorio AL FINAL (lo último que lee el modelo): sin él, se saltaba la marca. Solo en cursos con temario.
    con_temario = bool(acceso and topic_folder and (mm / course_root / topic_folder / 'sources' / 'temario.md').exists())
    mark_text = ("\n\n## Recordatorio obligatorio: marca de progreso\nTermina SIEMPRE, en todos tus mensajes, con una "
                 "línea sola `[[PUNTO p.s]]` con lo último YA superado según la regla de arriba (p. ej. `[[PUNTO 1.7]]`), "
                 "aunque no haya cambiado desde el mensaje anterior. Sin ella, el avance se pierde al cerrar.") \
        if con_temario else ""
    # `cuaderno` no None: el curso lleva su documento en el navegador del alumno (ver `agent/Japones.md`).
    # Viaja completo en cada petición porque el servidor no lo guarda: si el tutor no lo reescribe entero,
    # la app no tiene de dónde sacar lo que faltó (es justo lo que le pasó a Nando probándolo él mismo).
    # Con `tope_material` (destino Groq) también se recorta: un cuaderno ya crecido + el prompt del tutor
    # no cabían en el límite gratuito de Groq y la respuesta llegaba cortada, sin cerrar la marca
    # (encontrado el 2026-11-23 probando japonés sin clave propia: cayó al Groq del servidor y reventó).
    tope_cuaderno = tope_material or CUADERNO_TOPE
    cuaderno_text = "" if cuaderno is None else (
        f"\n\n## Tu cuaderno hasta ahora\n{(cuaderno or '(vacío: es la primera entrada)')[:tope_cuaderno]}"
        "\n\n## ÚLTIMO PASO OBLIGATORIO, SIN EXCEPCIÓN: la marca del cuaderno\nAcabas de explicar o descifrar "
        "algo en este mensaje. Antes de darlo por terminado, añádelo al cuaderno de arriba y escribe el "
        "cuaderno COMPLETO (todo lo de arriba + lo nuevo, nunca un resumen, nunca solo la fila añadida) entre "
        "`[[CUADERNO]]` y `[[/CUADERNO]]`, como última línea del mensaje. Esto no es opcional ni algo que "
        "hacer 'cuando convenga': es el último paso de CADA respuesta en la que expliques, descifres o "
        "corrijas algo nuevo. Solo lo omites si tu mensaje no añade nada nuevo al cuaderno (p. ej. solo "
        "preguntas o saludas)."
    )
    return (
        f"{claude_md}\n\n"
        f"{student_status}```json\n{json.dumps(profile, indent=2)}\n```"
        f"{point_text}"
        f"{sources_text}"
        f"{session_log}"
        f"{mark_text}"
        f"{cuaderno_text}"
    )


GREET_TOKENS = ('__greet__', '__greet_plan__')   # lo que manda el navegador; '_plan' = ya hay un plan de pomodoros en marcha


def _resolve_greet(messages, is_admin, guest_name_val):
    if messages and messages[-1]['content'] in GREET_TOKENS:
        if is_admin:
            messages[-1]['content'] = GREET_ADMIN_PLAN if messages[-1]['content'] == '__greet_plan__' else GREET_ADMIN
        elif guest_name_val:
            messages[-1]['content'] = GREET_GUEST.replace(
                "llámale 'aprendiz'", f"llámale '{guest_name_val}', que es su nombre real"
            )
        else:
            messages[-1]['content'] = GREET_GUEST
        # Para que el saludo no sea siempre igual: un estilo al azar, AÑADIDO al final
        # (no se toca el texto de GREET_*: el replace de arriba depende de él).
        messages[-1]['content'] += f" Esta vez, arranca {random.choice(GREET_STYLES)}."
    return _resolve_start(messages)


START_MARK = '__start__'   # el navegador lo pega a la respuesta con el tiempo (tras el saludo que escribe la app)


def _resolve_start(messages):
    """Arranque de la clase: la respuesta con el tiempo lleva START_MARK. En el ÚLTIMO mensaje se cambia por la
    instrucción (con un estilo al azar); en el historial se quita, para no repetir el arranque en cada respuesta."""
    for i, m in enumerate(messages):
        if m.get('role') == 'user' and START_MARK in m.get('content', ''):
            texto = m['content'].replace(START_MARK, '').strip()
            if i == len(messages) - 1:
                texto += ("\n\n(Instrucción de la app, el estudiante no la ve: acaba de decirte su tiempo; es el arranque "
                          "de la clase. Confirma el plan de pomodoros y preséntale en una o dos frases el tema que vais a "
                          f"trabajar {random.choice(GREET_STYLES)}. Luego sigue DONDE LO DEJÓ: si arriba hay una marca "
                          "de punto guardada o una sesión registrada, continúa desde ahí (con una pregunta rápida de "
                          "repaso de lo último), sin repetir lo ya visto; solo si no hay nada, empieza por el primer subpunto.)")
            messages[i] = {**m, 'content': texto}
    return messages


def stream_claude(messages, system, api_key='', max_tokens=4096):
    import anthropic
    modelo = "claude-sonnet-4-6"
    client = anthropic.Anthropic(api_key=(api_key or '').strip() or os.environ['ANTHROPIC_API_KEY'])
    with client.messages.stream(
        model=modelo,
        max_tokens=max_tokens,
        system=system,
        messages=messages
    ) as stream:
        mostrado = False
        for text in stream.text_stream:
            if not mostrado:
                mostrado = True
                yield _evento_modelo('claude', modelo)
            yield f"data: {json.dumps(text)}\n\n"


# Cadena de Groq, en orden. Cada modelo tiene su propia cuota en Groq, así que un 429 en uno no
# bloquea a los demás. qwen3.8 está en Preview (puede retirarse sin aviso: un 404 cae al siguiente);
# los gpt-oss son de producción. Los llama (3.3-70b, 3.1-8b) los retiró Groq el 2026-08-16.
GROQ_MODELS = ['qwen/qwen3.8-27b', 'openai/gpt-oss-120b', 'openai/gpt-oss-20b']


def _evento_modelo(proveedor, modelo, respaldo=False):
    """Evento SSE que dice al navegador qué modelo está respondiendo (la etiqueta de debajo del mensaje).
    Se manda justo antes del PRIMER texto, nunca antes: así un modelo que falla sin dar texto no deja etiqueta."""
    return f"data: {json.dumps({'model': modelo, 'provider': proveedor, 'fallback': respaldo})}\n\n"


def _clave_groq(clave_usuario=''):
    """La clave que trae el usuario manda sobre la del servidor: quien pone la suya gasta SU cuota.
    Nunca se guarda ni se escribe en ningún archivo (repo público), solo vive en la petición."""
    return (clave_usuario or '').strip() or os.environ['GROQ_API_KEY']


# De qué servicio es una clave, por su prefijo. Groq gratis topa en 8.000 tokens/minuto y el prompt con
# material no cabe: por eso interesa que el usuario pueda traer también una de Gemini o Claude.
PREFIJOS_CLAVE = (('gsk_', 'groq'), ('sk-ant-', 'claude'), ('AIza', 'gemini'))


def proveedor_de_clave(clave):
    """'groq' | 'claude' | 'gemini', o None si no se reconoce (mejor avisar que fallar de forma rara)."""
    clave = (clave or '').strip()
    for prefijo, proveedor in PREFIJOS_CLAVE:
        if clave.startswith(prefijo):
            return proveedor
    return None


def stream_groq(messages, system, model_name=None, max_tokens=1024, respaldo=False, api_key=''):
    """Responde con Groq y, si un modelo falla ANTES de dar texto (429, 404, 5xx, respuesta vacía),
    prueba el siguiente de GROQ_MODELS. Si falla a mitad de respuesta no cambia de modelo: el alumno
    ya ha visto texto y el siguiente modelo lo repetiría desde cero."""
    from groq import Groq
    # max_retries=0: el SDK reintenta con espera ante un 429; una cuota agotada no se arregla en
    # segundos y aquí ya hay respaldo entre modelos.
    client = Groq(api_key=_clave_groq(api_key), max_retries=0, timeout=30)
    groq_messages = [{"role": "system", "content": system}] + [
        {"role": m['role'], "content": m['content']} for m in messages
    ]
    primero = model_name or GROQ_MODELS[0]
    cadena = [primero] + [m for m in GROQ_MODELS if m != primero]
    ultimo_error = None
    for modelo in cadena:
        empezo = False
        try:
            stream = client.chat.completions.create(
                model=modelo,
                messages=groq_messages,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    if not empezo:
                        yield _evento_modelo('groq', modelo, respaldo or modelo != cadena[0])
                    empezo = True
                    yield f"data: {json.dumps(delta)}\n\n"
            if empezo:
                return
            ultimo_error = RuntimeError(f'{modelo}: respuesta vacía')
        except Exception as e:
            if empezo:
                raise
            ultimo_error = e
        print(f"[Groq] {modelo} no disponible ({type(ultimo_error).__name__}): pruebo el siguiente")
    raise ultimo_error


BREVITY_REMINDER = "\n\n(Recuerda: máximo 3 frases. Un concepto. Una pregunta. Sin listas ni subtítulos.)"


def con_brevedad(messages, is_greet):
    """Mismo recordatorio que `stream_gemini` ya le mete siempre al último mensaje (ver BREVITY_REMINDER),
    pero para Groq: sin él, un ciclo largo en un solo turno (explicar + varios ejemplos + ejercicios,
    p. ej. Chino) se come el tope de tokens y se corta a media frase, sin aviso."""
    if is_greet or not messages:
        return messages
    return messages[:-1] + [{**messages[-1], 'content': messages[-1]['content'] + BREVITY_REMINDER}]


def stream_gemini(messages, system, model_name='gemini-flash-latest', max_tokens=4096, is_greet=False, api_key=''):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=(api_key or '').strip() or os.environ['GEMINI_API_KEY'],
                          http_options=types.HttpOptions(api_version='v1beta'))
    history = [
        types.Content(role=m['role'].replace('assistant', 'model'),
                      parts=[types.Part(text=m['content'])])
        for m in messages[:-1]
    ]
    last_content = messages[-1]['content'] if is_greet else messages[-1]['content'] + BREVITY_REMINDER
    mostrado = False
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=history + [types.Content(role='user', parts=[types.Part(text=last_content)])],
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=max_tokens)
    ):
        if chunk.text:
            if not mostrado:
                mostrado = True
                # model_version trae el modelo real detrás del alias -latest; si falta, el alias.
                yield _evento_modelo('gemini', getattr(chunk, 'model_version', None) or model_name)
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


@app.route('/dashboard.js')
def dashboard_js():
    return _sin_cache(send_from_directory('.', 'dashboard.js', mimetype='application/javascript'))


@app.route('/dashboard.css')
def dashboard_css():
    return _sin_cache(send_from_directory('.', 'dashboard.css', mimetype='text/css'))


# --- PWA ---
# Mimetypes puestos a mano: en Windows el registro puede mapear .js a text/plain, y el
# navegador rechaza registrar un service worker que no llegue como JavaScript.

@app.route('/manifest.json')
def manifest():
    return _sin_cache(send_from_directory('.', 'manifest.json', mimetype='application/manifest+json'))


# Archivos cuyo contenido decide la versión de la caché del service worker
_ARCHIVOS_INTERFAZ = ('index.html', 'styles.css', 'app.js', 'code-editor.js', 'dashboard.js', 'dashboard.css',
                      'manifest.json', 'sw.js')


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


@app.route('/docs/<path:filename>')
def docs(filename):
    return send_from_directory(ROOT.parent / 'docs', filename)


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
    """SIN USAR desde el 2026-11-23: el invitado ahora lleva su nombre en su perfil local (`student`) y
    recibe el saludo con nombre por esa vía. Se conserva porque es la única forma de alimentar la rama
    con nombre de `_resolve_greet` (probada en `test_greet.py`): borrarla sería tirar comportamiento que
    funciona. Si algún día se quita, hay que quitar también esa rama y sus pruebas."""
    name = request.json.get('name', '').strip()
    if name:
        session['guest_name'] = name
    return jsonify({'ok': True})


GREET_ADMIN = (
    "Arranca la sesión con energía. Saluda al estudiante por su nombre, "
    "recuérdale exactamente en qué punto quedamos la última sesión (usa el log), "
    "y pregúntale cuánto tiempo tiene hoy: 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros). "
    "Sé motivador y directo, estilo entrenador personal. Máximo 3 frases. "
    "La pregunta del tiempo es la ÚNICA pregunta de este mensaje: ni retos, ni ejercicios, ni explicaciones todavía; "
    "la clase empieza cuando responda."
)

# Mismo arranque, pero el estudiante ya tiene un plan de pomodoros en marcha: no se le vuelve a preguntar el tiempo.
GREET_ADMIN_PLAN = (
    "Estás empezando un tema nuevo dentro de una sesión que ya está en marcha. Saluda al estudiante por su nombre, "
    "dile en una frase de qué va el tema nuevo y lánzale directamente el primer paso del método. "
    "NO le preguntes cuánto tiempo tiene: ya tiene un plan de pomodoros en marcha. "
    "Sé motivador y directo, estilo entrenador personal. Máximo 3 frases."
)

GREET_STYLES = [
    "como un entrenador en el vestuario antes del partido",
    "como un compañero de estudio que se alegra de verte",
    "anunciando el reto que os espera en el tema en curso, sin plantearlo todavía",
    "con una curiosidad breve de programación relacionada con el tema, contada en una frase y sin preguntar nada",
    "con un toque de humor ligero, sin pasarte",
]

GREET_GUEST = (
    "Da la bienvenida a un nuevo estudiante que acaba de llegar a CS50. "
    "No uses su nombre — llámale 'aprendiz'. "
    "Dile que empieza desde cero y que vas a guiarle paso a paso. "
    "Pregúntale cuánto tiempo tiene hoy: 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros). "
    "Máximo 3 frases, con energía. "
    "La pregunta del tiempo es la ÚNICA pregunta de este mensaje: ni retos ni ejercicios todavía."
)

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    messages = data['messages']
    is_admin = session.get('is_admin', False)
    is_greet = messages and messages[-1]['content'] in GREET_TOKENS
    # Usuario con sus datos en su navegador: el perfil viaja en la petición, el servidor no guarda nada suyo.
    local = None if is_admin else perfil_local(data.get('perfil'))

    # Clave del propio usuario (la pega en ⚙ o al crear su cuenta): no se guarda en el servidor, viaja
    # en la petición. Puede ser de Groq, Gemini o Claude; el prefijo dice cuál. `groq_key` es el nombre
    # viejo del campo: se acepta para que un navegador con el JS en caché siga funcionando.
    clave_usuario = (data.get('ia_key') or data.get('groq_key') or '').strip()
    proveedor_usuario = proveedor_de_clave(clave_usuario)

    # Hay que saber a qué modelo va ANTES de construir el prompt: a Groq hay que mandarle menos material.
    destino = proveedor_usuario or ('groq' if not is_admin else os.environ.get('AI_PROVIDER', 'gemini'))
    # Cuaderno del curso (Japonés): solo viaja si el front lo manda (cursos que lo usan). Clave presente
    # pero vacía = cuaderno recién empezado; clave ausente = este curso no usa cuaderno.
    cuaderno = data.get('cuaderno')
    if isinstance(cuaderno, str):
        cuaderno = cuaderno[:CUADERNO_TOPE]
    else:
        cuaderno = None
    system = build_system_prompt(is_admin=is_admin, local=local, cuaderno=cuaderno,
                                 tope_material=TOPE_MATERIAL_GROQ if destino == 'groq' else None)
    messages = _resolve_greet(messages, is_admin or local is not None, session.get('guest_name', ''))

    if not is_admin and not clave_usuario:
        model = 'gemini-flash-latest'
        max_tokens = 500 if is_greet else 300
    else:
        model = data.get('model', 'gemini-flash-latest')
        max_tokens = 4096

    provider = os.environ.get('AI_PROVIDER', 'gemini')

    def generate():
        try:
            if clave_usuario and not proveedor_usuario:
                yield f"data: {json.dumps({'error': 'Esa clave no parece de Groq (gsk_…), Gemini (AIza…) ni Claude (sk-ant-…). Revísala en ⚙.'})}\n\n"
            elif proveedor_usuario == 'groq':
                # Quien trae su clave gasta SU cuota: no se toca ninguna clave del servidor.
                yield from stream_groq(con_brevedad(messages, is_greet), system, max_tokens=max_tokens, api_key=clave_usuario)
            elif proveedor_usuario == 'gemini':
                yield from stream_gemini(messages, system, model, max_tokens, is_greet=is_greet, api_key=clave_usuario)
            elif proveedor_usuario == 'claude':
                yield from stream_claude(messages, system, api_key=clave_usuario, max_tokens=max_tokens)
            elif not is_admin:
                # 2048, no el default (1024): con un curso-cuaderno (Japonés) la respuesta + la marca
                # [[CUADERNO]] no cabían y se cortaba a mitad de la marca, perdiendo el cuaderno entero
                # (visto en vivo el 2026-11-23, probando el invitado tal cual lo usaría alguien real).
                # `con_brevedad`: a Gemini SIEMPRE se le pide esto (ver BREVITY_REMINDER) pero a Groq no
                # se le pedía nunca — un ciclo largo (p. ej. Chino: explicar + varios ejemplos + ejercicios
                # en un solo turno, ver agent/Chino.md) se comía el tope igual y se cortaba a media frase,
                # sin aviso (visto el 2026-11-24, probando chino de invitado sin clave).
                yield from stream_groq(con_brevedad(messages, is_greet), system, max_tokens=2048)
            elif provider == 'claude':
                yield from stream_claude(messages, system)
            else:
                empezo = False
                try:
                    for pieza in stream_gemini(messages, system, model, max_tokens, is_greet=is_greet):
                        empezo = True
                        yield pieza
                except Exception as e_gemini:
                    # Si Gemini falla antes de dar texto (404, cuota, caída), responde Groq; a mitad
                    # de respuesta no se cambia de modelo.
                    if empezo:
                        raise
                    print(f"[Gemini] {model} falló ({type(e_gemini).__name__}): respondo con Groq")
                    yield from stream_groq(messages, system, max_tokens=max_tokens, respaldo=True)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


def _cursos_disponibles():
    """Cursos reales = un .md por curso en agent/ (AGENT.md es el enrutador, no un curso)."""
    found = []
    for f in sorted((ROOT / 'agent').glob('*.md')):
        if f.stem.upper() == 'AGENT':
            continue
        found.append(f.stem.lower())
    return found


@app.route('/courses')
def courses():
    # ?temas=1: cursos con sus temas, para quien lleva su progreso en el navegador (no hay sesión que
    # consultar, así que necesita la lista entera de una vez para elegir curso y saber por dónde empezar).
    if request.args.get('temas'):
        return jsonify({'courses': [{'course': c, 'topics': course_topics(c)} for c in _cursos_disponibles()]})
    if not session.get('is_admin', False):
        return jsonify({'courses': ['cs50']})
    return jsonify({'courses': _cursos_disponibles()})


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


def _resumen_curso(course):
    """Resumen de UN curso para el panel. Solo lee: el progreso y las carpetas de temas de brain/. Un tema
    "dominado" que ya no existe en brain/ no cuenta, así que hechos nunca supera al total."""
    folders = [t['folder'] for t in course_topics(course)]
    prog = get_progress(course)
    hechos = [f for f in folders if f in prog.get('mastered', [])]          # en el orden del curso
    current = prog.get('current')
    i = folders.index(current) if current in folders else None
    siguiente = folders[i + 1] if i is not None and i + 1 < len(folders) else None
    ultimo = hechos[-1] if hechos else None
    return {'course': course, 'done': len(hechos), 'total': len(folders),
            'percent': round(len(hechos) / len(folders) * 100) if folders else 0,
            'finished': bool(folders) and len(hechos) == len(folders),
            'current': current, 'current_label': folder_label(current),
            'last_mastered': ultimo, 'last_mastered_label': folder_label(ultimo),
            'next': siguiente, 'next_label': folder_label(siguiente)}


def _logros(resumenes):
    """Logros del panel, derivados SOLO de los resúmenes (temas dominados y total). Rachas y pomodoros no
    están: no hay un dato fiable de actividad (ver ROADMAP, punto 24)."""
    total_hechos = sum(r['done'] for r in resumenes)

    def mas_cercano(meta):          # el curso que más cerca está de la meta → (progreso, objetivo)
        cand = [(min(r['done'], meta(r)), meta(r)) for r in resumenes if meta(r) > 0]
        return max(cand, key=lambda pn: pn[0] / pn[1]) if cand else (0, 0)

    mitad = mas_cercano(lambda r: (r['total'] + 1) // 2)                    # la mitad, redondeando hacia arriba
    completo = mas_cercano(lambda r: r['total'])
    definidos = [('first_topic', min(total_hechos, 1), 1), ('topics_5', min(total_hechos, 5), 5),
                 ('topics_10', min(total_hechos, 10), 10), ('half_course', *mitad), ('course_complete', *completo),
                 ('all_courses_started', sum(1 for r in resumenes if r['done'] > 0), len(resumenes))]
    return [{'id': i, 'progress': p, 'target': t, 'unlocked': t > 0 and p >= t} for i, p, t in definidos]


@app.route('/dashboard')
def dashboard():
    """Panel de cursos: el resumen de TODOS los cursos a la vez y los logros. Solo con contraseña: el invitado
    no tiene panel. Solo lee, no guarda nada."""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Solo con contraseña'}), 403
    nombres = [c for c in courses().get_json()['courses'] if re.fullmatch(r'[a-z0-9_-]+', c)]
    # Cada curso lee su progreso (en producción, una ida y vuelta a GitHub): a la vez, no uno tras otro. map() conserva
    # el orden de `nombres`; después el último curso usado pasa al principio (ver más abajo).
    # También el último curso usado (perfil), en paralelo con los progresos: así el navegador no pide /profile aparte.
    with ThreadPoolExecutor(max_workers=max(1, min(8, len(nombres) + 1))) as pool:
        perfil = pool.submit(get_admin_profile)
        resumenes = list(pool.map(_resumen_curso, nombres))
        try:
            ultimo = (perfil.result() or {}).get('course', '').lower()
        except Exception:
            ultimo = ''                       # sin perfil legible, el panel sale igual (solo sin la etiqueta "último")
    logros = _logros(resumenes)               # antes de reordenar: ante un empate, `max` se queda con el primero
    if ultimo:
        resumenes.sort(key=lambda r: r['course'] != ultimo)       # sort es estable: el último usado, primero; el resto igual
    return jsonify({'courses': resumenes, 'achievements': logros, 'last_course': ultimo})


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
    prog.pop('point', None)                          # sección nueva: se empieza por su punto 1
    save_progress(course, prog)
    return jsonify({'ok': True, 'progress': _progress_view(course, prog)})


POINT_RE = re.compile(r'^\d+\.(\d+|ejercicios|examen)$')   # '1.5', '1.ejercicios', '1.examen', '2.0'


def _point_key(point):
    """Orden de las marcas dentro de la sección: 1.2 < 1.10 < 1.ejercicios < 1.examen < 2.0."""
    p, s = point.split('.')
    return (int(p), {'ejercicios': 10_000, 'examen': 10_001}.get(s) or int(s))


@app.route('/progress/point', methods=['POST'])
def progress_point():
    """Dónde va DENTRO de la sección (la marca [[PUNTO x.y]] del tutor): así, al volver, sigue por ahí."""
    if not session.get('is_admin', False):
        return jsonify({'error': 'Solo con contraseña'}), 403
    point = str((request.json or {}).get('point', ''))
    if not POINT_RE.match(point):
        return jsonify({'error': 'Punto no válido'}), 400
    course = get_admin_profile().get('course', '').lower()
    prog = get_progress(course)
    old = prog.get('point')
    if old and POINT_RE.match(old) and _point_key(point) <= _point_key(old):
        return jsonify({'ok': True, 'point': old})   # nunca hacia atrás (ni guardar lo mismo otra vez)
    prog['point'] = point
    save_progress(course, prog)
    return jsonify({'ok': True, 'point': point})


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
    # Primera vez que se elige ESTE curso: sin progreso, 'current' queda en None y la barra sale en
    # blanco (visto el 2026-11-23 con chino: primer curso elegido de cero desde que existe este archivo
    # por curso — CS50/MoureDev/42Málaga ya tenían progreso real, por eso nunca se vio). Un curso sin
    # temas (p. ej. Japonés, que no avanza por carpetas) se queda en None a propósito: no hay nada que
    # inicializar ahí.
    curso_elegido = data.get('course')
    if curso_elegido:
        prog = get_progress(curso_elegido)
        if not prog.get('current'):
            temas = course_topics(curso_elegido)
            if temas:
                save_progress(curso_elegido, {'current': temas[0]['folder'], 'mastered': []})
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
