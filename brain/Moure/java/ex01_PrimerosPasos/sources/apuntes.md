# Apuntes — Sección 1 · Primeros pasos (contrastados con la documentación oficial)

**Para el tutor:** esto es tu respaldo para no equivocarte en los detalles. Explica con tus palabras y en el orden del
`temario.md`, un subpunto cada vez; no pegues estos apuntes enteros. Fuentes: Oracle Java Tutorials (escritos para
JDK 8, siguen siendo válidos), especificación del lenguaje Java 21 (JLS), API de `java.util.Formatter` y JEP 330.
Los **mensajes de error** son los reales de `javac` (comprobados compilando cada caso) y las **salidas** están
comprobadas ejecutando el código. El proyecto de Nando usa Java 21 o superior.

---

## Punto 1 · Hola Mundo

```java
public class HolaMundo {
    public static void main(String[] args) {
        System.out.println("Hola Mundo");
    }
}
```

- **Mostrar texto:** `System.out.println("…")` escribe el texto en la salida estándar (la consola) y salta de línea.
  `System.out.print("…")` lo escribe **sin** saltar. `System` es una clase de la biblioteca estándar de Java.
  Comprobado: `print("Hola ")` seguido de `println("Mundo")` muestra `Hola Mundo` en una sola línea.
- **Sintaxis:** cada instrucción termina en `;` y los bloques van entre `{ }`. Java distingue mayúsculas y minúsculas.
  - Sin `;` → `error: ';' expected`.
  - `system.out.println(…)` (con minúscula) → `error: package system does not exist`.
- **Texto entre comillas dobles** (`"Hola"`, un `String`). Las comillas simples son para **un solo carácter** (`'H'`):
  `println('Hola')` → `error: unclosed character literal`.
- **La clase y el archivo:** todo el código vive dentro de una clase (`class Nombre { … }`). Si la clase es `public`,
  el archivo tiene que llamarse igual: `public class Distinta` dentro de otro archivo →
  `error: class Distinta is public, should be declared in a file named Distinta.java`.
- **El método `main`:** `public static void main(String[] args)` es el punto de entrada: el programa empieza ahí.
  Oracle: `public` y `static` pueden ir en cualquier orden, pero la convención es `public static`. `args` recibe lo
  que se escribe detrás del nombre al ejecutar (`java App uno dos`); el nombre `args` es costumbre, no obligatorio.
  Al principio basta con saber que hace falta y dónde va; `public`, `static` y `void` se entienden más adelante.
- **Secuencias de escape** dentro de un texto: `\n` salto de línea, `\t` tabulador, `\"` comillas dobles,
  `\'` comilla simple, `\\` una barra invertida. Existen otras (`\r`, `\b`, `\f`, `\s`), poco usadas. Cualquier otra
  letra tras `\` → `error: illegal escape character`.
  Comprobado: `println("Dijo: \"Hola\"")` → `Dijo: "Hola"`; `println("C:\\fotos")` → `C:\fotos`.
  **Trampa:** `"C:\fotos"` (una sola barra) **compila**, porque `\f` es una secuencia válida (salto de página), pero no
  muestra lo que esperas.
- **Compilar y ejecutar:** `javac App.java` crea `App.class` (bytecode); `java App` lo ejecuta, **sin** extensión.
  Desde Java 11 (JEP 330) también vale `java App.java`: compila en memoria y ejecuta, sin dejar `.class` en disco
  (comprobado). Ejecuta la primera clase del archivo, que debe tener el `main`.
- **Qué pasa por debajo:** el `.class` no es código de tu procesador, sino bytecode; lo ejecuta la **JVM** (máquina
  virtual de Java). Por eso el mismo `.class` funciona en Windows, Mac o Linux si tienen una JVM.
- **Leer un error:** `App.java:7: error: ';' expected` → archivo `App.java`, **línea 7**, y qué falla.

---

## Punto 2 · Comentarios

- El compilador **ignora** los comentarios: no cambian lo que hace el programa. Tres formas (Oracle):
  - `// texto` → desde `//` hasta el final de la línea.
  - `/* texto */` → todo lo que hay entre `/*` y `*/`, aunque ocupe varias líneas.
  - `/** texto */` → **comentario de documentación** (Javadoc). Se pone encima de clases y métodos; la herramienta
    `javadoc` lo usa para generar la documentación en HTML. Etiquetas básicas: `@param` (un parámetro) y `@return`
    (lo que devuelve).
- **Reglas exactas** (JLS §3.7):
  - **No se anidan:** el primer `*/` cierra el comentario. `/* uno /* dos */ tres */` deja `tres */` fuera, como
    código, y no compila (comprobado: `error: <identifier> expected`).
  - Dentro de un `//`, los `/*` y `*/` no significan nada. Dentro de un `/* */`, el `//` tampoco.
  - **Dentro de un texto no hay comentarios:** en `"http://web.com"` el `//` es parte del texto.
- **Para qué sirven:** explicar el **porqué** de una decisión (no repetir lo que el código ya dice), dejar notas
  (`// TODO: …`) y desactivar una línea sin borrarla. Un comentario que miente es peor que ninguno.

---

## Punto 3 · Variables y constantes

- **Variable:** un nombre para guardar un valor de un **tipo** concreto. Ahora se usan **variables locales**
  (dentro de `main`); las de las clases (campos) llegan con la POO.
- **Declarar, dar valor y cambiarlo:** `int edad;` · `int edad = 42;` · `edad = 43;` (al cambiarlo no se repite el
  tipo).
- **Una variable local hay que inicializarla antes de usarla:** Java no le pone valor por defecto.
  `int x; System.out.println(x);` → `error: variable x might not have been initialized`.
- **El tipo manda:** `int edad = "42";` → `error: incompatible types: String cannot be converted to int`.
- **Nombres** (Oracle): letras, dígitos, `$` y `_`, sin empezar por dígito y sin espacios; no pueden ser palabras
  reservadas (`class`, `int`, `public`…); `edad` y `Edad` son variables distintas. **Convenciones:** empezar por letra
  (no por `$` ni `_`), palabras completas en vez de abreviaturas, una palabra en minúsculas (`edad`) y varias en
  `camelCase` (`likeProgramming`, `gearRatio`).
- **`var`** (desde Java 10): el compilador deduce el tipo del valor inicial. `var year = 1984;` es un `int` para
  siempre: el tipo **no cambia** después. Solo para variables **locales con valor inicial** (y en los `for`); no
  para campos, parámetros ni tipos de retorno.
  - `var x;` → `error: cannot infer type for local variable x`. Tampoco vale `var x = null;`.
  - `var` no es palabra reservada, sino un "nombre de tipo reservado": `var var = 1;` compila, pero no se hace.
- **Constantes con `final`:** solo se les puede dar valor **una vez**.
  `final int MAX = 3; MAX = 4;` → `error: cannot assign a value to final variable MAX`.
  Se puede declarar y darle valor después, una sola vez (`final int MAX; MAX = 3;`). Convención: **MAYÚSCULAS con
  guion bajo** (`MAX_INTENTOS`, `EMAIL`).
- **Mostrar variables:**
  - Concatenar con `+`: `"Tengo " + edad + " años"`.
  - `printf` con huecos: `%s` texto (vale cualquier cosa), `%d` número entero, `%f` decimal (6 decimales por defecto),
    `%.2f` con 2 decimales, `%n` salto de línea, `%%` un `%`. Comprobado:
    `printf("Tengo %d años y me llamo %s%n", 42, "Nando")` → `Tengo 42 años y me llamo Nando`.
  - `%d` con un texto **compila**, pero **falla al ejecutar**: `IllegalFormatConversionException`.
  - **Ojo:** `%.2f` usa la coma o el punto según el idioma del sistema. En el PC de Nando, `printf("%.2f", 3.14159)`
    muestra `3,14`.

---

## Punto 4 · Tipos de datos primitivos

| Tipo | Tamaño | Rango / valores |
|---|---|---|
| `byte` | 8 bits | -128 a 127 |
| `short` | 16 bits | -32.768 a 32.767 |
| `int` | 32 bits | -2.147.483.648 a 2.147.483.647 (el entero "normal") |
| `long` | 64 bits | unos ±9,2 trillones |
| `float` | 32 bits | decimal, unas 7 cifras de precisión |
| `double` | 64 bits | decimal, unas 15-16 cifras de precisión (el decimal "normal") |
| `char` | 16 bits | un carácter Unicode (de `'\u0000'` a `'\uffff'`) |
| `boolean` | — | solo `true` o `false` |

(Las precisiones de `float` y `double` son aproximadas: Oracle remite a la especificación.)

- **Literales:**
  - Un número entero escrito tal cual es `int`. Para `long`, con `L` (mejor mayúscula: la `l` se confunde con un 1).
    `long n = 3000000000;` → `error: integer number too large` (sin la `L`, no cabe en un `int`).
  - Un decimal escrito tal cual es `double`. Para `float`, con `f`:
    `float f = 1.77;` → `error: incompatible types: possible lossy conversion from double to float`.
  - `char` con comillas simples (`'a'`); `"a"` es un `String`.
  - Guiones bajos para leer mejor: `1_000_000` (entre dígitos; no al principio ni al final, ni junto al punto
    decimal o a la `L`/`f`).
  - Prefijos: `0x1A` hexadecimal, `0b1010` binario.
- **`byte b = 42;` compila** (es una constante que cabe). `byte b = 200;` no (no cabe). Con una variable,
  `int x = 42; byte b = x;` tampoco compila, aunque quepa: hace falta un cast. En los dos casos:
  `error: incompatible types: possible lossy conversion from int to byte`.
- **Desbordamiento sin aviso:** `Integer.MAX_VALUE + 1` da `-2147483648`: no hay error, da la vuelta (comprobado).
- **Los decimales no son exactos:** `0.1 + 0.2` da `0.30000000000000004` (comprobado).
- **`char` es un número por dentro:** `'A' + 1` da `66` (comprobado).
- **`String` no es primitivo:** es una clase (por eso va en mayúscula y tiene métodos) y es **inmutable** (no se
  modifica, se crea otro). En el código de Nando, `getClass().getSimpleName()` lo muestra.
- **Conversiones:**
  - **Automáticas, de pequeño a grande** (ampliación): `byte` → `short` → `int` → `long` → `float` → `double`, y
    `char` → `int`. Comprobado: `long l = 42; double d = l;` → `42.0`. Ojo: `int` o `long` a `float`, y `long` a
    `double`, pueden perder precisión en números muy grandes.
  - **De grande a pequeño, con cast** (estrechamiento), y se puede perder información:
    `(int) 3.9` → `3`, `(int) -3.9` → `-3` (corta hacia el cero, no redondea); `(byte) 200` → `-56` (se queda con los
    bits de abajo). Comprobado.
- **Valores por defecto** (`0`, `false`, `null`…) solo los tienen los **campos** de una clase, no las variables
  locales (enlaza con el punto 3).
