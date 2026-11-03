# Temario — Sección 1 · Primeros pasos

Esta carpeta es **una sección entera**: 4 puntos, en este orden, y al final el examen global.
Cada punto: ciclo completo + examen del punto. `[[DOMINADO]]` solo tras aprobar el **examen global**.

Código de Nando de la sección (`src/`): `HelloWorld.java`, `VariablesAndConstants.java`, `DataTypes.java`.

---

## Punto 1 de 4 · Hola Mundo

Subpuntos, **en este orden: de lo práctico a lo teórico** (el examen del punto tiene que pasar por TODOS).
Se empieza por lo que se ve en pantalla; la teoría (cómo se compila, la JVM) va al final y en sencillo.
1. Mostrar texto por pantalla: `System.out.println("Hola");` — lo primero que se enseña, con el ejemplo más simple.
2. `println` (salta de línea al terminar) frente a `print` (no salta): qué sale en pantalla con cada uno.
3. Sintaxis básica: cada instrucción acaba en `;`, el texto va entre comillas dobles, Java distingue mayúsculas
   (`system.out` no compila).
4. Dónde vive ese código: la clase (`public class Nombre { ... }`, el archivo se llama igual: `Nombre.java`) y el
   método `main` (`public static void main(String[] args)`), que es por donde empieza el programa. De momento basta
   con saber que hacen falta y dónde va cada cosa; `public`, `static` y `void` se entienden más adelante.
5. Secuencias de escape dentro del texto: `\n`, `\t`, `\"`, `\\`
   (en el código de Nando: `"\\___/"` para dibujar una sola barra).
6. Leer un error de compilación: qué dice el mensaje y en qué línea (falta un `;`, comillas sin cerrar, clase con
   otro nombre que el archivo).
7. Cómo se ejecuta: `javac Nombre.java` + `java Nombre` (desde Java 11 también `java Nombre.java`).
8. Qué pasa por debajo, en sencillo: el `.java` se traduce a bytecode (`.class`) y la JVM lo ejecuta (por eso Java
   funciona igual en Windows, Mac o Linux).

Ejemplo real: `HelloWorld.java` (un `println` y un dibujo con varios `println` y una barra escapada).
Fuentes: Oracle Hello World https://docs.oracle.com/javase/tutorial/getStarted/application/index.html ·
W3Schools Syntax https://www.w3schools.com/java/java_syntax.asp · Output https://www.w3schools.com/java/java_output.asp

---

## Punto 2 de 4 · Comentarios

Subpuntos:
1. Qué es un comentario: texto que el compilador ignora; no cambia lo que hace el programa.
2. Para qué sirve: explicar el **porqué** de una decisión (no repetir lo que el código ya dice), dejar notas
   (`TODO`) y desactivar código temporalmente sin borrarlo.
3. De una línea: `//` — desde ahí hasta el final de la línea; solo o detrás de una instrucción.
4. De bloque: `/* ... */` — varias líneas; **no se pueden anidar** (el primer `*/` lo cierra).
5. De documentación (Javadoc): `/** ... */` encima de clases y métodos; `@param` y `@return`; la herramienta
   `javadoc` genera la documentación HTML.
6. Trampas: `//` dentro de una cadena (`"http://..."`) no es comentario; comentar una línea a medias puede dejar el
   código sin compilar (una llave o un `;` que se queda fuera).
7. Buenas prácticas: cortos y al día; un comentario que miente es peor que ninguno; mejor un nombre claro que un
   comentario que lo explique.

Ejemplo real: el `//` detrás de una instrucción en `HelloWorld.java`; en `VariablesAndConstants.java`, comentarios
de sección (`// Variables`) y una línea desactivada con su explicación (`// name = 37 no funcionaria…`).
Fuentes: W3Schools Comments https://www.w3schools.com/java/java_comments.asp ·
JLS comentarios https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.7

---

## Punto 3 de 4 · Variables y constantes

Subpuntos:
1. Qué es una variable: un nombre para un espacio de memoria que guarda un valor de un **tipo** concreto.
2. Declarar, inicializar y reasignar: `int age;` · `int age = 42;` · `age = 43;` (al reasignar no se repite el tipo).
3. El tipo manda: a un `String` no se le puede asignar `37`, pero sí `"37"` (ejemplo del código de Nando).
4. Una variable local hay que inicializarla antes de usarla (si no, error de compilación).
5. Nombres: reglas (no empezar por número, sin espacios, no palabras reservadas como `class` o `int`, distingue
   mayúsculas) y convención `camelCase` (`likeProgramming`).
6. `var` (Java 10+): el compilador deduce el tipo; solo en variables locales y con valor inicial; el tipo queda fijo
   (`var year = 1984;` es `int` para siempre).
7. Constantes con `final`: no se pueden reasignar (error de compilación); convención `MAYUSCULAS_CON_GUIONES`.
8. Mostrar variables: concatenar con `+` en `println`, `print` seguido, y `printf` con `%s`/`%d`.

Ejemplo real: `VariablesAndConstants.java` (`String`, `char`, `int`, `boolean`, `var`, `final String EMAIL` y las
tres formas de imprimir; tiene una errata en un texto, "constamte", que sirve para un `/read`).
Fuentes: Oracle Variables https://docs.oracle.com/javase/tutorial/java/nutsandbolts/variables.html ·
W3Schools Variables https://www.w3schools.com/java/java_variables.asp · final https://www.w3schools.com/java/java_variables_final.asp

---

## Punto 4 de 4 · Tipos de datos primitivos

Subpuntos:
1. Qué es un tipo primitivo: un valor simple guardado directamente (no un objeto). Java tiene **8**.
2. Enteros: `byte` (8 bits), `short` (16), `int` (32, el normal), `long` (64, literal con `L`: `3000000000L`). Cuál
   elegir y qué pasa si no cabe (literal demasiado grande no compila; desbordamiento al operar).
3. Decimales: `double` (el normal) y `float` (literal con `f`: `1.77f`; sin la `f` no compila). No son exactos
   (`0.1 + 0.2`).
4. `char`: **un** carácter entre comillas simples (`'a'`); `"a"` es un `String`. Por dentro es un número (Unicode).
5. `boolean`: solo `true` o `false` (no `1`/`0`).
6. `String` **no** es primitivo: es una clase (mayúscula, tiene métodos). Ejemplo de Nando:
   `myString.getClass().getSimpleName()`.
7. Conversiones: de pequeño a grande es automática (`int` → `long` → `double`); de grande a pequeño, con cast
   (`(int) 3.9` da `3`: se pierde la parte decimal).
8. Una variable local primitiva no tiene valor hasta que se lo das (enlaza con el punto 3).

Ejemplo real: `DataTypes.java` (`int`, `double`, `char`, `boolean` reasignado, `String`, `getClass().getSimpleName()`;
deja anotado `// float, long, byte` sin ejemplo: buen hueco para un ejercicio).
Fuentes: Oracle Primitive Data Types https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html ·
W3Schools Data Types https://www.w3schools.com/java/java_data_types.asp · Casting https://www.w3schools.com/java/java_type_casting.asp

---

## Preguntas de repaso de la sección (Nando tiene que saber responderlas)

Hazlas **de vez en cuando**, con tus palabras y mezcladas con tu repertorio: al cerrar un punto, al volver de una
pausa o como calentamiento. Solo las de puntos **ya explicados**. También entran en el test del examen global.
- Qué pasa si a una variable `int` le asignas un texto (`String`): no compila, los tipos no casan.
- Qué tipo usar para un número entero (`int`) y para un valor verdadero/falso (`boolean`).
- Qué tipo usar para guardar texto (`String`).
- Diferencia entre `var` y escribir el tipo (`int`): con `var` lo deduce el compilador, pero el tipo queda igual de fijo.
- Para qué sirve el método `main`: es por donde empieza a ejecutarse el programa.
- Reconocer, entre varias opciones, una declaración de variable bien escrita (tipo, nombre, `=`, valor, `;`).
- Con qué palabra se declara una constante (`final`) y qué pasa si intentas cambiarle el valor (error de compilación).
- Con qué instrucción se imprime en consola (`System.out.println`).

---

## EXAMEN GLOBAL · Primeros pasos (solo tras aprobar los 4 puntos)

Entran los 4 puntos, mezclados.
- **Parte 1 · Test de 10 preguntas**, una a una: al menos 2 por punto y alguna que los combine (p. ej. "¿compila
  esto?" con un `final`, un `char` y un comentario mal cerrado). 4 opciones o respuesta corta; que razone la
  respuesta, no solo la letra.
- **Parte 2 · Un programa completo** escrito por él que use todo a la vez: clase y `main`, Javadoc de la clase,
  variables de varios tipos, una constante, una conversión con cast y salida con `println` y `printf`.
- **Parte 3 · Cambio de requisito** sobre SU programa (un dato inesperado o un tipo que ya no vale).

Aprobado: test con al menos 8 de 10 **y** programa correcto **y** cambio resuelto. Si falla un punto concreto, se le
dice cuál y se repasa ese punto antes de repetir (otras preguntas, no las mismas). Aprobado → `[[DOMINADO]]`.
