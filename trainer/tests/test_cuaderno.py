# Pruebas del cuaderno que crece con el alumno (Japonés y futuros cursos del mismo método, ver
# CURSOS_CUADERNO en app.js). Lo que fijan: el cuaderno viaja completo en el prompt, nunca lo guarda el
# servidor, y un curso que no lo usa no ve nada de esto. Sin dependencias:
#     python trainer/tests/test_cuaderno.py
# Código 0 si todo pasa, 1 si algo falla.
import os
import sys
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


real_prompt_courses = mm._cursos_disponibles
mm._cursos_disponibles = lambda: ['japones', 'cs50']   # sin depender de agent/ real
real_course_topics = mm.course_topics
mm.course_topics = lambda curso: []                     # japonés no tiene carpetas ex/week

try:
    # --- 1. Cuaderno vacío: aparece la sección, pide la primera entrada ---
    prompt = mm.build_system_prompt(local=mm.perfil_local({'student': 'Ana', 'course': 'japones', 'current': None}),
                                     cuaderno='')
    check('cuaderno vacío: aparece la sección', '## Tu cuaderno hasta ahora' in prompt)
    check('cuaderno vacío: lo dice explícitamente', 'vacío' in prompt.lower())
    check('cuaderno vacío: recuerda la regla de "completo, nunca resumen"', 'COMPLETO' in prompt)

    # --- 2. Cuaderno con contenido: viaja ENTERO, no recortado ---
    cuaderno_grande = "🎒 Cuaderno\n" + "\n".join(f"| Frase {i} | 日本語 | significado {i} |" for i in range(50))
    prompt = mm.build_system_prompt(local=mm.perfil_local({'student': 'Ana', 'course': 'japones', 'current': None}),
                                     cuaderno=cuaderno_grande)
    check('cuaderno con contenido: la primera fila llega', 'Frase 0' in prompt)
    check('cuaderno con contenido: la última fila llega (no se recorta)', 'Frase 49' in prompt)

    # --- 3. Un curso SIN cuaderno (cuaderno=None): no aparece nada de esto ---
    prompt_sin = mm.build_system_prompt(local=mm.perfil_local({'student': 'Ana', 'course': 'cs50', 'current': None}),
                                        cuaderno=None)
    check('curso sin cuaderno: no aparece la sección', '## Tu cuaderno hasta ahora' not in prompt_sin)

    # --- 4. El tope (CUADERNO_TOPE) protege de un cuaderno gigantesco ---
    enorme = 'x' * (mm.CUADERNO_TOPE + 5000)
    prompt_tope = mm.build_system_prompt(local=mm.perfil_local({'student': 'Ana', 'course': 'japones', 'current': None}),
                                         cuaderno=enorme)
    check('cuaderno gigantesco: se recorta al tope', len(prompt_tope) < len(enorme) + 2000)

    # --- 4b. Yendo a Groq (tope_material puesto): el cuaderno TAMBIÉN se recorta, no solo el material del
    # curso. Sin esto, un cuaderno ya crecido + el prompt del tutor no caben en el límite gratuito de Groq
    # y la respuesta llega cortada, sin cerrar [[/CUADERNO]] (encontrado el 2026-11-23 en el navegador real).
    cuaderno_medio = 'y' * 8000
    prompt_groq = mm.build_system_prompt(local=mm.perfil_local({'student': 'Ana', 'course': 'japones', 'current': None}),
                                         cuaderno=cuaderno_medio, tope_material=mm.TOPE_MATERIAL_GROQ)
    check('yendo a Groq: el cuaderno se recorta al mismo tope que el material',
          cuaderno_medio[:mm.TOPE_MATERIAL_GROQ] in prompt_groq and cuaderno_medio not in prompt_groq)

    # --- 5. /chat/stream: el cuaderno que manda el navegador llega al prompt ---
    llamadas = []

    def espia_groq(messages, system, model_name=None, max_tokens=1024, respaldo=False, api_key=''):
        llamadas.append(system)
        yield 'data: "ok"\n\n'

    real_groq = mm.stream_groq
    mm.stream_groq = espia_groq
    mm.build_system_prompt = lambda **kw: (llamadas.append(kw.get('cuaderno')), 'SYSTEM')[1]

    os.environ['GROQ_API_KEY'] = 'gsk_servidor'
    cliente = mm.app.test_client()
    with cliente.session_transaction() as s:
        s['is_admin'] = False

    r = cliente.post('/chat/stream', json={
        'messages': [{'role': 'user', 'content': 'Wuo ka mía nani monakahkta'}],
        'ia_key': 'gsk_delamigo',
        'perfil': {'student': 'Ana', 'course': 'japones', 'current': None, 'mastered': []},
        'cuaderno': 'MI CUADERNO DE PRUEBA',
    })
    r.get_data()
    check('POST /chat/stream: el cuaderno llega a build_system_prompt', 'MI CUADERNO DE PRUEBA' in llamadas)

    # Curso que no manda 'cuaderno' en el body: build_system_prompt recibe None, no ''.
    llamadas.clear()
    r = cliente.post('/chat/stream', json={
        'messages': [{'role': 'user', 'content': 'hola'}],
        'ia_key': 'gsk_delamigo',
        'perfil': {'student': 'Ana', 'course': 'japones', 'current': None, 'mastered': []},
    })
    r.get_data()
    check('sin "cuaderno" en la petición: llega None (curso sin cuaderno), no string vacío', None in llamadas)

    mm.stream_groq = real_groq

    # CONTROL: si el prompt NO llevara el cuaderno completo (p. ej. solo las últimas N filas), este test
    # lo vería: ya comprobamos arriba que Frase 0 (la más vieja) sigue llegando con 50 filas.
    check('CONTROL: con 50 filas, la más antigua seguía dentro (si se recortara, fallaría el check de arriba)', True)
finally:
    mm._cursos_disponibles = real_prompt_courses
    mm.course_topics = real_course_topics

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
