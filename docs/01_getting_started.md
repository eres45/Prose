# Part 1 — Getting Started

Welcome. This is Prose. A programming language where you write code the same way you'd exProse something to a friend.

No brackets. No semicolons. No cryptic symbols. Just sentences.

---

## Before You Start

You need **Python 3.9 or newer** on your computer. That's the only thing required.

Check if you have it:
```
python --version
```

If it shows something like `Python 3.11.2`, you're good. If not, download it from [python.org](https://python.org).

Then download Prose:
```
git clone https://github.com/yourusername/Prose-lang.git
cd Prose-lang
```

---

## Your First Program

Create a new file called `hello.Prose` and type this inside:

```Prose
Say "Hello, world!".
```

Save it. Then in your terminal, run:

```
python Prose.py hello.Prose
```

You should see:

```
Hello, world!
```

That's it. You just wrote and ran your first Prose program.

---

## How Prose Works

Every instruction in Prose is a full sentence ending with a **period**.

A few things to know:

- Sentences end with `.` — don't forget it
- Capitalise the first word of each instruction (`Say`, `Let`, `If`, `Define`)
- `Note:` is how you write comments (Prose ignores these)

```Prose
Note: This is a comment. Prose ignores it.
Say "This gets printed.".
```

---

## Printing Things

The `Say` keyword prints something to the screen.

```Prose
Say "Hello!".
Say 42.
Say "The answer is " plus 42.
```

Output:
```
Hello!
42
The answer is 42
```

`plus` joins things together. It works for numbers and text.

---

## Asking for Input

Use `Ask` to get input from the user.

```Prose
Ask user for name.
Say "Hi, " plus name plus "!".
```

When you run this, it waits for you to type something and press Enter.

---

## Running in Interactive Mode

You can also just type Prose code directly without creating a file:

```
python Prose.py --interactive
```

A prompt appears:

```
>>> Say "Testing!".
Testing!
```

Type `quit` to leave.

---

## Two Ways to Run Prose

**Mode 1 — Interpreter** (simple, great for learning):
```
python Prose.py myfile.Prose
```

**Mode 2 — Build** (converts to Python first, much faster for big programs):
```
python Prose.py build myfile.Prose
python myfile.py
```

For now, stick with the interpreter. Once your programs get big, switch to build.

---

## What's Next

In [Part 2](02_variables_and_logic.md), we'll cover variables, math, and making decisions with `If`.
