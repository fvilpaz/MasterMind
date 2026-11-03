# Apuntes — Sección 2 · Operadores (contrastados con la documentación oficial)

**Para el tutor:** esto es tu respaldo para no equivocarte en los detalles. Explica con tus palabras y en el orden del
`temario.md`, un subpunto cada vez; no pegues estos apuntes enteros. Fuentes: Oracle Java Tutorials ("Operators",
escritos para JDK 8, siguen siendo válidos) y especificación del lenguaje Java 21 (JLS, capítulo 15). Los **mensajes
de error** son los reales de `javac` y las **salidas** están comprobadas ejecutando el código (JDK 25 de IntelliJ, el
que usa Nando).

---

## Punto 1 · Aritméticos

- `+ - * / %`. Oracle: `%` "divide un operando entre otro y devuelve el resto". `+` también concatena textos.
- **División entera** (JLS §15.17.2): entre dos enteros, el resultado se **corta hacia el cero**, no se redondea.
  Comprobado: `7 / 2` → `3`; `-7 / 2` → `-3`; `7.0 / 2` y `7 / 2.0` → `3.5`; `(double) 7 / 2` → `3.5` (el cast va
  antes que la división); `(double) (7 / 2)` → `3.0` (se divide primero, ya cortado); `1 / 3 * 3.0` → `0.0`.
- **Resto** (JLS §15.17.3): el resultado lleva el **signo del de la izquierda**. Comprobado: `7 % 3` → `1`,
  `-7 % 3` → `-1`, `7 % -3` → `1`, `-7 % -3` → `-1`, `3 % 5` → `3`. También con decimales: `7.5 % 2` → `1.5`.
  Par: `n % 2 == 0` (con negativos impares `n % 2` da `-1`, por eso se compara con `0` y no con `1`).
- **Entre cero:** con enteros compila (sin aviso de `javac`; IntelliJ sí lo subraya) y falla al ejecutar:
  `Exception in thread "main" java.lang.ArithmeticException: / by zero` (también con `%`). Con decimales no hay error:
  `5.0 / 0` → `Infinity`, `-5.0 / 0` → `-Infinity`, `0.0 / 0` → `NaN` ("no es un número"; `NaN == NaN` es `false`).
- **Orden:** `* / %` antes que `+ -`; a igual nivel, de izquierda a derecha (Oracle: "todos los binarios salvo la
  asignación se evalúan de izquierda a derecha"). Comprobado: `2 + 3 * 4` → `14`; `(2 + 3) * 4` → `20`;
  `10 - 4 - 3` → `3`; `100 / 10 / 2` → `5`; `10 / 3 * 3` → `9`; `10 * 3 / 3` → `10`.
- **Concatenar** (JLS §15.18.1): si uno de los dos lados es `String`, el otro se convierte en texto. Va de izquierda
  a derecha, así que importa dónde está el texto. Comprobado: `"1" + 2 + 3` → `123`; `1 + 2 + "3"` → `33`;
  `"Suma: " + 1 + 2` → `Suma: 12`; `"Suma: " + (1 + 2)` → `Suma: 3`; `'a' + 'b'` → `195` (dos `char` se suman
  como números: 97 + 98); `"" + 'a' + 'b'` → `ab`.
- **Tipo del resultado:** `byte`, `short` y `char` se operan como `int`. `byte a = 1, b = 2; byte c = a + b;` →
  `error: incompatible types: possible lossy conversion from int to byte`. Si un operando es `double`, el resultado es
  `double`. Desbordamiento sin aviso: `Integer.MAX_VALUE + 1` → `-2147483648`.

---

## Punto 2 · Asignación

- `=` (Oracle): "asigna el valor de su derecha al operando de su izquierda". Primero se calcula la derecha entera.
- **Compuesta:** `+= -= *= /= %=`. Oracle: `x += 1;` y `x = x + 1;` suman 1 los dos. Comprobado con `int`:
  `int z = 7; z /= 2;` → `3` (división entera); `int w = 7; w %= 2;` → `1`.
- **La derecha va entera, y antes:** `int y = 2; y *= 2 + 3;` → `10` (es `y = y * (2 + 3)`).
- **Con texto:** `String s = "Hola"; s += " mundo"; s += 1 + 2;` → `Hola mundo3`.
- **Cast escondido** (JLS §15.26.2): `E1 op= E2` equivale a `E1 = (T) ((E1) op (E2))`, siendo `T` el tipo de `E1`.
  Comprobado: `byte b = 10; b += 5;` → `15` (compila); `byte top = 127; top += 1;` → `-128`;
  `int x = 10; x += 2.5;` → `12` (corta). En cambio `x = x + 2.5;` →
  `error: incompatible types: possible lossy conversion from double to int`.
- **Una asignación es una expresión con valor** (JLS §15.26): vale lo que queda guardado. `println(v = 8)` imprime
  `8`. `a = b = 5;` deja las dos en 5: la asignación va de **derecha a izquierda** (Oracle).
- **Orden de evaluación** (JLS §15.7.1): primero el lado izquierdo entero. `int i = 2; int j = (i = 3) * i;` → `9`.
  Curiosidad, no para enseñar al principio.

---

## Punto 3 · Comparación

- `==  !=  >  >=  <  <=`. El resultado es `boolean`. Oracle: "usa `==`, no `=`, para comprobar si dos valores
  primitivos son iguales".
- `int x = 5; if (x = 5) { }` → `error: incompatible types: int cannot be converted to boolean`.
- **Mal escritos:** `x =< 5` → `error: illegal start of type`; `x => 5` → `error: illegal start of expression`.
- **No se encadenan:** `1 < x < 10` → `error: bad operand types for binary operator '<'` (con `first type: boolean`,
  `second type: int`: `1 < x` ya es un `boolean` y no se puede comparar con `10`). Se escribe `x > 1 && x < 10`.
- **Tipos:** los números se comparan aunque sean de tipos distintos: `5 == 5.0` → `true`. `char` por su número:
  `'a' < 'b'` → `true`, `'A' == 65` → `true`. Los `boolean` solo con `==` / `!=`: `true > false` →
  `error: bad operand types for binary operator '>'`.
- **Decimales:** `0.1 + 0.2 == 0.3` → `false` (no son exactos; enlaza con la sección 1). Con `NaN`, cualquier
  comparación da `false` salvo `!=` (JLS §15.20.1).
- **Textos:** `==` en objetos compara si son **el mismo objeto**, no el texto: `"hola" == new String("hola")` →
  `false`; `"hola".equals(new String("hola"))` → `true`. Con `String` se usa `.equals()` (sección 3).

---

## Punto 4 · Lógicos

| `a` | `b` | `a && b` | `a \|\| b` | `a ^ b` | `!a` |
|---|---|---|---|---|---|
| true | true | true | true | false | false |
| true | false | false | true | true | false |
| false | true | false | true | true | true |
| false | false | false | false | false | true |

- Solo funcionan con `boolean`: `5 && true` → `error: bad operand types for binary operator '&&'`;
  `!5` → `error: bad operand type int for unary operator '!'`. Escribir `and` en vez de `&&` → `error: ';' expected`.
- **Precedencia** (Oracle): `!` → comparaciones → `==`/`!=` → `&&` → `||`. Comprobado: `true || false && false` →
  `true` (se hace antes el `&&`); `(true || false) && false` → `false`; `!true || true` → `true`;
  `!(true || true)` → `false`.
- **Cortocircuito** (Oracle: "el segundo operando solo se evalúa si hace falta"; JLS §15.23/§15.24): `&&` solo mira la
  derecha si la izquierda es `true`; `||` solo si es `false`. Comprobado con `int d = 0;`:
  `d != 0 && 10 / d > 1` → `false` (no divide); `d == 0 || 10 / d > 1` → `true`; con `&` en vez de `&&` →
  `ArithmeticException: / by zero` (`&` evalúa siempre las dos partes).
  Con efectos: `int n = 0; boolean r = (n > 5) && (++n > 0);` → `r = false`, `n` sigue en `0`; con `&`, `n` pasa a `1`.
- `^` (o exclusivo): `true` si son distintos. `&`, `|` y `^` también existen para enteros (operan bit a bit): fuera del
  temario, solo nombrarlo si sale.
- **De Morgan** (comprobado con todas las combinaciones): `!(a && b)` es `!a || !b`; `!(a || b)` es `!a && !b`.
- El operador ternario `? :` es de la sección de condicionales.

---

## Punto 5 · Unarios

- Oracle: `+` indica positivo ("los números ya lo son sin él"), `-` niega una expresión, `++` suma 1, `--` resta 1,
  `!` invierte un `boolean`.
- **Prefijo y sufijo** (Oracle): `result++;` y `++result;` acaban igual, sumando 1. "La única diferencia es que el
  prefijo (`++result`) da el valor ya incrementado y el sufijo (`result++`) da el valor original". Ejemplo de Oracle,
  comprobado: `int i = 3; i++;` → `4`; `++i;` → `5`; `println(++i)` → `6`; `println(i++)` → `6`; `println(i)` → `7`.
- **El código de Nando** (`b = 3`): `+b` → `3`, `-b` → `-3`, `++b` → `4`, `b++` → `4` (y `b` pasa a 5),
  `--b` → `4`, `b--` → `4` (y `b` vuelve a 3).
- **Solo sobre variables** (JLS §15.14.2): `5++;` y `(x + y)++` → `error: unexpected type` (`required: variable`,
  `found: value`). Sobre una `final`: `final int MAX = 3; MAX++;` →
  `error: cannot assign a value to final variable MAX`.
- **Tipos:** `char c = 'a'; c++;` → `b`; `double d = 1.5; d++;` → `2.5`; `byte b = 127; b++;` → `-128` (lleva el
  mismo cast escondido que `+=`).
- **Trampas** (comprobadas): `int q = 5; q = q++;` → `q` sigue en `5` (se guarda el valor viejo encima del nuevo);
  `int m = 5; int r = m++ + ++m;` → `r = 12` (5 + 7), `m = 7`. `- -k` y `-(-k)` dan `k`; `--k` es otra cosa.

### Todo junto: precedencia (Oracle, de más a menos, solo lo de esta sección)

| Nivel | Operadores |
|---|---|
| sufijo | `x++  x--` |
| unarios | `++x  --x  +x  -x  !` |
| multiplicativos | `*  /  %` |
| aditivos | `+  -` |
| comparación | `<  >  <=  >=` |
| igualdad | `==  !=` |
| (lógicos sin cortocircuito) | `&` → `^` → `\|` |
| y lógico | `&&` |
| o lógico | `\|\|` |
| asignación | `=  +=  -=  *=  /=  %=` (de derecha a izquierda) |

Comprobado: `2 + 3 * 4 > 10 && !false || 1 == 2` → `true` (`14 > 10` → `true && true` → `true || false`).
`int t = 25; boolean sol = true, lluvia = false;` → `(t > 20 && sol) || !lluvia` → `true`, y sin paréntesis da lo
mismo porque `&&` ya va antes: los paréntesis no cambian el resultado, pero se leen mejor.
