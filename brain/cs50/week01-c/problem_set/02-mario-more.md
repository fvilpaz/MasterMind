# Mario (More)

## Problem to Solve

Toward the beginning of World 1-1 in Nintendo's Super Mario Brothers, Mario must hop over **adjacent pyramids** of blocks.

In a file called `mario.c` in a folder called `mario-more`, implement a program in C that recreates that pyramid using hashes (`#`) for bricks:

```
   #  #
  ##  ##
 ###  ###
####  ####
```

The user decides how tall the pyramids should be by inputting a positive `int` between **1 and 8**, inclusive.

> Notice that the width of the **gap** between adjacent pyramids is always equal to **two hashes (`  `)**, regardless of height.

---

## Examples

**Height 8:**
```
$ ./mario
Height: 8
       #  #
      ##  ##
     ###  ###
    ####  ####
   #####  #####
  ######  ######
 #######  #######
########  ########
```

**Height 4:**
```
$ ./mario
Height: 4
   #  #
  ##  ##
 ###  ###
####  ####
```

**Height 2:**
```
$ ./mario
Height: 2
 #  #
##  ##
```

**Height 1:**
```
$ ./mario
Height: 1
#  #
```

**Invalid inputs (re-prompt until valid):**
```
$ ./mario
Height: -1
Height: 0
Height: 42
Height: 50
Height: 4
   #  #
  ##  ##
 ###  ###
####  ####
```

---

## How to Test

Does your code work correctly when you input:

- `-1` or other negative numbers?
- `0`?
- `1` through `8`?
- `9` or other positive numbers?
- Letters or words?
- No input at all (just pressing Enter)?

---

## Correctness

```
check50 cs50/problems/2026/x/mario/more
```

## Style

```
style50 mario.c
```

## How to Submit

```
submit50 cs50/problems/2026/x/mario/more
```
