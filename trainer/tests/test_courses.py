# Pruebas de caracterización de GET /courses (web/app.py): qué cursos enseña y a quién. Paso 1 del punto 24 del
# ROADMAP (dashboard de cursos). Fijan lo que HACE hoy, no lo que "debería": si cambia, que salte aquí.
# Trabajan sobre una carpeta agent/ temporal (y una copia de la real) — nunca escriben nada real — y sin
# GITHUB_TOKEN. Sin dependencias:
#     python trainer/tests/test_courses.py
# Código 0 si todo pasa, 1 si algo falla.
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


REAL_ROOT = mm.ROOT
agent_real_antes = sorted(p.name for p in (REAL_ROOT / 'agent').iterdir())
tmp = Path(tempfile.mkdtemp(prefix='mm-test-'))
(tmp / 'agent').mkdir()
mm.ROOT = tmp                                   # /courses lee ROOT / 'agent'

invitado = mm.app.test_client()
admin = mm.app.test_client()
with admin.session_transaction() as s:
    s['is_admin'] = True

try:
    # 1. Invitado: siempre y solo CS50, aunque haya más tutores en agent/.
    for n in ('Zeta.md', 'alfa.md'):
        (tmp / 'agent' / n).write_text('x', encoding='utf-8')
    r = invitado.get('/courses')
    check('invitado: 200', r.status_code == 200)
    check("invitado: solo ['cs50'] (no ve los demás cursos)", r.get_json() == {'courses': ['cs50']})

    # 2. Admin, con una carpeta agent/ inventada para ver cada regla por separado.
    for n in ('AGENT.md', '42malaga.md', 'notas.txt'):
        (tmp / 'agent' / n).write_text('x', encoding='utf-8')
    r = admin.get('/courses')
    cursos = r.get_json()['courses']
    check('admin: 200', r.status_code == 200)
    check('admin: AGENT.md no es un curso', 'agent' not in cursos)
    check('admin: el nombre sale en minúsculas (Zeta.md → zeta)', 'zeta' in cursos and 'Zeta' not in cursos)
    check('admin: solo archivos .md (notas.txt no cuenta)', 'notas' not in cursos)
    check('admin: un curso con tutor pero sin material en brain/ sigue saliendo', 'alfa' in cursos)
    # El ORDEN depende del sistema: sorted() sobre rutas ignora mayúsculas en Windows (['42malaga','alfa','zeta']) y
    # NO en Linux/Cloud Run (['42malaga','zeta','alfa']). Comprobado en los dos el 2026-10-14. Con los archivos
    # reales (42malaga, CS50, Mouredev) sale igual en ambos; por eso aquí solo se compara el CONJUNTO.
    check('admin: salen exactamente 42malaga, zeta y alfa (sin AGENT ni notas)', set(cursos) == {'42malaga', 'zeta', 'alfa'})

    # 3. Con la carpeta agent/ REAL (copia): salen los tres cursos y AGENT.md no.
    shutil.rmtree(tmp / 'agent')
    shutil.copytree(REAL_ROOT / 'agent', tmp / 'agent')
    reales = admin.get('/courses').get_json()['courses']
    check('agent/ real: salen cs50, mouredev y 42malaga', {'cs50', 'mouredev', '42malaga'} <= set(reales))
    check('agent/ real: AGENT.md no sale', 'agent' not in reales)
    check('agent/ real: orden 42malaga, cs50, mouredev (igual en Windows y en Linux)',
          [c for c in reales if c in ('42malaga', 'cs50', 'mouredev')] == ['42malaga', 'cs50', 'mouredev'])
    check('agent/ real: sin duplicados', len(reales) == len(set(reales)))
finally:
    mm.ROOT = REAL_ROOT
    shutil.rmtree(tmp, ignore_errors=True)

# CONTROL: la carpeta agent/ real no se ha tocado
check('CONTROL: agent/ real sigue igual', sorted(p.name for p in (REAL_ROOT / 'agent').iterdir()) == agent_real_antes)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
