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
shutil.copytree(REAL_ROOT / 'agent', tmp / 'agent')        # instrucciones de la IA (build_system_prompt)
mm.ROOT = tmp
perfil_path = tmp / 'config' / 'profile.json'
real_antes = (REAL_ROOT / 'config' / 'profile.json').read_bytes()


def perfil():
    return json.loads(perfil_path.read_text(encoding='utf-8'))


def escribir(p):
    perfil_path.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding='utf-8')


cliente = mm.app.test_client()

try:
    # 1. _topic_folder: qué carpeta de tema (y por tanto qué material) recibe la IA del chat.
    #    Lee SOLO el progreso de su curso (config/progress/<curso>.json).
    prog = tmp / 'config' / 'progress'
    (prog / 'mouredev.json').write_text(json.dumps({'current': 'ex3_DataTypes', 'mastered': []}), encoding='utf-8')
    (prog / 'cs50.json').write_text(json.dumps({'current': 'week02-arrays', 'mastered': []}), encoding='utf-8')
    check("_topic_folder('mouredev'): la carpeta de su progreso", mm._topic_folder('mouredev') == 'ex3_DataTypes')
    check("_topic_folder('cs50'): semana 2 = week02-arrays (antes inventaba week02-c, que no existe)",
          mm._topic_folder('cs50') == 'week02-arrays')
    escribir({**perfil(), 'course': 'cs50', 'current_folder': 'ex3_DataTypes'})   # restos de MoureDev en el perfil
    check("_topic_folder('cs50'): NO usa carpetas de MoureDev aunque estén en el perfil",
          mm._topic_folder('cs50') == 'week02-arrays')
    check("_topic_folder: curso sin progreso → None", mm._topic_folder('cursonuevo') is None)

    # 1b. build_system_prompt usa _topic_folder: el material que recibe la IA sale del progreso del curso.
    brain = Path(json.loads((tmp / 'config' / 'local.json').read_text(encoding='utf-8'))['mastermind_path']) \
        if (tmp / 'config' / 'local.json').exists() else REAL_ROOT.parent / 'brain'
    notas = (brain / 'cs50' / 'week01-c' / 'sources' / 'lecture_notes.md').read_text(encoding='utf-8')[200:260]
    (prog / 'cs50.json').write_text(json.dumps({'current': 'week01-c', 'mastered': []}), encoding='utf-8')
    escribir({**perfil(), 'course': 'cs50'})
    check('admin en CS50 semana 1: la IA recibe el material de week01-c', notas in mm.build_system_prompt(is_admin=True))
    # El invitado nunca recibe material (sources_text = "" si no es admin): así era y así sigue.
    check('invitado: no recibe material', notas not in mm.build_system_prompt(is_admin=False))

    # 1c. /profile devuelve, además del perfil, el progreso DEL CURSO ELEGIDO (para la barra de arriba)
    (prog / 'mouredev.json').write_text(json.dumps({'current': 'ex3_DataTypes', 'mastered': ['ex1_HelloWorld']}), encoding='utf-8')
    (prog / 'cs50.json').write_text(json.dumps({'current': 'week02-arrays', 'mastered': []}), encoding='utf-8')
    c = mm.app.test_client()
    with c.session_transaction() as s:
        s['is_admin'] = True
    escribir({**perfil(), 'course': 'mouredev'})
    pr = c.get('/profile').get_json().get('progress', {})
    check("/profile (mouredev): progreso de MoureDev → n=3, 'Data Types'",
          (pr.get('current'), pr.get('n'), pr.get('topic')) == ('ex3_DataTypes', 3, 'Data Types'))
    escribir({**perfil(), 'course': 'cs50'})
    pr = c.get('/profile').get_json().get('progress', {})
    check("/profile (cs50): progreso de CS50 → n=2, 'Arrays' (no el de MoureDev)",
          (pr.get('current'), pr.get('n'), pr.get('topic')) == ('week02-arrays', 2, 'Arrays'))
    pr = mm.app.test_client().get('/profile').get_json().get('progress', {})
    check('/profile (invitado): semana 1, sin leer el progreso de Nando', (pr.get('current'), pr.get('n')) == ('week01-c', 1))

    # 1d. /ls → GET /progress: lista de temas del curso (de las carpetas de brain/) con su estado
    if not hasattr(mm, 'course_topics'):
        check('course_topics y GET /progress existen', False)
    else:
        ts = mm.course_topics('mouredev')
        check('course_topics(mouredev): ex1…ex10 en orden de NÚMERO (ex10 al final, no tras ex1)',
              [t['n'] for t in ts] == list(range(1, 11)) and ts[0]['folder'] == 'ex1_HelloWorld' and ts[-1]['folder'] == 'ex10_OOP')
        ts = mm.course_topics('cs50')
        check('course_topics(cs50): week01…week10 en orden', [t['n'] for t in ts] == list(range(1, 11)) and ts[1]['folder'] == 'week02-arrays')
        check('course_topics: curso sin carpetas → []', mm.course_topics('cursonuevo') == [])
        (prog / 'mouredev.json').write_text(json.dumps({'current': 'ex2_VariablesAndConstants', 'mastered': ['ex1_HelloWorld']}), encoding='utf-8')
        escribir({**perfil(), 'course': 'mouredev'})
        r = c.get('/progress')
        estados = [t['status'] for t in r.get_json().get('topics', [])] if r.status_code == 200 else []
        check("GET /progress: ✅ ex1 dominado, 👉 ex2 actual, 🔒 el resto",
              estados[:3] == ['mastered', 'current', 'locked'] and estados[3:] == ['locked'] * 7)
        check('GET /progress: el invitado no puede (su mundo es otro)', mm.app.test_client().get('/progress').status_code == 403)

    # 1e. Guardar la partida: POST /progress/next (solo tras aprobar; de uno en uno)
    (prog / 'mouredev.json').write_text(json.dumps({'current': 'ex1_HelloWorld', 'mastered': []}), encoding='utf-8')
    (prog / 'cs50.json').write_text(json.dumps({'current': 'week01-c', 'mastered': []}), encoding='utf-8')
    cs50_antes = (prog / 'cs50.json').read_bytes()
    escribir({**perfil(), 'course': 'mouredev'})
    r = c.post('/progress/next', json={})
    check('POST /progress/next: ex1 → dominado, ex2 → actual',
          r.status_code == 200 and mm.get_progress('mouredev') == {'current': 'ex2_VariablesAndConstants', 'mastered': ['ex1_HelloWorld']})
    check('POST /progress/next: responde con el tema nuevo para el botón',
          (r.get_json() or {}).get('progress', {}).get('topic') == 'Variables And Constants')
    c.post('/progress/next', json={'to': 'ex9_Funciones'})           # intento de saltar: se ignora
    check('POST /progress/next: NO se puede saltar (pedir ex9 avanza solo a ex3)',
          mm.get_progress('mouredev')['current'] == 'ex3_DataTypes')
    check('POST /progress/next: CS50 no se toca', (prog / 'cs50.json').read_bytes() == cs50_antes)
    (prog / 'mouredev.json').write_text(json.dumps({'current': 'ex10_OOP', 'mastered': []}), encoding='utf-8')
    check('POST /progress/next: en el último ejercicio → 400, no inventa un ex11', c.post('/progress/next', json={}).status_code == 400)
    check('POST /progress/next: el invitado no puede', mm.app.test_client().post('/progress/next', json={}).status_code == 403)

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

    # 6. Progreso por curso: config/progress/<curso>.json (get_progress / save_progress / folder_label)
    if not hasattr(mm, 'get_progress'):
        check('get_progress / save_progress / folder_label existen', False)
    else:
        prog_dir = tmp / 'config' / 'progress'
        check('get_progress: lee el archivo del curso',
              mm.get_progress('mouredev') == json.loads((prog_dir / 'mouredev.json').read_text(encoding='utf-8')))
        cs50_antes = (prog_dir / 'cs50.json').read_bytes()
        mm.save_progress('mouredev', {'current': 'ex2_VariablesAndConstants', 'mastered': ['ex1_HelloWorld']})
        check('save_progress + get_progress: ida y vuelta',
              mm.get_progress('mouredev') == {'current': 'ex2_VariablesAndConstants', 'mastered': ['ex1_HelloWorld']})
        check('AISLAMIENTO: guardar MoureDev no toca el progreso de CS50', (prog_dir / 'cs50.json').read_bytes() == cs50_antes)
        check('curso sin archivo → progreso vacío, sin romperse',
              mm.get_progress('cursonuevo') == {'current': None, 'mastered': []})
        rechazado = True
        for malo in ('../profile', 'a/b', '', 'MoureDev!'):
            try:
                mm.get_progress(malo)
                rechazado = False
            except ValueError:
                pass
        check("SEGURIDAD: nombres de curso raros ('../profile', 'a/b'…) se rechazan", rechazado)
        check("folder_label: ex1_HelloWorld → 'Hello World'", mm.folder_label('ex1_HelloWorld') == 'Hello World')
        check("folder_label: ex10_OOP → 'OOP'", mm.folder_label('ex10_OOP') == 'OOP')
        check("folder_label: ex2_VariablesAndConstants → 'Variables And Constants'",
              mm.folder_label('ex2_VariablesAndConstants') == 'Variables And Constants')
        check("folder_label: week02-arrays → 'Week 2 · Arrays'", mm.folder_label('week02-arrays') == 'Week 2 · Arrays')
        check("folder_label: week01-c → 'Week 1 · C'", mm.folder_label('week01-c') == 'Week 1 · C')
        check("folder_label: None → ''", mm.folder_label(None) == '')
        # Producción: GitHub, en trainer/config/progress/<curso>.json
        rutas = []
        mm.github_get = lambda path: (rutas.append(('get', path)), json.dumps({'current': 'ex5_Strings', 'mastered': []}))[1]
        mm.github_put = lambda path, content, msg: rutas.append(('put', path))
        os.environ['GITHUB_TOKEN'] = 'falso-para-la-prueba'
        try:
            leido = mm.get_progress('mouredev')
            mm.save_progress('mouredev', leido)
        finally:
            mm.github_get, mm.github_put = orig_get, orig_put
            os.environ.pop('GITHUB_TOKEN', None)
        check('producción: get_progress lee de GitHub', leido.get('current') == 'ex5_Strings')
        check('producción: lee y guarda en trainer/config/progress/mouredev.json',
              rutas == [('get', 'trainer/config/progress/mouredev.json'), ('put', 'trainer/config/progress/mouredev.json')])
finally:
    mm.ROOT = REAL_ROOT
    shutil.rmtree(tmp, ignore_errors=True)

# CONTROL: el profile.json real no se ha tocado
check('CONTROL: el profile.json real sigue idéntico', (REAL_ROOT / 'config' / 'profile.json').read_bytes() == real_antes)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
