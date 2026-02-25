# Part 3 — Loops and Lists

Loops let you repeat things. Lists let you store multiple values together. These two are the backbone of most real programs.

---

## Repeating Something a Set Number of Times

```Prose
Repeat 5 times do the following.
    Say "Hello!".
End repeat.
```

Output:
```
Hello!
Hello!
Hello!
Hello!
Hello!
```

You can also use a variable as the count:

```Prose
Let count be 3.
Repeat count times do the following.
    Say "Repeating...".
End repeat.
```

---

## Repeating While Something is True

Keep going as long as a condition holds:

```Prose
Let number be 1.

While number <= 5 do the following.
    Say number.
    Let number be number plus 1.
End while.
```

Output: `1  2  3  4  5`

Be careful with `While` — if the condition never becomes false, the loop runs forever. Always make sure something inside the loop changes the condition.

---

## Range-Based Loops

Count from one number to another:

```Prose
For each i from 1 to 10 do the following.
    Say i.
End for.
```

Count by twos, fives, or any step:

```Prose
For each i from 0 to 20 step 5 do the following.
    Say i.
End for.
```

Output: `0  5  10  15  20`

---

## Stopping a Loop Early

Use `Stop loop.` to exit immediately:

```Prose
For each i from 1 to 100 do the following.
    If i > 5 then do the following.
        Stop loop.
    End if.
    Say i.
End for.
```

Output: `1  2  3  4  5`

Use `Skip to next.` to jump to the next iteration without finishing the current one:

```Prose
For each i from 1 to 10 do the following.
    Let r be i modulo 2.
    If r is 0 then do the following.
        Skip to next.
    End if.
    Say i.
End for.
```

Output (only odd numbers): `1  3  5  7  9`

---

## Lists

A list holds multiple values in order.

```Prose
Let fruits be a list containing "apple", "banana", "cherry".
```

An empty list:

```Prose
Let items be a list.
```

### Adding and Removing

```Prose
Let numbers be a list containing 10, 20, 30.
Add 40 to numbers.
Remove item 2 from numbers.   Note: removes 20 (1-based index)
```

### Getting Items

Prose uses **1-based indexing** — the first item is item 1, not item 0.

```Prose
Let fruits be a list containing "apple", "banana", "cherry".
Say item 1 of fruits.    Note: apple
Say item 3 of fruits.    Note: cherry
```

### Looping Over a List

```Prose
Let fruits be a list containing "apple", "banana", "cherry".

For each fruit in fruits do the following.
    Say "I like " plus fruit plus ".".
End for.
```

### Useful List Operations

```Prose
Let numbers be a list containing 5, 2, 8, 1, 9, 3.

Say the length of numbers.   Note: 6

Sort numbers.
Say item 1 of numbers.       Note: 1 (smallest, now at front)

Say the index of 8 in numbers.   Note: position of 8
```

Join a list into a single text string:

```Prose
Let words be a list containing "Hello", "from", "Prose".
Let sentence be join words with " ".
Say sentence.
```

Output: `Hello from Prose`

Split text into a list:

```Prose
Let sentence be "one two three".
Let parts be split sentence by " ".
Say item 2 of parts.   Note: two
```

---

## Filtering Lists

One of Prose's best features — filter a list with a single line:

```Prose
Let scores be a list containing 45, 78, 90, 55, 88, 30, 95.

Let passing be all score in scores where score > 60.

For each s in passing do the following.
    Say s.
End for.
```

Output: `78  90  88  95`

You can filter by text too:

```Prose
Let names be a list containing "Alice", "Bob", "Andrew", "Charlie".
Let a_names be all n in names where n contains "A".
```

---

## What's Next

[Part 4](04_functions_and_files.md) covers functions, file reading, and organising bigger programs.
