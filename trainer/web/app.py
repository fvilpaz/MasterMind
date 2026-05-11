from flask import Flask, request, jsonify, send_from_directory
import json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.')
ROOT = Path(__file__).parent.parent


def get_last_session_log(current_week):
    sessions_dir = ROOT / f"week{current_week}-c/sessions"
    if not sessions_dir.exists():
        return ""
    logs = sorted(sessions_dir.glob("*.md"), reverse=True)
    if not logs:
        return ""
    return f"\n\n## Última sesión registrada\n{logs[0].read_text()}"


def build_system_prompt():
    claude_md = (ROOT / 'CLAUDE.md').read_text()
    profile = json.loads((ROOT / 'config/profile.json').read_text())
    local_path = ROOT / 'config/local.json'
    topic_notes = ""
    if local_path.exists():
        local = json.loads(local_path.read_text())
        mm = Path(local.get('mastermind_path', ''))
        notes_path = mm / f"cs50/week0{profile['current_week']}-c/sources/lecture_notes.md"
        if notes_path.exists():
            topic_notes = f"\n\n## Notas del tema actual\n{notes_path.read_text()[:3000]}"
    session_log = get_last_session_log(profile['current_week'])
    return (
        f"{claude_md}\n\n"
        f"## Estado del estudiante\n```json\n{json.dumps(profile, indent=2)}\n```"
        f"{topic_notes}"
        f"{session_log}"
    )


def call_claude(messages, system):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
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
        config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=1024)
    )
    return response.text


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


GREET_PROMPT = (
    "Arranca la sesión con energía. Saluda al estudiante por su nombre, "
    "recuérdale exactamente en qué punto quedamos la última sesión (usa el log), "
    "y pregúntale cuánto tiempo tiene hoy: 1 hora (2 pomodoros), hora y media (3 pomodoros) o 2 horas (4 pomodoros). "
    "Sé motivador y directo, estilo entrenador personal. Máximo 3 frases."
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data['messages']
    model = data.get('model', 'gemini-2.5-flash')
    provider = os.environ.get('AI_PROVIDER', 'claude')
    system = build_system_prompt()
    if messages and messages[-1]['content'] == '__greet__':
        messages[-1]['content'] = GREET_PROMPT
    try:
        reply = call_claude(messages, system) if provider == 'claude' else call_gemini(messages, system, model)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/profile')
def profile():
    return jsonify(json.loads((ROOT / 'config/profile.json').read_text()))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
