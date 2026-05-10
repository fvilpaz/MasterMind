# Recover

## Problem to Solve

A memory card had photos deleted from it. In the computer world, "deleted" usually means "forgotten," not actually erased. Write a program that recovers JPEGs from a forensic image of the card.

In a file called `recover.c` in a folder called `recover`.

---

## Distribution Code

```bash
wget https://cdn.cs50.net/2023/fall/psets/4/recover.zip
unzip recover.zip
rm recover.zip
cd recover
```

Files inside:

| File | Description |
|------|-------------|
| `recover.c` | Starting point — your code goes here |
| `card.raw` | Forensic image of the memory card (contains 50 JPEGs) |

---

## Background

### JPEG Signatures

Every JPEG starts with a 4-byte signature:

| Byte | Value |
|------|-------|
| `[0]` | `0xff` |
| `[1]` | `0xd8` |
| `[2]` | `0xff` |
| `[3]` | `0xe0` – `0xef` (first 4 bits are `1110`) |

```c
// How to detect a JPEG signature in a buffer:
if (buffer[0] == 0xff &&
    buffer[1] == 0xd8 &&
    buffer[2] == 0xff &&
    (buffer[3] & 0xf0) == 0xe0)
{
    // Start of a new JPEG
}
```

### FAT File System — 512-byte blocks

- The camera writes data in **512-byte blocks**.
- JPEG signatures always appear at the **start** of a block — check only the first 4 bytes of each block.
- JPEGs are stored **contiguously** — a new signature means the previous JPEG has ended.
- Slack space at the end of a JPEG is filled with `0x00` — safe to include.

---

## Specification

| Rule | Detail |
|------|--------|
| Arguments | Exactly 1: the forensic image filename |
| Bad usage | Print `Usage: ./recover FILE` and return `1` |
| Can't open file | Inform the user and return `1` |
| Output filenames | `###.jpg` — three-digit decimal, starting at `000` |
| Memory | No leaks if you use `malloc` |

---

## Algorithm (Pseudocode)

```
open card.raw
create 512-byte buffer

while (fread 512 bytes into buffer) == 512:
    if buffer starts with JPEG signature:
        if a JPEG is already open → close it
        open a new output file (000.jpg, 001.jpg, ...)
    if a JPEG is currently open:
        write the 512-byte buffer to it

close any open files
```

---

## Key Implementation Details

### Buffer type

```c
#include <stdint.h>

uint8_t buffer[512];   // one block = 512 bytes
```

### Reading blocks in a loop

```c
while (fread(buffer, 1, 512, card) == 512)
{
    // process each 512-byte block
}
```

### Naming output files

```c
char filename[8];   // "000.jpg\0" = 7 chars + null terminator
sprintf(filename, "%03i.jpg", counter);
```

### Cleaning up test output

```bash
rm *.jpg       # deletes all JPEGs in current directory
rm -f *.jpg    # same, without confirmation prompt
```

---

## How to Test

```bash
make recover
./recover card.raw
```

Open the recovered `000.jpg`, `001.jpg`, etc. — if they display correctly, it worked. You should recover exactly **50 JPEGs**.

## Correctness

```bash
check50 cs50/problems/2024/x/recover
```

## Style

```bash
style50 recover.c
```

## How to Submit

```bash
submit50 cs50/problems/2024/x/recover
```
