# Pruebas de caracterización del perfil (web/app.py): cómo se lee, cómo se guarda y qué carpeta de tema
# se usa. Trabajan sobre una COPIA temporal de config/ — nunca tocan el profile.json real — y sin
# GITHUB_TOKEN (no suben nada a GitHub). Sin dependencias:
#     python trainer/tests/test_profile.py
# Código 0 si todo pasa, 1 si algo falla.
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'web'))
os.environ.pop('GITHUB_TOKEN', None)          # nada de GitHub en las pruebas
import app as mm  # noqa: E402

fallos = 0


def check(nombre, cond):
    global fallos
    print(('✅ ' if cond else '❌ ') + nombre)
    if not cond:
        fallos += 1


# ── Entorno aislado: ROOT apunta a una copia de trainer/ con solo config/ ──
REAL_ROOT = mm.ROOT
tmp = Path(tempfile.mkdtemp(prefix='mm-test-'))
shutil.copytree(REAL_ROOT / 'config', tmp / 'config')
mm.ROOT = tmp
perfil_path = tmp / 'config' / 'profile.json'
real_antes = (REAL_ROOT / 'config' / 'profile.json').read_bytes()


def perfil():
    return json.loads(perfil_path.read_text(encoding='utf-8'))


def escribir(p):
    perfil_path.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding='utf-8')


cliente = mm.app.test_client()

try:
    # 1. _topic_folder: qué carpeta de tema se usa
    check("_topic_folder: si hay current_folder, manda él",
          mm._topic_folder('mouredev', {'current_folder': 'ex3_DataTypes'}) == 'ex3_DataTypes')
    check("_topic_folder: CS50 sin current_folder → week0N-c",
          mm._topic_folder('cs50', {'current_week': 2}) == 'week02-c')
    check("_topic_folder: otro curso sin current_folder → None",
          mm._topic_folder('mouredev', {}) is None)

    # 2. get_admin_profile sin token → lee el archivo local
    escribir({**perfil(), 'current_topic': 'Marca de prueba'})
    check('get_admin_profile (sin token): lee el archivo local', mm.get_admin_profile()['current_topic'] == 'Marca de prueba')

    # 3. /update-profile sin ser admin → 403 y no toca nada
    antes = perfil_path.read_bytes()
    r = cliente.post('/update-profile', json={'course': 'cs50'})
    check('/update-profile sin admin → 403', r.status_code == 403)
    check('/update-profile sin admin → el perfil no cambia', perfil_path.read_bytes() == antes)

    # 4. /update-profile como admin: cambia lo permitido, conserva el resto, ignora lo no permitido
    with cliente.session_transaction() as s:
        s['is_admin'] = True
    escribir({**perfil(), 'course': 'mouredev', 'current_folder': 'ex1_HelloWorld', 'notes': 'no tocar'})
    r = cliente.post('/update-profile', json={'course': 'cs50', 'inventado': 'x'})
    p = perfil()
    check('/update-profile admin → 200', r.status_code == 200)
    check('/update-profile: cambia un campo permitido (course)', p['course'] == 'cs50')
    check('/update-profile: conserva los demás (current_folder, notes)',
          p.get('current_folder') == 'ex1_HelloWorld' and p.get('notes') == 'no tocar')
    check('/update-profile: ignora campos no permitidos', 'inventado' not in p)
    check('/update-profile: devuelve el perfil guardado', r.get_json().get('profile', {}).get('course') == 'cs50')

    # 5. PRODUCCIÓN: el perfil de verdad vive en GitHub y la copia local es la de la imagen (vieja).
    #    Elegir curso NO puede devolver la partida a lo que diga la copia vieja.
    escribir({**perfil(), 'course': 'mouredev', 'current_folder': 'ex1_HelloWorld'})      # copia vieja
    en_github = {**perfil(), 'current_folder': 'ex3_DataTypes', 'current_topic': 'Data Types'}  # partida real
    subido = {}
    orig_get, orig_put = mm.github_get, mm.github_put
    mm.github_get = lambda path: json.dumps(en_github)
    mm.github_put = lambda path, content, msg: subido.update(json.loads(content))
    os.environ['GITHUB_TOKEN'] = 'falso-para-la-prueba'
    try:
        cliente.post('/update-profile', json={'course': 'mouredev'})
    finally:
        mm.github_get, mm.github_put = orig_get, orig_put
        os.environ.pop('GITHUB_TOKEN', None)
    check('producción: al elegir curso se conserva la partida guardada en GitHub (ex3, no ex1)',
          subido.get('current_folder') == 'ex3_DataTypes')
finally:
    mm.ROOT = REAL_ROOT
    shutil.rmtree(tmp, ignore_errors=True)

# CONTROL: el profile.json real no se ha tocado
check('CONTROL: el profile.json real sigue idéntico', (REAL_ROOT / 'config' / 'profile.json').read_bytes() == real_antes)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
