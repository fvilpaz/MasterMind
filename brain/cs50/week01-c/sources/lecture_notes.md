# Lecture 1 — C

## Índice
- [Welcome!](#welcome)
- [Source Code](#source-code)
- [Visual Studio Code for CS50](#visual-studio-code-for-cs50)
- [Hello World](#hello-world)
- [From Scratch to C](#from-scratch-to-c)
- [Header Files and CS50 Manual Pages](#header-files-and-cs50-manual-pages)
- [Hello, You](#hello-you)
- [Linux](#linux)
- [Conditionals](#conditionals)
- [Types](#types)
- [Format Codes](#format-codes)
- [Variables](#variables)
- [compare.c](#comparec)
- [agree.c](#agreec)
- [Loops and meow.c](#loops-and-meowc)
- [Functions](#functions)
- [Correctness, Design, Style](#correctness-design-style)
- [Mario](#mario)
- [Operators](#operators)
- [Summing Up](#summing-up)

---

## Welcome!

In our previous session, we learned about **Scratch**, a visual programming language.

Learning computer science concepts can be quite challenging. Indeed, it can feel like you are drinking from a firehose. Remember: What is ultimately important is the gains you experience over these coming weeks and months through your hard work and study in this course.

All the essential programming concepts presented in Scratch will be utilized as you learn how to program any programming language. **Functions, conditionals, loops, and variables** found in Scratch are fundamental building blocks that you will find in any programming language.

---

## Source Code

Machines only understand **binary**. Where humans write **source code** — a list of instructions that is human readable — machines only understand **machine code**: a pattern of ones and zeros that produces a desired effect.

We convert source code into machine code using a special piece of software called a **compiler**. Today, we introduce a compiler that converts C source code into machine code.

```
source code  →  compiler  →  machine code
```

Today, in addition to learning how to program, you will be learning how to write **good code**.

---

## Visual Studio Code for CS50

The text editor used for this course is **Visual Studio Code** (VS Code), accessible at [cs50.dev](https://cs50.dev).

VS Code has all the software required for the course pre-loaded. The IDE is divided into:

- **File explorer** — on the left side
- **Text editor** — in the middle
- **Terminal / CLI** — at the bottom, to send commands to the computer

Because this IDE is pre-configured with all necessary software, you should use it to complete all assignments.

---

## Hello World

Three commands to write, compile, and run your first program:

```bash
code hello.c   # creates and opens the file
make hello     # compiles it into an executable
./hello        # runs the program
```

In the text editor, write:

```c
// A program that says hello to the world

#include <stdio.h>

int main(void)
{
    printf("hello, world\n");
}
```

> `printf` outputs a line of text. The `\n` creates a new line. Every character has a purpose — if you type it incorrectly, the program will not compile.

After `make hello` (no errors), run `./hello` → it prints `hello, world`.

---

## From Scratch to C

In Scratch, the `say` block displays text. In C, `printf` does exactly this:

```c
printf("hello, world\n");
```

### Escape characters

| Sequence | Effect |
|----------|--------|
| `\n` | New line |
| `\r` | Return to start of line |
| `\"` | Print a double quote |
| `\'` | Print a single quote |
| `\\` | Print a backslash |

---

## Header Files and CS50 Manual Pages

```c
#include <stdio.h>
```

This tells the compiler to use the **stdio.h** library (standard input/output), which provides `printf` among many other functions.

A **library** is a collection of pre-written code you can reuse in your programs.

CS50 also provides its own library **cs50.h** with helpful input functions:

| Function | Returns |
|----------|---------|
| `get_char` | `char` |
| `get_double` | `double` |
| `get_float` | `float` |
| `get_int` | `int` |
| `get_long` | `long` |
| `get_string` | `string` |

These are pre-installed at [cs50.dev](https://cs50.dev).

---

## Hello, You

```c
// get_string and printf with %s

#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string answer = get_string("What's your name? ");
    printf("hello, %s\n", answer);
}
```

- `get_string` gets a string from the user.
- `%s` is a **format code** (placeholder) that tells `printf` to expect a string.
- `answer` is a **variable** of type `string` that holds the user's input.

---

## Linux

Common terminal commands used in this course:

| Command | Description |
|---------|-------------|
| `cd` | Change directory |
| `cp` | Copy files or directories |
| `ls` | List files in a directory |
| `mkdir` | Make a new directory |
| `mv` | Move or rename files |
| `rm` | Remove files |
| `rmdir` | Remove directories |

---

## Conditionals

```c
// Conditionals — mutually exclusive
if (x < y)
{
    printf("x is less than y\n");
}
else if (x > y)
{
    printf("x is greater than y\n");
}
else
{
    printf("x is equal to y\n");
}
```

---

## Types

Available data types in C:

| Type | Description |
|------|-------------|
| `bool` | Boolean (`true` / `false`) |
| `char` | Single character |
| `float` | Floating-point number |
| `int` | Integer |
| `long` | Large integer |
| `string` | String of characters (via cs50.h) |

---

## Format Codes

Used with `printf` to specify the type of variable being printed:

| Code | Type |
|------|------|
| `%c` | `char` |
| `%f` | `float` |
| `%i` | `int` |
| `%li` | `long` |
| `%s` | `string` |

---

## Variables

```c
int counter = 0;    // declare and initialize

counter = counter + 1;  // increment
counter += 1;           // shorthand
counter++;              // shortest

counter--;              // decrement
```

---

## compare.c

```c
// Compare integers

#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int x = get_int("What's x? ");
    int y = get_int("What's y? ");

    if (x < y)
    {
        printf("x is less than y\n");
    }
    else if (x > y)
    {
        printf("x is greater than y\n");
    }
    else
    {
        printf("x is equal to y\n");
    }
}
```

---

## agree.c

`char` is a **single character**. Single characters use single quotes `'y'`; strings use double quotes `"yes"`.

```c
// Logical operators

#include <cs50.h>
#include <stdio.h>

int main(void)
{
    char c = get_char("Do you agree? ");

    if (c == 'Y' || c == 'y')
    {
        printf("Agreed.\n");
    }
    else
    {
        printf("Not agreed.\n");
    }
}
```

> `||` means **or**. `==` checks equality (a single `=` assigns a value).

---

## Loops and meow.c

### while loop

```c
int i = 0;
while (i < 3)
{
    printf("meow\n");
    i++;
}
```

### for loop (preferred)

```c
for (int i = 0; i < 3; i++)
{
    printf("meow\n");
}
```

> In computer science, we count from **zero**.

### do-while loop (guarantees at least one execution)

```c
int n;
do
{
    n = get_int("What's n? ");
}
while (n < 0);
```

### Infinite loop

```c
while (true)
{
    printf("meow\n");
}
```

> Break with `Ctrl+C` (sends `SIGINT`).

---

## Functions

```c
// Abstraction with parameterization

#include <stdio.h>

void meow(int n);

int main(void)
{
    meow(3);
}

void meow(int n)
{
    for (int i = 0; i < n; i++)
    {
        printf("meow\n");
    }
}
```

- **Prototype** (`void meow(int n);`) declared at the top so the compiler knows the function exists.
- **`void`** return type means the function returns nothing.
- Variables only exist within their **scope** (the `{}` block where they are declared).

---

## Correctness, Design, Style

Code is evaluated on three axes:

| Axis | Tool | Question |
|------|------|----------|
| **Correctness** | `check50` | Does the code run as intended? |
| **Design** | `design50` | How well is the code designed? |
| **Style** | `style50` | Is the code aesthetically consistent? |

---

## Mario

### Horizontal row of `?` blocks

```c
// Prints a row of 4 question marks with a loop

#include <stdio.h>

int main(void)
{
    for (int i = 0; i < 4; i++)
    {
        printf("?");
    }
    printf("\n");
}
```

### 3×3 grid of `#` bricks

```c
// Prints a 3-by-3 grid with nested loops

#include <stdio.h>

int main(void)
{
    const int n = 3;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            printf("#");
        }
        printf("\n");
    }
}
```

> `const` makes a variable **unchangeable** after initialization.

---

## Operators

| Operator | Operation |
|----------|-----------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Remainder (modulo) |

### Integer overflow

```c
// An int can only hold up to 2,147,483,647
// Use long for larger values

long dollars = 1;
printf("%li\n", dollars);
```

### Floating-point imprecision

```c
// Casting int to float for decimal division

int x = get_int("What's x? ");
int y = get_int("What's y? ");
printf("%f\n", (float) x / y);
```

> Floats have limited precision — always be aware of the type you are using.

---

## Summing Up

In this lesson, you learned:

- How to create your first program in C
- How to use the command line
- Predefined functions native to C
- Variables, conditionals, and loops
- How to create your own functions
- How to evaluate code: correctness, design, and style
- Types, operators, and their implications

**See you next time!**
