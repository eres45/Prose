# Part 2 — Variables and Logic

A variable is just a name you give to a piece of information so you can use it later.

---

## Creating Variables

```Prose
Let name be "Alice".
Let age be 25.
Let price be 9.99.
Let active be true.
```

`Let X be Y` — that's how you create a variable in Prose. Simple.

To update an existing variable, you use the same syntax:

```Prose
Let score be 0.
Let score be score plus 10.
Say score.
```

Output: `10`

---

## Math

Prose supports the four basic operations, and they all use English words:

| What you want | How to write it |
| :--- | :--- |
| Add | `plus` |
| Subtract | `minus` |
| Multiply | `times` |
| Divide | `divided by` |
| Remainder | `modulo` |

Examples:

```Prose
Let total be 50 plus 30.
Let half be total divided by 2.
Let area be 5 times 6.
Let remainder be 17 modulo 5.

Say total.      Note: 80
Say half.       Note: 40
Say area.       Note: 30
Say remainder.  Note: 2
```

You can chain them:

```Prose
Let result be 10 plus 5 times 2.
Say result.
```

---

## Working with Text

Text (called a *string*) goes inside quotes.

```Prose
Let greeting be "Hello".
Let name be "Ronit".
Let message be greeting plus ", " plus name plus "!".
Say message.
```

Output: `Hello, Ronit!`

Useful text operations:

```Prose
Let sentence be "the quick brown fox".

Say the length of sentence.          Note: 19
Say uppercase of sentence.           Note: THE QUICK BROWN FOX
Say lowercase of "HELLO WORLD".      Note: hello world
Say trim of "   hello   ".           Note: hello (spaces removed)
```

Check if text contains something:

```Prose
Let sentence be "the quick brown fox".

If sentence contains "fox" then do the following.
    Say "Found it!".
End if.
```

---

## Making Decisions

This is where programs get interesting. Use `If` to only do something when a condition is true.

```Prose
Let age be 20.

If age > 18 then do the following.
    Say "You are an adult.".
End if.
```

Always end an `If` block with `End if.`

### If / Otherwise

```Prose
Let temperature be 15.

If temperature > 25 then do the following.
    Say "It's hot outside.".
Otherwise do the following.
    Say "Bring a jacket.".
End if.
```

### Comparing Values

| Check | How to write it |
| :--- | :--- |
| Greater than | `> 5` or `is greater than 5` |
| Less than | `< 5` or `is less than 5` |
| Equal | `is 5` or `= 5` |
| Not equal | `is not 5` |
| Greater or equal | `>= 5` |
| Less or equal | `<= 5` |

### Multiple Conditions

Use `and` / `or` to combine checks:

```Prose
Let age be 22.
Let has_ticket be true.

If age >= 18 and has_ticket is true then do the following.
    Say "Welcome to the event!".
End if.
```

---

## Checking the Type of Something

```Prose
Let value be 42.

If value is a number then do the following.
    Say "It's a number.".
End if.

If value is a text then do the following.
    Say "It's text.".
End if.
```

Other type checks: `is a list`, `is a boolean`.

---

## Converting Between Types

```Prose
Let num_text be "42".
Let actual_number be num_text as a number.
Let back_to_text be actual_number as text.
```

---

## What's Next

[Part 3](03_loops_and_lists.md) covers loops and lists — how to repeat things and work with groups of data.
