# Credit

## Problem to Solve

A credit card number isn't random — it has structure and a built-in **checksum** that allows computers to detect typos or invalid numbers without querying a database.

In a file called `credit.c` in a folder called `credit`, implement a program in C that checks the validity of a given credit card number.

---

## Card Formats

| Network | Length | Starts with |
|---------|--------|-------------|
| American Express | 15 digits | `34` or `37` |
| MasterCard | 16 digits | `51`, `52`, `53`, `54`, or `55` |
| Visa | 13 or 16 digits | `4` |

---

## Luhn's Algorithm

Most cards use an algorithm invented by **Hans Peter Luhn** of IBM. To check if a number is valid:

1. **Multiply every other digit by 2**, starting from the **second-to-last** digit, and add the digits of those products together.
2. **Add that sum** to the sum of the digits that were **not** multiplied by 2.
3. If the **total's last digit is 0** (i.e., `total % 10 == 0`), the number is valid.

### Example: Visa `4003600000000014`

**Step 1 — Underline every other digit starting from second-to-last:**

```
4 0 0 3 6 0 0 0 0 0 0 0 0 0 1 4
          ↑       ↑       ↑       ↑       ↑       ↑       ↑       ↑
```

Underlined digits: `1, 0, 0, 0, 0, 6, 0, 4`

Multiply each by 2:

```
1×2 + 0×2 + 0×2 + 0×2 + 0×2 + 6×2 + 0×2 + 4×2
= 2 + 0 + 0 + 0 + 0 + 12 + 0 + 8
```

Add the **digits** of those products:

```
2 + 0 + 0 + 0 + 0 + 1 + 2 + 0 + 8 = 13
```

**Step 2 — Add the non-underlined digits:**

```
13 + 4 + 0 + 0 + 0 + 0 + 0 + 3 + 0 = 20
```

**Step 3 — Last digit of 20 is 0 → ✅ Valid!**

---

## Implementation Details

- Prompt the user for a credit card number.
- Use **`get_long`** from CS50's library (not `get_int` — numbers are too large for int!).
- Assume input is entirely numeric and has no leading zeroes.
- The last line of output must be exactly one of:

```
AMEX
MASTERCARD
VISA
INVALID
```

### Example runs:

```
$ ./credit
Number: 4003600000000014
VISA
```

```
$ ./credit
Number: 6176292929
INVALID
```

```
$ ./credit
Number: 4003-6000-0000-0014
Number: foo
Number: 4003600000000014
VISA
```

> `get_long` will automatically reject non-numeric input like hyphens or letters, re-prompting the user.

---

## How to Test

Test with valid and invalid inputs, including:

- Valid Visa, MasterCard, and Amex numbers (use [PayPal's test card numbers](https://developer.paypal.com/api/nvp-soap/paypal-payments-standard/integration-guide/underlineshelp/))
- Numbers that are numeric but not valid card numbers (e.g., phone numbers)
- Numbers with wrong length or wrong prefix

---

## Correctness

```
check50 cs50/problems/2026/x/credit
```

## Style

```
style50 credit.c
```

## How to Submit

```
submit50 cs50/problems/2026/x/credit
```
