# Filter (More Comfortable)

## Problem to Solve

Same BMP pixel manipulation as Filter Less, but replacing **sepia** with a harder filter: **edge detection** using the Sobel operator.

In a file called `helpers.c` in a folder called `filter-more`, implement four image filters.

---

## Distribution Code

```bash
wget https://cdn.cs50.net/2023/fall/psets/4/filter-more.zip
unzip filter-more.zip
rm filter-more.zip
cd filter-more
```

Files inside:

| File | Description |
|------|-------------|
| `bmp.h` | Defines `RGBTRIPLE`, `BITMAPFILEHEADER`, `BITMAPINFOHEADER` |
| `filter.c` | Main program — do not modify |
| `helpers.h` | Function prototypes — do not modify |
| `helpers.c` | **Your work goes here** |
| `Makefile` | Build instructions |
| `images/` | Sample BMP files for testing |

---

## Filters to Implement

### Grayscale (`-g`)

Set R, G, B to the **average** of their original values.

```c
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
        for (int j = 0; j < width; j++)
        {
            // Average R, G, B — round to nearest int
            // Set all three channels to that value
        }
}
```

---

### Reflect (`-r`)

Flip the image **horizontally** — swap pixels on opposite sides of each row.

```c
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
        // Iterate over half the width, swap left pixel with its mirror
}
```

---

### Blur (`-b`)

**Box blur**: replace each pixel with the average of its 3×3 neighborhood. Read from a copy, write to the original.

```c
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    // Copy image into copy

    for (int i = 0; i < height; i++)
        for (int j = 0; j < width; j++)
        {
            // Loop over 3x3 neighborhood in copy
            // Skip out-of-bounds pixels
            // Average valid neighbors → update image[i][j]
        }
}
```

---

### Edges (`-e`) — the new one

Apply the **Sobel operator** to detect edges. For each pixel and each color channel, compute **Gx** and **Gy** using these kernels:

```
Gx kernel:          Gy kernel:
-1   0  +1          -1  -2  -1
-2   0  +2           0   0   0
+1   0  +2          +1  +2  +1
```

Then combine:

```
final = round(sqrt(Gx² + Gy²))  →  cap at 255
```

**Edge pixels:** treat any pixel outside the image boundary as solid black (R=G=B=0).

```c
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    // Copy image into copy

    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // For each color channel:
            //   Loop over 3x3 neighborhood
            //   If neighbor is out of bounds → treat as 0
            //   Compute sumGx and sumGy using kernels
            //   final = round(sqrt(sumGx² + sumGy²)), cap at 255
            // Update image[i][j]
        }
    }
}
```

> The key difference from blur: out-of-bounds neighbors count as **black (0)**, not ignored.

---

## Sobel Kernels — Visual Reference

For a target pixel at position `[i][j]`, the 3×3 neighborhood maps to the kernels like this:

```
Neighbor positions:     Gx weights:     Gy weights:
[i-1][j-1] [i-1][j] [i-1][j+1]    -1   0  +1    -1  -2  -1
[i  ][j-1] [i  ][j] [i  ][j+1]    -2   0  +2     0   0   0
[i+1][j-1] [i+1][j] [i+1][j+1]    -1   0  +1    +1  +2  +1
```

---

## How to Test

```bash
make filter

./filter -g images/yard.bmp out.bmp    # grayscale
./filter -r images/yard.bmp out.bmp    # reflect
./filter -b images/yard.bmp out.bmp    # blur
./filter -e images/yard.bmp out.bmp    # edges
```

## Correctness

```bash
check50 cs50/problems/2024/x/filter/more
```

## Style

```bash
style50 helpers.c
```

## How to Submit

```bash
submit50 cs50/problems/2024/x/filter/more
```
