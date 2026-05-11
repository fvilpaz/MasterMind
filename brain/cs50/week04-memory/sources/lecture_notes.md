# Lecture 4 — Memory

## Índice
- [Welcome!](#welcome)
- [Pixel Art](#pixel-art)
- [Hexadecimal](#hexadecimal)
- [Memory](#memory)
- [Pointers](#pointers)
- [Strings](#strings)
- [Pointer Arithmetic](#pointer-arithmetic)
- [String Comparison](#string-comparison)
- [Copying](#copying)
- [malloc and Valgrind](#malloc-and-valgrind)
- [Garbage Values](#garbage-values)
- [Pointer Fun with Binky](#pointer-fun-with-binky)
- [Swap](#swap)
- [Overflow](#overflow)
- [scanf](#scanf)
- [File I/O](#file-io)
- [Summing Up](#summing-up)

---

## Welcome!

In previous weeks, we talked about images being made of smaller building blocks called **pixels**.

Today, we go deeper into the zeros and ones that make up these images — and further into the fundamental building blocks that make up files, including images.

We will also discuss how to access the underlying data stored in **computer memory**.

---

## Pixel Art

Pixels are squares — individual dots of color — arranged on an up-down, left-right grid. You can imagine an image as a map of bits, where zeros represent black and ones represent white.

**RGB** (red, green, blue) are numbers that represent the amount of each color. Each channel ranges from **0 to 255**.

> 255 in hexadecimal is `FF`. Why? Read on.

---

## Hexadecimal

Hexadecimal is **base-16**. Its 16 digits are:

```
0 1 2 3 4 5 6 7 8 9 a b c d e f
```

Each column is a power of 16.

| Decimal | Hexadecimal |
|---------|-------------|
| 0 | `00` |
| 9 | `09` |
| 10 | `0A` |
| 15 | `0F` |
| 16 | `10` |
| 255 | `FF` |

> `FF` = 16×15 + 15 = 240 + 15 = **255** — the highest value of a two-digit hex number.

Hexadecimal lets us represent information more **succinctly** than binary.

---

## Memory

Memory can be visualized as a series of blocks, each with a hexadecimal address. By convention, hex addresses are prefixed with **`0x`**:

```
0x0  0x1  0x2  0x3  0x4  ...
```

```c
#include <stdio.h>

int main(void)
{
    int n = 50;
    printf("%p\n", &n);  // prints the memory address of n
}
```

The C language has two powerful memory operators:

| Operator | Meaning |
|----------|---------|
| `&` | Address of — provides the memory address of a variable |
| `*` | Dereference — goes to the value at a memory address |

---

## Pointers

A **pointer** is a variable that contains the **address** of another value.

```c
int n = 50;
int *p = &n;  // p stores the address of n
```

```c
#include <stdio.h>

int main(void)
{
    int n = 50;
    int *p = &n;

    printf("%p\n", p);   // prints the address
    printf("%i\n", *p);  // prints the value at that address → 50
}
```

> A pointer is usually **8 bytes** in size. `int *p` declares a pointer that holds the address of an `int`.

---

## Strings

A **string** is simply an array of characters. `string s = "HI!"` in memory looks like:

```
H | I | ! | \0
```

The variable `s` is actually a **pointer** to the first character. The `\0` (null terminator) marks the end of the string.

```c
#include <stdio.h>

int main(void)
{
    char *s = "HI!";
    printf("%s\n", s);
}
```

> This is raw C — no cs50.h needed. `string` in cs50.h is just `typedef char *string`.

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string s = "HI!";
    printf("%p\n", s);      // address of first char
    printf("%p\n", &s[0]);  // same
    printf("%p\n", &s[1]);  // address + 1
    printf("%p\n", &s[2]);  // address + 2
    printf("%p\n", &s[3]);  // address of \0
}
```

---

## Pointer Arithmetic

You can access individual characters using array notation or pointer arithmetic — they are equivalent:

```c
#include <stdio.h>

int main(void)
{
    char *s = "HI!";

    // Array notation
    printf("%c\n", s[0]);
    printf("%c\n", s[1]);
    printf("%c\n", s[2]);

    // Pointer arithmetic
    printf("%c\n", *s);
    printf("%c\n", *(s + 1));
    printf("%c\n", *(s + 2));
}
```

---

## String Comparison

You **cannot** compare strings with `==` — it compares memory addresses, not content.

```c
// WRONG — compares addresses, not strings
if (s == t)
```

```c
// CORRECT — use strcmp from <string.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    char *s = get_string("s: ");
    char *t = get_string("t: ");

    if (strcmp(s, t) == 0)
    {
        printf("Same\n");
    }
    else
    {
        printf("Different\n");
    }
}
```

> `strcmp` returns `0` if the strings are identical.

---

## Copying

Assigning `string t = s` only copies the **address**, not the content — both `s` and `t` point to the same memory.

To make an authentic copy, use **`malloc`** to allocate new memory:

```c
#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void)
{
    char *s = get_string("s: ");
    if (s == NULL)
    {
        return 1;
    }

    // Allocate memory: length of s + 1 for the \0
    char *t = malloc(strlen(s) + 1);
    if (t == NULL)
    {
        return 1;
    }

    // Copy string (strcpy handles the \0 too)
    strcpy(t, s);

    // Capitalize only the copy
    if (strlen(t) > 0)
    {
        t[0] = toupper(t[0]);
    }

    printf("s: %s\n", s);
    printf("t: %s\n", t);

    free(t);  // always free memory you allocated
    return 0;
}
```

> **`malloc`** allocates a block of memory. **`free`** releases it. Always pair them.

---

## malloc and Valgrind

**Valgrind** detects memory errors: leaks, out-of-bounds writes, unfreed allocations.

```c
// BAD — writes out of bounds and never frees
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int *x = malloc(3 * sizeof(int));
    x[1] = 72;
    x[2] = 73;
    x[3] = 33;  // index 3 is out of bounds for an array of size 3!
}
```

```c
// GOOD — correct indices, memory freed
int *x = malloc(3 * sizeof(int));
x[0] = 72;
x[1] = 73;
x[2] = 33;
free(x);
```

Run with:

```bash
make memory
valgrind ./memory
```

---

## Garbage Values

When you allocate memory, it is **not guaranteed to be empty** — it may contain leftover data from previous use (**garbage values**).

```c
#include <stdio.h>

int main(void)
{
    int scores[1024];
    for (int i = 0; i < 1024; i++)
    {
        printf("%i\n", scores[i]);  // may print random junk
    }
}
```

> Always **initialize** your variables and arrays before using them.

---

## Pointer Fun with Binky

We watched a video from Stanford University that helped us visualize and understand pointers.

---

## Swap

Passing variables **by value** gives a function a copy — changes do not affect the original:

```c
// WRONG — swap doesn't affect x and y in main
void swap(int a, int b)
{
    int tmp = a;
    a = b;
    b = tmp;
}
```

Pass **by reference** (using pointers) to swap the actual values:

```c
#include <stdio.h>

void swap(int *a, int *b);

int main(void)
{
    int x = 1;
    int y = 2;

    printf("x is %i, y is %i\n", x, y);
    swap(&x, &y);
    printf("x is %i, y is %i\n", x, y);
}

void swap(int *a, int *b)
{
    int tmp = *a;
    *a = *b;
    *b = tmp;
}
```

### Memory layout

```
┌─────────────────────────────┐
│  machine code               │
│  globals                    │
│  heap  ↓  (malloc lives here)│
│  stack ↑  (functions live here)│
└─────────────────────────────┘
```

Each function call gets its own **stack frame**. That is why passing by value doesn't work across functions.

---

## Overflow

| Type | Cause |
|------|-------|
| **Heap overflow** | Writing past the end of `malloc`'d memory |
| **Stack overflow** | Too many nested function calls |

Both are types of **buffer overflow** — a common source of security vulnerabilities.

---

## scanf

`scanf` is the standard C way to read user input.

```c
// Reading an integer
#include <stdio.h>

int main(void)
{
    int x;
    printf("x: ");
    scanf("%i", &x);  // pass the ADDRESS of x
    printf("x: %i\n", x);
}
```

Reading strings with `scanf` is unsafe — you must pre-allocate memory:

```c
// Pre-allocated buffer (fragile — overflows if input > 3 chars)
#include <stdio.h>

int main(void)
{
    char s[4];
    printf("s: ");
    scanf("%s", s);
    printf("s: %s\n", s);
}
```

> This is why `get_string` from cs50.h exists — it handles memory allocation safely.

---

## File I/O

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    FILE *file = fopen("phonebook.csv", "a");  // open for appending
    if (!file)
    {
        return 1;  // protect against NULL (file not found / no permission)
    }

    char *name   = get_string("Name: ");
    char *number = get_string("Number: ");

    fprintf(file, "%s,%s\n", name, number);  // write to file

    fclose(file);
}
```

| Function | Purpose |
|----------|---------|
| `fopen(path, mode)` | Open a file (`"r"` read, `"w"` write, `"a"` append) |
| `fprintf(file, ...)` | Write formatted text to a file |
| `fclose(file)` | Close the file |
| `fread(...)` | Read raw bytes |
| `fwrite(...)` | Write raw bytes |

### Copying a file byte by byte

```c
#include <stdio.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    FILE *src = fopen(argv[1], "rb");
    FILE *dst = fopen(argv[2], "wb");

    BYTE b;
    while (fread(&b, sizeof(b), 1, src) != 0)
    {
        fwrite(&b, sizeof(b), 1, dst);
    }

    fclose(dst);
    fclose(src);
}
```

> This week's problem sets involve manipulating **BMP image files** at the byte level.

---

## Summing Up

In this lesson, you learned:

- **Pixel art** and how images are stored as bits
- **Hexadecimal** — base-16, used for memory addresses
- **Memory** layout and the `0x` address convention
- **Pointers** — variables that store memory addresses (`&`, `*`)
- **Strings** — arrays of `char` ending in `\0`, accessed via pointer
- **Pointer arithmetic** — navigating memory manually
- **String comparison** — use `strcmp`, not `==`
- **Copying** strings with `malloc` + `strcpy` + `free`
- **Valgrind** — detecting memory leaks and errors
- **Garbage values** — uninitialized memory contains junk
- **Swap** — pass by reference with pointers to mutate across functions
- **Buffer overflow** — heap and stack overflow
- **scanf** — standard input, but unsafe for strings
- **File I/O** — `fopen`, `fprintf`, `fclose`, `fread`, `fwrite`

**See you next time!**
