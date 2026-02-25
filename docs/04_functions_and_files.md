# Part 4 — Functions, Files, and Modules

Once your programs get longer than 20 lines, you need a way to organise them. Functions are the answer. They let you name a block of code and reuse it without copying it everywhere.

---

## Defining a Function

```Prose
Define a function called greet that takes name and does the following.
    Say "Hello, " plus name plus "!".
End function.
```

Calling it:

```Prose
Call greet with "Alice".
Call greet with "Bob".
```

Output:
```
Hello, Alice!
Hello, Bob!
```

---

## Functions That Return a Value

Use `Give back` to return a result:

```Prose
Define a function called add that takes a and b and does the following.
    Give back a plus b.
End function.

Let result be the result of calling add with 10 and 5.
Say result.
```

Output: `15`

---

## Multiple Parameters

Just list them in the definition, separated by `and`:

```Prose
Define a function called full_name that takes first and last and does the following.
    Give back first plus " " plus last.
End function.

Let name be the result of calling full_name with "John" and "Doe".
Say name.
```

---

## Functions With No Parameters

```Prose
Define a function called separator that takes no parameters and does the following.
    Say "----------------------------".
End function.

Call separator.
Say "Section One".
Call separator.
Say "Section Two".
Call separator.
```

---

## Reading and Writing Files

### Writing to a File

```Prose
Write "Hello, file!" to "output.txt".
```

### Appending to a File

```Prose
Append "Second line." to "output.txt".
```

### Reading a File

```Prose
Let contents be the contents of "output.txt".
Say contents.
```

### Checking if a File Exists

```Prose
If file "data.txt" exists then do the following.
    Say "File found!".
Otherwise do the following.
    Say "File not found.".
End if.
```

---

## Error Handling

Sometimes things go wrong — a file doesn't exist, a number is divided by zero, a network request fails. Use `Try` to handle errors gracefully:

```Prose
Try the following.
    Let data be the contents of "missing_file.txt".
    Say data.
If it fails do the following.
    Say "Could not read the file. Maybe it doesn't exist.".
End try.
```

Without `Try`, an error would crash your program. With it, you catch the problem and decide what to do.

---

## Importing Modules

Prose comes with built-in modules for math, time, HTTP requests, and databases.

### Math Module

```Prose
Import "math".

Let result be the result of calling math_sqrt with 144.
Say result.    Note: 12.0

Say math_pi.   Note: 3.14159...
```

Available: `math_sqrt`, `math_sin`, `math_cos`, `math_tan`, `math_log`, `math_floor`, `math_ceil`, `math_pi`

### Time Module

```Prose
Import "time".

Let start be the result of calling time_now.

Note: Do some work here...
Repeat 1000 times do the following.
    Let x be 1 plus 1.
End repeat.

Let end be the result of calling time_now.
Let elapsed be end minus start.
Say "Took " plus elapsed plus " seconds.".
```

### HTTP Requests

```Prose
Let response be the result of http get "https://httpbin.org/get".
Say response.
```

For POST requests with data:

```Prose
Let response be http post "https://httpbin.org/post" with "key=value".
```

### JSON Parsing

```Prose
Let data be json of "{\"name\": \"Alice\", \"age\": 30}".
```

---

## Splitting Your Code into Multiple Files

If your program gets really big, you can put functions in separate files and import them.

Say you have a file called `helpers.Prose` with some utility functions. Import it like this:

```Prose
Import functions from "helpers.Prose".
```

Or import specific functions:

```Prose
Import { greet, add } from "helpers.Prose".
```

---

## What's Next

[Part 5](05_advanced_features.md) covers classes, GUIs, databases, async code, and how to speed up your programs with the transpiler.
