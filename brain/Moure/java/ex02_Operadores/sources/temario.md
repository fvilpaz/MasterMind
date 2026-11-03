# Temario — Sección 2 · Operadores

Esta carpeta es **una sección entera**: 5 puntos, en este orden, y al final el examen global.
Cada punto: ciclo completo + examen del punto. `[[DOMINADO]]` solo tras aprobar el **examen global**.

Código de Nando de la sección (`src/`): `Operators.java` (los cinco tipos de operadores, en el orden del curso).
En su proyecto de IntelliJ (no en `brain/`), Nando hizo los ejercicios del curso del 1 al 7 y **dejó sin hacer** los
tres últimos: añadir una negación, 3 ejemplos de operadores unarios y combinar aritméticos, de comparación y lógicos
en una misma expresión. Son buenos ejercicios para los puntos 4 y 5 y para el examen global.

---

## Punto 1 de 5 · Operadores aritméticos

Subpuntos, **en este orden: de lo práctico a lo teórico** (el examen del punto tiene que pasar por TODOS).
1. Los cinco: `+` suma, `-` resta, `*` multiplicación, `/` división, `%` resto. Guardar el resultado en una variable
   e imprimirlo (`int suma = a + b;`).
2. División entera: entre dos `int`, `/` corta los decimales (`7 / 2` da `3`). Para tener decimales, que uno de los
   dos sea decimal (`7.0 / 2` o `(double) 7 / 2` dan `3.5`; `(double) (7 / 2)` da `3.0`: el corte ya se hizo).
3. El resto `%`: qué sobra al dividir (`7 % 3` da `1`). Usos: saber si un número es par (`n % 2 == 0`) o si es
   múltiplo de otro. Con negativos, el resto lleva el signo del de la izquierda (`-7 % 3` da `-1`).
4. Orden de las operaciones: `*`, `/` y `%` antes que `+` y `-` (`2 + 3 * 4` da `14`); los paréntesis mandan
   (`(2 + 3) * 4` da `20`); a igual nivel, de izquierda a derecha (`10 / 3 * 3` da `9`, no `10`).
5. `+` con texto concatena: en cuanto aparece un `String`, lo que sigue se pega como texto (`"Suma: " + 1 + 2` da
   `Suma: 12`; con paréntesis, `Suma: 3`; `1 + 2 + "3"` da `33`). Ojo: `'a' + 'b'` da `195` (dos `char` se suman como
   números).
6. Dividir entre cero: con enteros **compila** pero falla al ejecutar (`ArithmeticException: / by zero`, también con
   `%`); con decimales no falla: da `Infinity` o `NaN`.
7. Tipos del resultado (lo más teórico): `byte`/`short`/`char` se operan como `int` (`byte c = a + b;` no compila);
   si uno es `double`, el resultado es `double`. El desbordamiento no avisa (enlaza con la sección 1).

Ejemplo real: `Operators.java`, bloque "Aritméticos" (`var a = 6; var b = 3;` y las cinco operaciones: 9, 3, 18, 2, 0).
Fuentes: Oracle https://docs.oracle.com/javase/tutorial/java/nutsandbolts/op1.html ·
JLS 21 §15.17 https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.17 ·
W3Schools https://www.w3schools.com/java/java_operators_arithmetic.asp

---

## Punto 2 de 5 · Operadores de asignación

Subpuntos:
1. `=` guarda el valor de la derecha en la variable de la izquierda; primero se calcula la derecha (`a = b * 2;`).
   **No** es "igual a": eso es `==` (punto 3).
2. Asignación compuesta: `+=`, `-=`, `*=`, `/=`, `%=`. `x += 5` es lo mismo que `x = x + 5`. Leerla y escribirla.
3. Lo de la derecha se calcula entero antes: `y *= 2 + 3` con `y = 2` da `10` (es `y = y * (2 + 3)`), no `7`.
4. `+=` con texto añade al final: `s += " mundo";`. Y `s += 1 + 2` añade `3` (la derecha se calcula antes).
5. La compuesta lleva un cast escondido: `byte b = 10; b += 5;` compila, `b = b + 5;` no; con `int x = 10;`,
   `x += 2.5` deja `12` (corta los decimales) y `x = x + 2.5` no compila.
6. Una asignación también da un valor: `a = b = 5;` deja las dos en 5 (se lee de derecha a izquierda). Se puede, pero
   se lee mal: mejor una por línea.

Ejemplo real: `Operators.java`, bloque "Asignación" (salidas 3, 6, 7, 6, 12, 6; el último `a %= 2` no se imprime:
buena pregunta de `/read`, ¿cuánto vale `a` después?).
Fuentes: Oracle op1 (arriba) · JLS 21 §15.26 https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.26 ·
W3Schools https://www.w3schools.com/java/java_operators_assign.asp

---

## Punto 3 de 5 · Operadores de comparación

Subpuntos:
1. Los seis: `==` igual, `!=` distinto, `>` mayor, `<` menor, `>=` mayor o igual, `<=` menor o igual.
2. El resultado es un `boolean` (`true`/`false`): se puede imprimir o guardar (`boolean mayor = edad >= 18;`).
3. `=` frente a `==`: `if (x = 5)` no compila con un `int` (`int cannot be converted to boolean`).
4. Se escriben así y no al revés: `>=` y `<=` (`=<` y `=>` no existen); un rango no se encadena
   (`1 < x < 10` no compila: se escribe `x > 1 && x < 10`, que es el punto 4).
5. Qué se puede comparar: números entre sí aunque sean de tipos distintos (`5 == 5.0` es `true`), `char` por su número
   (`'a' < 'b'`); los `boolean` solo con `==` y `!=` (`true > false` no compila).
6. Trampas: decimales con `==` (`0.1 + 0.2 == 0.3` es `false`); y textos: `==` en un `String` no compara el texto,
   se usa `.equals()` (solo avisarlo: los `String` son la sección 3).

Ejemplo real: `Operators.java`, bloque "Relacionales" (con `a = 0` y `b = 3`; que adivine cada `true`/`false` antes
de ejecutarlo).
Fuentes: Oracle https://docs.oracle.com/javase/tutorial/java/nutsandbolts/op2.html ·
JLS 21 §15.20 y §15.21 · W3Schools https://www.w3schools.com/java/java_operators_comparison.asp

---

## Punto 4 de 5 · Operadores lógicos

Subpuntos:
1. `&&` (y): `true` solo si los dos lo son. `||` (o): `true` si al menos uno lo es. `!` (no): le da la vuelta.
   Las tablas de verdad con `true`/`false`.
2. Con comparaciones, que es como se usan: `edad >= 18 && cualificado`, rangos (`nota >= 5 && nota <= 10`).
3. `!` delante de un paréntesis: `!(3 > 2 || 5 > 2)`. Sin paréntesis no vale: `!5` no compila.
4. Precedencia: `!` primero, luego las comparaciones, luego `&&` y al final `||`. `a || b && c` es `a || (b && c)`:
   `true || false && false` da `true`, `(true || false) && false` da `false`. Los paréntesis lo dejan claro.
5. Cortocircuito: `&&` no mira la derecha si la izquierda es `false`; `||` no la mira si la izquierda es `true`.
   Uso real: `d != 0 && 10 / d > 1` no divide entre cero. Si a la derecha hay un `++`, no se ejecuta.
6. `&`, `|` (sin cortocircuito: evalúan siempre las dos partes) y `^` (o exclusivo: `true` si son distintos).
   Existen; en el día a día se usa `&&` y `||`.
7. Negar una condición compuesta (De Morgan): `!(a && b)` es `!a || !b` y `!(a || b)` es `!a && !b`.

Ejemplo real: `Operators.java`, bloques `&&`, `||` y `!` (las cuatro combinaciones de cada uno, con comparaciones).
Fuentes: Oracle op2 (arriba) · JLS 21 §15.23 y §15.24 · W3Schools https://www.w3schools.com/java/java_operators_logical.asp

---

## Punto 5 de 5 · Operadores unarios

Subpuntos:
1. Qué es un unario: actúa sobre **un** valor. `+` (positivo, no cambia nada) y `-` (cambia el signo: `-b`).
2. `++` suma 1 y `--` resta 1 a una variable. Solos en una línea (`i++;` o `++i;`) hacen lo mismo.
3. Prefijo y sufijo dentro de una expresión: `++b` suma y **luego** da el valor; `b++` da el valor **y luego** suma.
   Con `b = 3`: `println(++b)` saca `4`; después `println(b++)` saca `4` y `b` queda en `5`.
4. Solo sirven sobre una variable: `5++` y `(x + y)++` no compilan; tampoco sobre una constante `final`.
5. Trampas: `x = x++;` deja `x` igual; `m++ + ++m` con `m = 5` da `12`. Se entienden, pero no se escriben así.
6. También en `char` (`'a'` pasa a `'b'`) y en `double` (`1.5` pasa a `2.5`); en `byte`, `127` pasa a `-128`.
7. Todo junto: la tabla de precedencia completa (unarios → `* / %` → `+ -` → comparación → `==`/`!=` → `&&` → `||` →
   asignación) y leer expresiones que mezclan todo: `2 + 3 * 4 > 10 && !false || 1 == 2`.

Ejemplo real: `Operators.java`, bloque "Unarios" (salidas 3, -3, 4, 4, 4, 4; los dos comentarios `// b+` y `// b-`
muestran que `+` y `-` van delante).
Fuentes: Oracle op1 (arriba) · precedencia https://docs.oracle.com/javase/tutorial/java/nutsandbolts/operators.html ·
JLS 21 §15.14 y §15.15 · W3Schools https://www.w3schools.com/java/java_operators_precedence.asp

---

## Preguntas de repaso de la sección (Nando tiene que saber responderlas)

Hazlas **de vez en cuando**, con tus palabras y mezcladas con tu repertorio: al cerrar un punto, al volver de una
pausa o como calentamiento. Solo las de puntos **ya explicados**. También entran en el test del examen global.
- Qué hace `+=` (suma lo de la derecha a la variable y lo guarda en ella).
- Reconocer cuál es un operador lógico entre varios símbolos (`&&`, `||`, `!` frente a `+`, `=`, `%`…).
- Qué hace `!=` (comprueba si dos valores son distintos y da un `boolean`).
- Con qué operador se niega un `boolean` (`!`).
- Qué da `true || false` (`true`: basta con que uno lo sea).
- Qué operador comprueba "menor o igual" (`<=`).
- Qué operador da el resto de una división (`%`).
- Qué hace `==` (compara si dos valores son iguales; no asigna, eso es `=`).
- Con qué operador se suman dos números (`+`).
- Qué le hace `++` a una variable (le suma 1; y la diferencia entre ponerlo delante o detrás).

---

## EXAMEN GLOBAL · Operadores (solo tras aprobar los 5 puntos)

Entran los 5 puntos, mezclados.
- **Parte 1 · Test de 10 preguntas**, una a una: al menos 2 por punto y varias que combinen. Muchas del tipo "¿qué
  imprime?" o "¿compila?" (`"Total: " + 2 * 3`, `x += 2.5` con un `int`, `a || b && c`, `b++` dentro de un
  `println`). 4 opciones o respuesta corta; que razone la respuesta, no solo la letra.
- **Parte 2 · Un programa completo** escrito por él: con unos datos (precio, unidades, edad, un `boolean`), calcula
  con los cinco aritméticos, actualiza con asignaciones compuestas, usa `++`, y decide con comparaciones y lógicos
  combinados (`&&`, `||`, `!`, con paréntesis) e imprime cada resultado con un texto. Son los ejercicios 8–10 que
  dejó sin hacer.
- **Parte 3 · Cambio de requisito** sobre SU programa (el precio pasa a tener decimales, una división que puede ser
  entre cero, una condición nueva que hay que negar).

Aprobado: test con al menos 8 de 10 **y** programa correcto **y** cambio resuelto. Si falla un punto concreto, se le
dice cuál y se repasa ese punto antes de repetir (otras preguntas, no las mismas). Aprobado → `[[DOMINADO]]`.
