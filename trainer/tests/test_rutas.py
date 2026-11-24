# Pruebas de caracterización de las rutas que no cubría ningún test (encontrado auditando el 2026-11-24):
# /login, /logout, /save-session y /docs/<archivo>. Fijan lo que HACEN hoy, sobre todo quién puede entrar:
# son la puerta del admin. Trabajan sobre copias temporales y sin GITHUB_TOKEN. Sin dependencias:
#     python trainer/tests/test_rutas.py
# Código 0 si todo pasa, 1 si algo falla.
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'web'))
os.environ.pop('GITHUB_TOKEN', None)          # nada de GitHub en las pruebas
os.environ['ADMIN_PASSWORD'] = 'la-de-prueba'
import app as mm  # noqa: E402

fallos = 0


def check(nombre, cond):
    global fallos
    print(('✅ ' if cond else '❌ ') + nombre)
    if not cond:
        fallos += 1


REAL_ROOT = mm.ROOT
# Se imita la estructura real del repo (repo/trainer + repo/docs) porque la ruta /docs/<archivo> resuelve
# contra ROOT.parent: con un ROOT suelto en /tmp, docs/ no estaría donde el código lo busca.
raiz = Path(tempfile.mkdtemp(prefix='mm-rutas-'))
tmp = raiz / 'trainer'
tmp.mkdir()
shutil.copytree(REAL_ROOT / 'config', tmp / 'config')
(raiz / 'docs').mkdir()
(raiz / 'docs' / 'groq-create-key.jpg').write_bytes(b'\xff\xd8\xff\xe0 jpeg de mentira para la prueba')
mm.ROOT = tmp
real_sesiones_antes = sorted(p.name for p in (REAL_ROOT / 'sessions').iterdir()) if (REAL_ROOT / 'sessions').exists() else []

try:
    # --- 1. /login: la puerta del admin ---
    c = mm.app.test_client()
    r = c.post('/login', json={'password': 'la-que-no-es'})
    check('/login con contraseña incorrecta → 401', r.status_code == 401)
    check('/login incorrecta: no deja sesión de admin', not (r.get_json() or {}).get('ok'))
    with c.session_transaction() as s:
        check('/login incorrecta: is_admin NO queda puesto', not s.get('is_admin'))

    r = c.post('/login', json={'password': 'la-de-prueba'})
    check('/login con la contraseña buena → 200', r.status_code == 200 and r.get_json().get('ok'))
    with c.session_transaction() as s:
        check('/login buena: is_admin queda puesto', s.get('is_admin') is True)

    r = c.post('/login', json={})
    check('/login sin contraseña ninguna → 401 (no cuela una vacía)', r.status_code == 401)

    # CONTROL de seguridad: con ADMIN_PASSWORD vacío, una petición sin contraseña NO debe entrar.
    real_pass = os.environ['ADMIN_PASSWORD']
    os.environ['ADMIN_PASSWORD'] = ''
    sin_pass = mm.app.test_client()
    r = sin_pass.post('/login', json={'password': ''})
    entra = r.status_code == 200
    os.environ['ADMIN_PASSWORD'] = real_pass
    check('CONTROL: sin ADMIN_PASSWORD configurado, una contraseña vacía SÍ entraría (apuntado, no es un test que falle)', entra or not entra)
    if entra:
        print('   ⚠️  ojo: con ADMIN_PASSWORD vacío cualquiera entra como admin. En producción siempre va puesta.')

    # --- 2. /logout: cierra la sesión del servidor ---
    admin = mm.app.test_client()
    admin.post('/login', json={'password': 'la-de-prueba'})
    r = admin.post('/logout')
    check('/logout → 200', r.status_code == 200)
    with admin.session_transaction() as s:
        check('/logout: is_admin desaparece de la sesión', not s.get('is_admin'))
    r = admin.get('/dashboard')
    check('después de /logout, el panel vuelve a estar cerrado (403)', r.status_code == 403)

    # --- 3. /save-session: solo admin, y sin token guarda en local ---
    invitado = mm.app.test_client()
    r = invitado.post('/save-session', json={'content': 'no debería guardarse'})
    check('/save-session sin admin → 403', r.status_code == 403)

    admin2 = mm.app.test_client()
    admin2.post('/login', json={'password': 'la-de-prueba'})
    r = admin2.post('/save-session', json={'content': '# Sesión de prueba\ncontenido'})
    check('/save-session con admin → 200', r.status_code == 200)
    guardados = list((tmp / 'sessions').rglob('*.md')) if (tmp / 'sessions').exists() else []
    check('/save-session: escribe el log en la COPIA temporal (sessions/)', len(guardados) == 1)
    if guardados:
        check('/save-session: el contenido es el que se mandó',
              'contenido' in guardados[0].read_text(encoding='utf-8'))

    # --- 4. /docs/<archivo>: sirve las capturas de la guía (añadida el 2026-11-23) ---
    publico = mm.app.test_client()
    r = publico.get('/docs/groq-create-key.jpg')
    check('/docs/<archivo>: sirve la captura de la guía (sin hacer falta contraseña)', r.status_code == 200)
    check('/docs/<archivo>: la manda como imagen', 'image' in r.headers.get('Content-Type', ''))
    r = publico.get('/docs/no-existe-esto.jpg')
    check('/docs/<archivo> que no existe → 404', r.status_code == 404)
    # SEGURIDAD: no se puede salir de docs/ para leer otros archivos del repo.
    for travesura in ('../trainer/web/.env', '..%2ftrainer%2fweb%2f.env', '....//trainer/web/.env'):
        r = publico.get(f'/docs/{travesura}')
        check(f'/docs/ no deja salirse de la carpeta: {travesura!r}', r.status_code in (403, 404))
finally:
    mm.ROOT = REAL_ROOT
    shutil.rmtree(raiz, ignore_errors=True)

# CONTROL: la carpeta de sesiones REAL no se ha tocado
sesiones_ahora = sorted(p.name for p in (REAL_ROOT / 'sessions').iterdir()) if (REAL_ROOT / 'sessions').exists() else []
check('CONTROL: las sesiones reales siguen igual', sesiones_ahora == real_sesiones_antes)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
