# Volume

## Problem to Solve

WAV files store audio as a sequence of **samples**: numbers that represent the value of some audio signal at a particular point in time.

- WAV files begin with a **44-byte header** containing metadata (file size, samples per second, sample size, etc.).
- After the header, each sample is a **16-bit (2-byte) signed integer**.

Scaling each sample by a given factor changes the volume:

| Factor | Effect |
|--------|--------|
| `2.0` | Double the volume |
| `0.5` | Cut the volume in half |

In a file called `volume.c` in a folder called `volume`, write a program to modify the volume of a WAV audio file.

---

## Distribution Code

```bash
wget https://cdn.cs50.net/2023/fall/psets/4/volume.zip
unzip volume.zip
rm volume.zip
cd volume
```

---

## Implementation Details

Your program must accept **3 command-line arguments**:

```bash
./volume input.wav output.wav factor
```

| Argument | Description |
|----------|-------------|
| `input` | Original audio file |
| `output` | New audio file to generate |
| `factor` | Float — scale factor for volume |

### Rules

- Read the 44-byte header from `input` and write it unchanged to `output`.
- Read the remaining data **one 16-bit sample at a time**.
- Multiply each sample by `factor` and write it to `output`.
- Assume samples are **16-bit signed integers** (`int16_t`).
- If you use `malloc`, you must not leak memory.

---

## Key Data Types (`stdint.h`)

| Type | Size | Use |
|------|------|-----|
| `uint8_t` | 8-bit unsigned | Reading the WAV header byte by byte |
| `int16_t` | 16-bit signed | Reading/writing audio samples |

---

## Hints

### 1. Copy the header

```c
uint8_t header[HEADER_SIZE];
fread(header, HEADER_SIZE, 1, input);
fwrite(header, HEADER_SIZE, 1, output);
```

### 2. Process samples in a loop

```c
int16_t buffer;

while (fread(&buffer, sizeof(int16_t), 1, input))
{
    buffer *= factor;
    fwrite(&buffer, sizeof(int16_t), 1, output);
}
```

> `fread` returns the number of items successfully read — when it reaches the end of the file it returns `0`, which ends the loop.

---

## How to Test

```bash
./volume input.wav output.wav 2.0   # output should be twice as loud
./volume input.wav output.wav 0.5   # output should be half as loud
```

## Correctness

```bash
check50 cs50/problems/2024/x/volume
```

## Style

```bash
style50 volume.c
```

## How to Submit

```bash
submit50 cs50/problems/2024/x/volume
```
