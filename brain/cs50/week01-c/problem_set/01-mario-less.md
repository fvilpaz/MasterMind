# Mario

## Problem to Solve

Toward the end of World 1-1 in Nintendo's Super Mario Bros., Mario must ascend a right-aligned pyramid of bricks.

In a file called `mario.c` in a folder called `mario-less`, implement a program in C that recreates that pyramid using hashes (`#`) for bricks:

```
       #
      ##
     ###
    ####
   #####
  ######
 #######
########
```

Prompt the user for an `int` for the pyramid's actual height, so the program can also output shorter pyramids like:

```
  #
 ##
###
```

Re-prompt the user, again and again as needed, if their input is not greater than 0 or not an `int` altogether.

---

## Hints

- Recall that you can get an int from a user with `get_int`, declared in `cs50.h`.
- Recall that you can print a string with `printf`, declared in `stdio.h`.

---

## Advice

### 1. Write some code that you know will compile

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{

}
```

### 2. Write some pseudocode before writing more code

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Prompt the user for the pyramid's height

    // Print a pyramid of that height
}
```

### 3. Convert the pseudocode to code

**Prompt the user for height using a `do while` loop:**

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int n;
    do
    {
        n = get_int("Height: ");
    }
    while (n < 1);

    for (int i = 0; i < n; i++)
    {
        // Print row of bricks
    }
}
```

**Introduce a `print_row` function:**

```c
#include <cs50.h>
#include <stdio.h>

void print_row(int bricks);

int main(void)
{
    int n;
    do
    {
        n = get_int("Height: ");
    }
    while (n < 1);

    for (int i = 0; i < n; i++)
    {
        print_row(i + 1);
    }
}

void print_row(int bricks)
{
    for (int i = 0; i < bricks; i++)
    {
        printf("#");
    }
    printf("\n");
}
```

> **Why `i + 1`?** Because on the first iteration `i` is 0, but the first row should have 1 brick.  
> **Why `\n`?** To move to the next line after printing each row.

**Add spaces for right-alignment:**

```c
#include <cs50.h>
#include <stdio.h>

void print_row(int spaces, int bricks);

int main(void)
{
    int n;
    do
    {
        n = get_int("Height: ");
    }
    while (n < 1);

    for (int i = 0; i < n; i++)
    {
        // Print row of bricks — complete this!
    }
}

void print_row(int spaces, int bricks)
{
    // Print spaces

    // Print bricks
}
```

> The remaining pseudocode in `main` and `print_row` is left for you to complete.  
> Consider also factoring out the input logic into a `get_height` function!

---

## How to Test

Does your code work correctly when you input:

- `-1` or other negative numbers?
- `0`?
- `1` or other positive numbers?
- Letters or words?
- No input at all (just pressing Enter)?

---

## Correctness

```
check50 cs50/problems/2026/x/mario/less
```

## Style

```
style50 mario.c
```

## How to Submit

```
submit50 cs50/problems/2026/x/mario/less
```
