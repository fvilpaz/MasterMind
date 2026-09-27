# Pruebas de caracterización del saludo inicial (_resolve_greet en web/app.py).
# Fijan lo que hace hoy para poder tocarlo sin miedo (p. ej. al traducir los textos, punto 12
# del ROADMAP). Sin dependencias: se lanza con
#     python trainer/tests/test_greet.py
# y devuelve código 0 si todo pasa, 1 si algo falla.
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')   # la consola de Windows no pinta ✅/❌ sin esto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'web'))
import app as mm  # noqa: E402


def greet_msgs():
    return [{'role': 'user', 'content': '__greet__'}]


fallos = 0


def check(nombre, cond):
    global fallos
    print(('✅ ' if cond else '❌ ') + nombre)
    if not cond:
        fallos += 1


# 1. Admin → recibe las instrucciones de admin (con lo esencial que no debe perderse)
out = mm._resolve_greet(greet_msgs(), True, '')[-1]['content']
check('admin: saludo por su nombre', 'Saluda al estudiante por su nombre' in out)
check('admin: recuerda dónde quedamos (log)', 'en qué punto quedamos' in out)
check('admin: pregunta pomodoros', '2 pomodoros' in out and '4 pomodoros' in out)
check('admin: ya no queda __greet__', out != '__greet__')

# 2. Invitado con nombre → su nombre sustituye a 'aprendiz'
out = mm._resolve_greet(greet_msgs(), False, 'Ana')[-1]['content']
check("invitado con nombre: aparece 'Ana'", "'Ana'" in out)
check("invitado con nombre: ya NO dice 'aprendiz'", "'aprendiz'" not in out)

# 3. Invitado sin nombre → 'aprendiz'
out = mm._resolve_greet(greet_msgs(), False, '')[-1]['content']
check("invitado sin nombre: le llama 'aprendiz'", "'aprendiz'" in out)
check('invitado: pregunta pomodoros', '2 pomodoros' in out)

# 4. Un mensaje normal NO se toca
msgs = [{'role': 'user', 'content': 'hola, ¿qué es un puntero?'}]
check('mensaje normal: intacto', mm._resolve_greet(msgs, True, '')[-1]['content'] == 'hola, ¿qué es un puntero?')

# 5. Estilo al azar (GREET_STYLES) añadido al final, sin tocar el texto de GREET_*
out = mm._resolve_greet(greet_msgs(), True, '')[-1]['content']
check('estilo: admin conserva sus instrucciones al principio', out.startswith(mm.GREET_ADMIN))
check('estilo: termina con uno de GREET_STYLES', any(out.endswith(f"arranca {s}.") for s in mm.GREET_STYLES))
vistos = {mm._resolve_greet(greet_msgs(), True, '')[-1]['content'] for _ in range(60)}
check(f'estilo: varía entre llamadas ({len(vistos)} distintos en 60)', len(vistos) > 1)
out = mm._resolve_greet(greet_msgs(), False, 'Ana')[-1]['content']
check("estilo: invitado con nombre tiene 'Ana' Y el estilo", "'Ana'" in out and 'Esta vez, arranca' in out)
msgs = [{'role': 'user', 'content': 'hola'}]
check('estilo: mensaje normal sigue SIN estilo', mm._resolve_greet(msgs, True, '')[-1]['content'] == 'hola')

# 6. CONTROL: el test tiene que poder fallar. `str.replace` no da error si no encuentra su texto:
#    si alguien cambia "llámale 'aprendiz'" en GREET_GUEST, el nombre del invitado se pierde en
#    silencio. Se rompe a propósito y el test debe notarlo.
original = mm.GREET_GUEST
mm.GREET_GUEST = original.replace("llámale 'aprendiz'", "llámalo 'aprendiz'")
out = mm._resolve_greet(greet_msgs(), False, 'Ana')[-1]['content']
check("CONTROL: con el texto roto, 'Ana' ya NO aparece (el test lo detecta)", "'Ana'" not in out)
mm.GREET_GUEST = original

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} FALLO(S)'}")
sys.exit(1 if fallos else 0)
