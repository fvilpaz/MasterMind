# Pruebas de la clave de Groq del propio usuario (la que se pega en ⚙): _clave_groq y a qué proveedor
# manda /chat/stream. Lo que fijan: quien trae su clave gasta SU cuota y NO pasa por Gemini.
# Sin red: stream_groq / stream_gemini se sustituyen por espías. Sin dependencias:
#     python trainer/tests/test_groq_key.py
# Código 0 si todo pasa, 1 si algo falla.
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'web'))
os.environ.pop('GITHUB_TOKEN', None)          # nada de GitHub en las pruebas
os.environ['GROQ_API_KEY'] = 'gsk_DEL_SERVIDOR'
import app as mm  # noqa: E402

fallos = 0


def check(nombre, cond):
    global fallos
    print(('✅ ' if cond else '❌ ') + nombre)
    if not cond:
        fallos += 1


# --- 1. _clave_groq: la del usuario manda sobre la del servidor ---
check('sin clave de usuario: usa la del servidor', mm._clave_groq('') == 'gsk_DEL_SERVIDOR')
check('None (el campo no viaja): usa la del servidor', mm._clave_groq(None) == 'gsk_DEL_SERVIDOR')
check('con clave de usuario: manda la suya', mm._clave_groq('gsk_DEL_AMIGO') == 'gsk_DEL_AMIGO')
check('recorta espacios al pegarla', mm._clave_groq('  gsk_DEL_AMIGO  ') == 'gsk_DEL_AMIGO')
check('solo espacios = sin clave', mm._clave_groq('   ') == 'gsk_DEL_SERVIDOR')

# --- 2. /chat/stream: a quién llama y con qué clave ---
llamadas = []
real_groq, real_gemini = mm.stream_groq, mm.stream_gemini
real_prompt = mm.build_system_prompt


def espia_groq(messages, system, model_name=None, max_tokens=1024, respaldo=False, api_key=''):
    llamadas.append({'proveedor': 'groq', 'api_key': api_key, 'max_tokens': max_tokens})
    yield 'data: "hola"\n\n'


def espia_gemini(messages, system, model_name='gemini-flash-latest', max_tokens=4096, is_greet=False):
    llamadas.append({'proveedor': 'gemini', 'api_key': '', 'max_tokens': max_tokens})
    yield 'data: "hola"\n\n'


mm.stream_groq, mm.stream_gemini = espia_groq, espia_gemini
mm.build_system_prompt = lambda **kw: 'SYSTEM'   # no depender de brain/ ni de MASTERMIND_PATH

invitado = mm.app.test_client()
admin = mm.app.test_client()
with admin.session_transaction() as s:
    s['is_admin'] = True


def pedir(cliente, **extra):
    llamadas.clear()
    cuerpo = {'messages': [{'role': 'user', 'content': 'hola'}], **extra}
    r = cliente.post('/chat/stream', json=cuerpo)
    r.get_data()                                  # agota el stream: sin esto generate() no corre
    return llamadas[0] if llamadas else {}


try:
    # Admin SIN clave propia: sigue yendo a Gemini (comportamiento de hoy, no se toca).
    c = pedir(admin)
    check('admin sin clave: responde Gemini (como hasta hoy)', c.get('proveedor') == 'gemini')

    # Admin CON clave propia: Groq con SU clave, y Gemini no se toca.
    c = pedir(admin, groq_key='gsk_DEL_AMIGO')
    check('admin con clave: responde Groq', c.get('proveedor') == 'groq')
    check('admin con clave: se usa la clave del usuario', c.get('api_key') == 'gsk_DEL_AMIGO')
    check('admin con clave: NO se llama a Gemini', all(x['proveedor'] != 'gemini' for x in llamadas))

    # Invitado SIN clave: Groq con la del servidor (comportamiento de hoy).
    c = pedir(invitado)
    check('invitado sin clave: Groq con la del servidor', c.get('proveedor') == 'groq' and c.get('api_key') == '')

    # Invitado CON clave propia: Groq con la suya y con el tope completo (paga él).
    c = pedir(invitado, groq_key='gsk_DEL_AMIGO')
    check('invitado con clave: se usa la suya', c.get('api_key') == 'gsk_DEL_AMIGO')
    check('invitado con clave: tope completo de tokens (paga él)', c.get('max_tokens') == 4096)

    # La clave del usuario no se queda en la sesión del servidor (no se guarda en ningún sitio).
    with admin.session_transaction() as s:
        check('la clave NO se guarda en la sesión del servidor',
              not any('gsk_DEL_AMIGO' in str(v) for v in s.values()))

    # --- 3. De qué servicio es cada clave, por su prefijo ---
    check('gsk_… es de Groq', mm.proveedor_de_clave('gsk_loquesea') == 'groq')
    check('AIza… es de Gemini', mm.proveedor_de_clave('AIzaSyLoQueSea') == 'gemini')
    check('sk-ant-… es de Claude', mm.proveedor_de_clave('sk-ant-api03-loquesea') == 'claude')
    check('clave rara: no se reconoce', mm.proveedor_de_clave('pepito') is None)
    check('vacía: no se reconoce', mm.proveedor_de_clave('') is None)

    # Una clave que no reconocemos NO debe acabar en ningún proveedor: mejor decírselo al usuario.
    llamadas.clear()
    r = invitado.post('/chat/stream', json={'messages': [{'role': 'user', 'content': 'hola'}], 'ia_key': 'clave-rara'})
    cuerpo = r.get_data(as_text=True)
    check('clave no reconocida: no se llama a ningún modelo', not llamadas)
    check('clave no reconocida: se avisa al usuario', 'no parece de Groq' in cuerpo)

    # CONTROL: con la lógica rota (ignorar la clave del usuario), el test lo detecta.
    real_clave = mm._clave_groq
    mm._clave_groq = lambda clave_usuario='': os.environ['GROQ_API_KEY']
    roto = mm._clave_groq('gsk_DEL_AMIGO') == 'gsk_DEL_AMIGO'
    mm._clave_groq = real_clave
    check('CONTROL: si se ignorase la clave del usuario, el test fallaría', not roto)
finally:
    mm.stream_groq, mm.stream_gemini = real_groq, real_gemini
    mm.build_system_prompt = real_prompt

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
