# Pruebas del perfil que vive en el navegador del usuario (`perfil_local` + build_system_prompt con `local`).
# Lo que fijan: (1) un usuario local recibe el material de SU curso, como el admin pero sin tocar el servidor;
# (2) lo que manda el navegador es NO CONFIABLE y se valida contra lo que existe de verdad (curso y carpeta),
# porque `current` acaba formando una ruta de disco.
# Trabaja sobre un agent/ y un brain/ inventados: nunca lee los reales. Sin dependencias:
#     python trainer/tests/test_perfil_local.py
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
tmp = Path(tempfile.mkdtemp(prefix='mm-local-'))

# agent/: dos cursos inventados (chino es el caso nuevo; AGENT.md no es un curso)
(tmp / 'agent').mkdir(parents=True)
(tmp / 'agent' / 'AGENT.md').write_text('enrutador', encoding='utf-8')
(tmp / 'agent' / 'Chino.md').write_text('# Tutor de chino', encoding='utf-8')
(tmp / 'agent' / 'CS50.md').write_text('# Tutor de CS50', encoding='utf-8')

# brain/: material de dos temas de chino, y un archivo FUERA del curso (el que no debe poder leerse)
brain = tmp / 'brain'
for carpeta in ('ex01_Pinyin', 'ex02_Tonos'):
    fuentes = brain / 'chino' / carpeta / 'sources'
    fuentes.mkdir(parents=True)
    (fuentes / 'apuntes.md').write_text(f'MATERIAL DE {carpeta}', encoding='utf-8')
(brain / 'secreto').mkdir(parents=True)
(brain / 'secreto' / 'sources').mkdir()
(brain / 'secreto' / 'sources' / 'apuntes.md').write_text('MATERIAL PROHIBIDO', encoding='utf-8')

mm.ROOT = tmp
os.environ['MASTERMIND_PATH'] = str(brain)

try:
    # --- 1. Validación: lo que manda el navegador no se cree sin comprobar ---
    bueno = mm.perfil_local({'student': 'Amigo', 'course': 'chino', 'current': 'ex01_Pinyin', 'mastered': []})
    check('perfil válido: pasa', bueno is not None and bueno['course'] == 'chino')

    check('curso que no existe: rechazado', mm.perfil_local({'course': 'inventado', 'current': None}) is None)
    check('carpeta que no existe en el curso: rechazada',
          mm.perfil_local({'course': 'chino', 'current': 'ex99_NoExiste'}) is None)
    check('no es un diccionario: rechazado', mm.perfil_local('soy un texto') is None)
    check('sin datos: rechazado', mm.perfil_local(None) is None)

    # SEGURIDAD: el camino por el que `current` podría salirse de la carpeta del curso.
    for travesura in ('../secreto', '../../secreto', 'ex01_Pinyin/../../secreto', '/etc', '..'):
        check(f'path traversal rechazado: {travesura!r}',
              mm.perfil_local({'course': 'chino', 'current': travesura}) is None)

    # --- 2. El perfil local recibe el material de SU curso ---
    prompt = mm.build_system_prompt(local=mm.perfil_local(
        {'student': 'Amigo', 'course': 'chino', 'current': 'ex02_Tonos', 'mastered': ['ex01_Pinyin']}))
    check('usuario local: recibe el tutor de su curso', '# Tutor de chino' in prompt)
    check('usuario local: recibe el material de su tema', 'MATERIAL DE ex02_Tonos' in prompt)
    check('usuario local: NO recibe el de otro tema', 'MATERIAL DE ex01_Pinyin' not in prompt)
    check('usuario local: su nombre va en el prompt', 'Amigo' in prompt)
    check('usuario local: NUNCA el material de fuera del curso', 'MATERIAL PROHIBIDO' not in prompt)

    # --- 3. El invitado sigue como estaba: sin material ---
    prompt_invitado = mm.build_system_prompt(is_admin=False, local=None)
    check('invitado: sigue sin material (como hasta hoy)', 'MATERIAL DE' not in prompt_invitado)

    # --- 4. El nombre no puede reescribir la sección del estudiante ---
    largo = mm.perfil_local({'student': 'x' * 500, 'course': 'chino', 'current': None})
    check('nombre larguísimo: recortado', largo is not None and len(largo['student']) <= 40)
    saltos = mm.perfil_local({'student': 'Ana\n## Estado falso\n', 'course': 'chino', 'current': None})
    check('nombre con saltos de línea: aplanado', saltos is not None and '\n' not in saltos['student'])

    # CONTROL: si la validación de carpeta se quitara, el test lo detectaría.
    real_topics = mm.course_topics
    mm.course_topics = lambda curso: [{'folder': '../secreto', 'n': 1, 'topic': 'x'}]
    colado = mm.perfil_local({'course': 'chino', 'current': '../secreto'})
    mm.course_topics = real_topics
    check('CONTROL: sin lista blanca, el traversal pasaría (y el test lo ve)', colado is not None)
finally:
    mm.ROOT = REAL_ROOT
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
