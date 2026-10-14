# Pruebas de GET /dashboard (web/app.py): resumen de TODOS los cursos a la vez y logros. Paso 2 del punto 24 del
# ROADMAP. Trabajan sobre una copia temporal de config/ y agent/ y un brain/ INVENTADO: nunca tocan nada real y sin
# GITHUB_TOKEN (salvo la prueba de producción, que sustituye github_get por una función falsa). Sin dependencias:
#     python trainer/tests/test_dashboard.py
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


REAL_ROOT = mm.ROOT
config_antes = {p.name: p.read_bytes() for p in (REAL_ROOT / 'config').rglob('*') if p.is_file()}
tmp = Path(tempfile.mkdtemp(prefix='mm-test-'))
shutil.copytree(REAL_ROOT / 'config', tmp / 'config')
(tmp / 'config' / 'local.json').unlink(missing_ok=True)       # que _brain_path use MASTERMIND_PATH
(tmp / 'agent').mkdir()
for n in ('CS50.md', 'Mouredev.md', '42malaga.md', 'AGENT.md'):
    (tmp / 'agent' / n).write_text('x', encoding='utf-8')

# brain/ inventado: cs50 con 3 semanas, MoureDev con 4 ejercicios, 42 con 2.
brain = tmp / 'brain'
for d in ('cs50/week01-c', 'cs50/week02-arrays', 'cs50/week03-algorithms',
          'Moure/java/ex1_HelloWorld', 'Moure/java/ex2_Variables', 'Moure/java/ex3_DataTypes', 'Moure/java/ex4_Operadores',
          '42/ex01_first_word', '42/ex02_fizzbuzz'):
    (brain / d).mkdir(parents=True)
os.environ['MASTERMIND_PATH'] = str(brain)

prog = tmp / 'config' / 'progress'
shutil.rmtree(prog, ignore_errors=True)
prog.mkdir(parents=True)


def escribir(curso, current, mastered):
    (prog / f'{curso}.json').write_text(json.dumps({'current': current, 'mastered': mastered}), encoding='utf-8')


escribir('cs50', 'week02-arrays', ['week01-c'])
escribir('mouredev', 'ex3_DataTypes', ['ex1_HelloWorld', 'ex2_Variables'])      # 42malaga: SIN archivo a propósito

mm.ROOT = tmp
invitado = mm.app.test_client()
admin = mm.app.test_client()
with admin.session_transaction() as s:
    s['is_admin'] = True


def pedir():
    r = admin.get('/dashboard')
    return r, (r.get_json() or {})


def foto():                      # nombre → bytes de TODO lo que hay en la config temporal (incluye archivos nuevos)
    return {str(p.relative_to(tmp)): p.read_bytes() for p in (tmp / 'config').rglob('*') if p.is_file()}


def curso(datos, nombre):
    return next((c for c in datos.get('courses', []) if c['course'] == nombre), {})


def logro(datos, id_):
    return next((a for a in datos.get('achievements', []) if a['id'] == id_), {})


try:
    # 1. Seguridad: el invitado no tiene panel y no ve nada.
    r = invitado.get('/dashboard')
    check('invitado → 403', r.status_code == 403)
    check('invitado: la respuesta es el aviso 403 y no lleva cursos ni logros',
          r.status_code == 403 and (r.get_json() or {}).get('error') and 'courses' not in r.get_json() and 'achievements' not in r.get_json())

    # 2. Admin: todos los cursos a la vez, sin AGENT.md. Y la PRIMERA petición no escribe nada en config/.
    base = foto()
    r, d = pedir()
    check('admin → 200', r.status_code == 200)
    check('GET /dashboard no crea ni modifica ningún archivo de config/ (primera petición)', foto() == base)
    check('admin: salen cs50, mouredev y 42malaga (sin AGENT)', {c['course'] for c in d.get('courses', [])} == {'cs50', 'mouredev', '42malaga'})

    # 3. Los números salen del progreso y de las carpetas de temas.
    c = curso(d, 'cs50')
    check('cs50: 1 de 3 dominado (33 %)', (c.get('done'), c.get('total'), c.get('percent')) == (1, 3, 33))
    check("cs50: ahora week02-arrays, último dominado week01-c, siguiente week03-algorithms",
          (c.get('current'), c.get('last_mastered'), c.get('next')) == ('week02-arrays', 'week01-c', 'week03-algorithms'))
    check("cs50: etiquetas legibles ('Week 2 · Arrays')", c.get('current_label') == 'Week 2 · Arrays')
    check('cs50: no está terminado', c.get('finished') is False)
    c = curso(d, 'mouredev')
    check('mouredev: 2 de 4 dominados (50 %)', (c.get('done'), c.get('total'), c.get('percent')) == (2, 4, 50))
    check('mouredev: siguiente ex4_Operadores', c.get('next') == 'ex4_Operadores')

    # 4. Curso SIN archivo de progreso: 0 hechos, sin romperse.
    c = curso(d, '42malaga')
    check('42malaga sin archivo: 0 de 2, 0 %', (c.get('done'), c.get('total'), c.get('percent')) == (0, 2, 0))
    check('42malaga sin archivo: existe en el panel, sin tema actual, sin último, sin siguiente',
          c.get('course') == '42malaga' and (c.get('current'), c.get('last_mastered'), c.get('next')) == (None, None, None))

    # 5. Un tema "dominado" que ya no existe en brain/ NO cuenta (nunca puede salir más hechos que total).
    escribir('mouredev', 'ex3_DataTypes', ['ex1_HelloWorld', 'ex2_Variables', 'ex99_Fantasma'])
    r, d = pedir()
    check('un dominado que no existe en brain/ no se cuenta', curso(d, 'mouredev').get('done') == 2)

    # 6. Logros: solo derivados de lo que hay (3 temas dominados en total: 1 + 2 + 0).
    escribir('mouredev', 'ex3_DataTypes', ['ex1_HelloWorld', 'ex2_Variables'])
    r, d = pedir()
    check('first_topic desbloqueado', logro(d, 'first_topic').get('unlocked') is True)
    check('topics_5: 3/5 y bloqueado', (logro(d, 'topics_5').get('progress'), logro(d, 'topics_5').get('target'), logro(d, 'topics_5').get('unlocked')) == (3, 5, False))
    check('topics_10: 3/10 y bloqueado', (logro(d, 'topics_10').get('progress'), logro(d, 'topics_10').get('target')) == (3, 10))
    check('half_course: MoureDev 2/2 (la mitad de 4) → desbloqueado',
          (logro(d, 'half_course').get('progress'), logro(d, 'half_course').get('target'), logro(d, 'half_course').get('unlocked')) == (2, 2, True))
    check('course_complete: el más cercano es MoureDev 2/4 → bloqueado',
          (logro(d, 'course_complete').get('progress'), logro(d, 'course_complete').get('target'), logro(d, 'course_complete').get('unlocked')) == (2, 4, False))
    check('all_courses_started: 2/3 (42 aún sin empezar)',
          (logro(d, 'all_courses_started').get('progress'), logro(d, 'all_courses_started').get('target')) == (2, 3))
    check('solo hay los 6 logros de esta fase (rachas y pomodoros NO: no hay dato)',
          [a['id'] for a in d.get('achievements', [])] == ['first_topic', 'topics_5', 'topics_10', 'half_course', 'course_complete', 'all_courses_started'])

    # 7. Curso terminado: todos dominados → finished y course_complete.
    escribir('cs50', 'week03-algorithms', ['week01-c', 'week02-arrays', 'week03-algorithms'])
    r, d = pedir()
    check('cs50 con todo dominado: finished y 100 %', (curso(d, 'cs50').get('finished'), curso(d, 'cs50').get('percent')) == (True, 100))
    check('cs50 terminado: no hay siguiente', curso(d, 'cs50').get('course') == 'cs50' and curso(d, 'cs50').get('next') is None)
    check('cs50 terminado: course_complete desbloqueado', logro(d, 'course_complete').get('unlocked') is True)

    # 8. Un tutor con nombre raro en agent/ no rompe el panel (y no sale).
    (tmp / 'agent' / 'Mi Curso Raro.md').write_text('x', encoding='utf-8')
    r, d = pedir()
    check('nombre de curso no válido: el panel sigue en 200', r.status_code == 200)
    check('nombre de curso no válido: no aparece y siguen los otros 3',
          len(d.get('courses', [])) == 3 and all(' ' not in c['course'] for c in d['courses']))
    (tmp / 'agent' / 'Mi Curso Raro.md').unlink()

    # 9. Solo lee, también al repetirlo: no escribe progreso ni perfil.
    antes = foto()
    codigos = [pedir()[0].status_code, pedir()[0].status_code]
    check('GET /dashboard (200 dos veces más) tampoco modifica config/', codigos == [200, 200] and antes == foto())

    # 10. Producción (con GITHUB_TOKEN): una lectura de GitHub por curso, y solo del progreso (no del perfil).
    llamadas = []
    original = mm.github_get
    mm.github_get = lambda ruta: (llamadas.append(ruta), json.dumps({'current': None, 'mastered': []}))[1]
    os.environ['GITHUB_TOKEN'] = 'falso'
    try:
        r, d = pedir()
    finally:
        os.environ.pop('GITHUB_TOKEN', None)
        mm.github_get = original
    check('producción: una lectura de GitHub por curso (3)', len(llamadas) == 3)
    check('producción: solo lee archivos de progreso',
          len(llamadas) > 0 and all(x.startswith('trainer/config/progress/') for x in llamadas))

    # 11. Los archivos del panel se sirven y el service worker se entera de ellos (paso 3).
    mm.ROOT = REAL_ROOT                        # los estáticos viven en web/, no en la copia temporal
    web = REAL_ROOT / 'web'
    js, css = invitado.get('/dashboard.js'), invitado.get('/dashboard.css')
    check('/dashboard.js: 200 y es JavaScript (no text/plain)', js.status_code == 200 and 'javascript' in js.content_type)
    check('/dashboard.css: 200 y es CSS', css.status_code == 200 and 'css' in css.content_type)
    check('/dashboard.js y .css llevan Cache-Control: no-cache como el resto de la interfaz',
          js.headers.get('Cache-Control') == 'no-cache' and css.headers.get('Cache-Control') == 'no-cache')
    check('index.html carga dashboard.css y dashboard.js (el JS ANTES que app.js)',
          'href="dashboard.css"' in (web / 'index.html').read_text(encoding='utf-8')
          and (web / 'index.html').read_text(encoding='utf-8').index('src="dashboard.js"') < (web / 'index.html').read_text(encoding='utf-8').index('src="app.js"'))
    sw = invitado.get('/sw.js').get_data(as_text=True)
    check("sw.js guarda '/dashboard.js' y '/dashboard.css' en su caché", "'/dashboard.js'" in sw and "'/dashboard.css'" in sw)
    # La huella se calcula sobre una COPIA de web/ (la prueba no toca los archivos reales).
    copia = tmp / 'web'
    copia.mkdir()
    for nombre in set(mm._ARCHIVOS_INTERFAZ) | {'dashboard.js', 'dashboard.css'}:   # siempre estos dos, estén o no en la lista
        if (web / nombre).exists():
            shutil.copy2(web / nombre, copia / nombre)
    raiz_real = mm.app.root_path
    mm.app.root_path = str(copia)
    try:
        v1 = mm._version_interfaz()
        (copia / 'dashboard.js').write_bytes((copia / 'dashboard.js').read_bytes() + b'\n// prueba\n')
        v2 = mm._version_interfaz()
    finally:
        mm.app.root_path = raiz_real
    check('cambiar dashboard.js cambia la versión del service worker (el móvil se entera)', v1 != v2)
finally:
    mm.ROOT = REAL_ROOT
    os.environ.pop('MASTERMIND_PATH', None)
    shutil.rmtree(tmp, ignore_errors=True)

config_despues = {p.name: p.read_bytes() for p in (REAL_ROOT / 'config').rglob('*') if p.is_file()}
check('CONTROL: el config/ real sigue idéntico', config_antes == config_despues)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
