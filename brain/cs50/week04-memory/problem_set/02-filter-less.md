# Filter (Less Comfortable)

## Problem to Solve

A **24-bit BMP** image stores each pixel as three bytes: **blue, green, red** (in that order on disk). Each channel value ranges from 0 to 255.

In a file called `helpers.c` in a folder called `filter-less`, implement four image filters by manipulating the RGB values of each pixel.

---

## Distribution Code

```bash
wget https://cdn.cs50.net/2023/fall/psets/4/filter-less.zip
unzip filter-less.zip
rm filter-less.zip
cd filter-less
```

Files you'll find inside:

| File | Description |
|------|-------------|
| `bmp.h` | Defines `RGBTRIPLE`, `BITMAPFILEHEADER`, `BITMAPINFOHEADER` |
| `filter.c` | Main program — already written, do not modify |
| `helpers.h` | Function prototypes — do not modify |
| `helpers.c` | **Your work goes here** |
| `Makefile` | Build instructions |
| `images/` | Sample BMP files for testing |

---

## BMP Structure

- **BITMAPFILEHEADER** — 14 bytes of file metadata
- **BITMAPINFOHEADER** — 40 bytes of image metadata
- **Pixel data** — stored as BGR triples (not RGB!)

Each pixel is an `RGBTRIPLE` struct with fields:

```c
image[i][j].rgbtRed
image[i][j].rgbtGreen
image[i][j].rgbtBlue
```

---

## Filters to Implement

### Grayscale (`-g`)

Convert every pixel to a shade of gray by setting R, G, B to the **average** of their original values.

```c
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Take average of red, green, blue — round to nearest int
            // Set all three channels to that average
        }
    }
}
```

> Divide by `3.0` (not `3`) to avoid integer truncation before rounding.

---

### Sepia (`-s`)

Apply the classic sepia tone using these formulas — **cap results at 255**:

```
sepiaRed   = .393 * R + .769 * G + .189 * B
sepiaGreen = .349 * R + .686 * G + .168 * B
sepiaBlue  = .272 * R + .534 * G + .131 * B
```

```c
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Compute sepia values with the formulas above
            // Round to nearest int
            // Cap at 255
            // Update pixel
        }
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
    {
        // Only iterate over half the width — swap left pixel with its mirror
    }
}
```

> Use a temporary variable to swap, just like swapping integers.

---

### Blur (`-b`)

Apply a **box blur**: replace each pixel's color with the average of all pixels in its 3×3 neighborhood (including itself). Edge and corner pixels use whatever neighbors exist.

```c
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Create a copy of image to read from while writing to the original
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
        for (int j = 0; j < width; j++)
            copy[i][j] = image[i][j];

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Loop over the 3x3 neighborhood centered on copy[i][j]
            // Skip pixels outside image bounds
            // Average valid neighbors and update image[i][j]
        }
    }
}
```

> Read from `copy`, write to `image` — never blur with already-blurred pixels.

---

## How to Test

```bash
make filter

./filter -g images/yard.bmp out.bmp    # grayscale
./filter -s images/yard.bmp out.bmp    # sepia
./filter -r images/yard.bmp out.bmp    # reflect
./filter -b images/yard.bmp out.bmp    # blur
```

## Correctness

```bash
check50 cs50/problems/2024/x/filter/less
```

## Style

```bash
style50 helpers.c
```

## How to Submit

```bash
submit50 cs50/problems/2024/x/filter/less
```
