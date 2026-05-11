# Cash

## Problem to Solve

Suppose you work at a store and a customer gives you $1.00 (100 cents) for candy that costs $0.50 (50 cents). You'll need to pay them their **change** — the amount leftover after paying for the candy.

In a file called `cash.c` in a folder called `cash`, implement a program in C that prints the **minimum number of coins** needed to make the given amount of change, in cents:

```
Change owed: 25
1
```

```
Change owed: 70
4
```

Prompt the user for an `int` greater than or equal to 0. Re-prompt again and again if the input is invalid (less than 0 or not an int).

---

## Greedy Algorithms

A **greedy algorithm** always takes the best immediate (local) solution at each step. For US coins (quarters, dimes, nickels, pennies), this approach is also globally optimal — it always yields the fewest coins possible.

**Example:** For 41¢:
1. Take one quarter (25¢) → 16¢ remaining
2. Take one dime (10¢) → 6¢ remaining
3. Take one nickel (5¢) → 1¢ remaining
4. Take one penny (1¢) → 0¢ remaining

**Result: 4 coins**

---

## Advice

### 1. Start with compilable code

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{

}
```

### 2. Write pseudocode first

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Prompt the user for change owed, in cents

    // Calculate how many quarters you should give customer
    // Subtract the value of those quarters from cents

    // Calculate how many dimes you should give customer
    // Subtract the value of those dimes from remaining cents

    // Calculate how many nickels you should give customer
    // Subtract the value of those nickels from remaining cents

    // Calculate how many pennies you should give customer
    // Subtract the value of those pennies from remaining cents

    // Sum the number of quarters, dimes, nickels, and pennies used
    // Print that sum
}
```

### 3. Convert pseudocode to code

**Prompt the user with a `do while` loop:**

```c
int cents;
do
{
    cents = get_int("Change owed: ");
}
while (cents < 0);
```

**Create a `calculate_quarters` function:**

```c
int calculate_quarters(int cents)
{
    int quarters = 0;
    while (cents >= 25)
    {
        quarters++;
        cents = cents - 25;
    }
    return quarters;
}
```

**Integrate it into the full program:**

```c
#include <cs50.h>
#include <stdio.h>

int calculate_quarters(int cents);

int main(void)
{
    // Prompt the user for change owed, in cents
    int cents;
    do
    {
        cents = get_int("Change owed: ");
    }
    while (cents < 0);

    // Calculate quarters and subtract from cents
    int quarters = calculate_quarters(cents);
    cents = cents - (quarters * 25);

    // Repeat the pattern for dimes, nickels, and pennies...
}

int calculate_quarters(int cents)
{
    int quarters = 0;
    while (cents >= 25)
    {
        quarters++;
        cents = cents - 25;
    }
    return quarters;
}
```

> Apply the same pattern to create `calculate_dimes`, `calculate_nickels`, and `calculate_pennies`. Then sum all results and print!

---

## How to Test

| Input | Expected output | Reasoning |
|-------|----------------|-----------|
| `-1`  | (re-prompt)    | Invalid input |
| `0`   | `0`            | No change needed |
| `1`   | `1`            | One penny |
| `4`   | `4`            | Four pennies |
| `5`   | `1`            | One nickel |
| `24`  | `6`            | Two dimes + four pennies |
| `25`  | `1`            | One quarter |
| `26`  | `2`            | One quarter + one penny |
| `99`  | `9`            | Three quarters + two dimes + four pennies |

---

## Correctness

```
check50 cs50/problems/2026/x/cash
```

## Style

```
style50 cash.c
```

## How to Submit

```
submit50 cs50/problems/2026/x/cash
```
