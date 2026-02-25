# Part 5 — Advanced Features

By this point you know enough to build real programs. This part covers the power features — desktop apps, databases, classes, and how to speed your code up significantly.

---

## Classes and Objects

Classes let you group related data and behaviour together. Think of a class as a blueprint for something.

```Prose
Define a class called Person with properties name and age.
```

Creating a new person:

```Prose
Let p be a new Person with name "Alice" and age 30.
```

Reading properties:

```Prose
Say the name of p.
Say the age of p.
```

Setting properties:

```Prose
Set the age of p to 31.
```

### Methods

Methods are functions that belong to a class.

```Prose
Define a method called greet on Person that takes no parameters and does the following.
    Say "Hi, I'm " plus the name of self plus ".".
End method.

Call greet on p.
```

### Inheritance

One class can extend another:

```Prose
Define a class called Employee with properties name and age and company.
    Inherits from Person.

Define a method called introduce on Employee that takes no parameters and does the following.
    Say "I'm " plus the name of self plus " from " plus the company of self plus ".".
End method.
```

---

## Building Desktop GUIs

Prose can build real native desktop windows using simple English.

```Prose
Create a window called app with title "My App" and size 400 by 300.
```

### Adding Widgets

```Prose
Add a label "Enter your name:" to app at row 0 column 0.
Add an input called name_box to app at row 0 column 1.
Add a button "Submit" to app at row 1 column 0 that does the following.
    Let name be the text of name_box.
    Say "Hello, " plus name plus "!".
End button.
```

### Other Widgets

```Prose
Add a text area called notes to app at row 2 column 0 spanning 2 columns.
Add a checkbox called dark_mode to app with label "Enable dark mode".
Add a dropdown called size_select to app with options "Small", "Medium", "Large".
```

### Events

Respond to things the user does:

```Prose
When user presses Enter on name_box do the following.
    Say "Enter was pressed!".
End when.

When window closes do the following.
    Say "Goodbye!".
End when.
```

### Starting the App

Always end a GUI program with:

```Prose
Run app.
```

---

## Built-in Database

Prose has a built-in database that stores data permanently (using SQLite under the hood).

```Prose
Import { create_table, save, find_all, find_where, delete_where, count } from "database".

Note: Create a table
Call create_table with "users", "name", "email", "age".

Note: Add some rows
Call save with "users", "Alice", "alice@example.com", "30".
Call save with "users", "Bob", "bob@example.com", "25".

Note: Get all rows
Let all_users be the result of calling find_all with "users".
For each user in all_users do the following.
    Say user.
End for.

Note: Filter by a column
Let found be the result of calling find_where with "users", "name", "Alice".

Note: Delete a row
Call delete_where with "users", "name", "Bob".

Note: Count rows
Let total be the result of calling count with "users".
Say "Total users: " plus total.
```

---

## Async Operations

If you're doing something that takes time (like waiting for a server response), you can run it without freezing the rest of your program.

```Prose
Define an async function called load_data that takes no parameters and does the following.
    Let data be the result of http get "https://api.example.com/data".
    Say data.
End function.

Call load_data.
```

---

## Switch/Check Statements

When you have many possible values to check, `Check` is cleaner than a chain of `If` statements:

```Prose
Let day be "Monday".

Check day.
    When "Monday" do the following.
        Say "Start of the week.".
    End when.
    When "Friday" do the following.
        Say "Almost the weekend!".
    End when.
    When "Saturday" or "Sunday" do the following.
        Say "Weekend!".
    End when.
    Otherwise do the following.
        Say "Just another weekday.".
    End otherwise.
End check.
```

---

## Enumerations

When you have a fixed set of named values:

```Prose
Define an enum called Direction with values North, South, East, West.

Let heading be Direction.North.
Say heading.
```

---

## Speeding Up Your Programs

If your program does a lot of heavy computation (big loops, lots of math), you can compile it to native Python first:

```
python Prose.py build myprogram.Prose
python myprogram.py
```

This can make your program **hundreds of times faster** for things like nested loops or large-scale data processing. The generated `.py` file is clean, readable Python — you can even look at it to understand what Prose is doing under the hood.

---

## Running Prose Interactively

The REPL (interactive mode) is great for quickly testing things:

```
python Prose.py --interactive
```

Type `help` inside to see a cheat sheet of all the keywords.

---

## Quick Reference

| Feature | Example |
| :--- | :--- |
| Variable | `Let x be 10.` |
| Print | `Say "Hello!".` |
| Input | `Ask user for name.` |
| Condition | `If x > 5 then do the following. ... End if.` |
| Repeat N times | `Repeat 10 times do the following. ... End repeat.` |
| Range loop | `For each i from 1 to 100 step 2 do the following. ... End for.` |
| List | `Let items be a list containing 1, 2, 3.` |
| Filter | `Let big be all x in items where x > 2.` |
| Function | `Define a function called add that takes a and b and does the following. ... End function.` |
| Class | `Define a class called Dog with properties name and breed.` |
| GUI window | `Create a window called app with title "App" and size 400 by 400.` |
| Database | `Import { save, find_all } from "database".` |
| File read | `Let text be the contents of "file.txt".` |
| Error handling | `Try the following. ... If it fails do the following. ... End try.` |
| HTTP | `Let data be the result of http get "https://example.com".` |

---

You now know everything Prose has to offer. Go build something.
