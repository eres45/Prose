# Plain Language Specification

**Version 1.0** — February 2026

Plain is a natural-English programming language where programs read like readable English sentences. The only punctuation symbols permitted are the **comma** (`,`) and the **period** (`.`).

---

## 1. Lexical Rules

- Programs are composed of **words** (alphabetic), **numbers** (digits and optional decimal point), **commas**, and **periods**.
- No special symbols are permitted (`=`, `+`, `-`, `*`, `/`, `{`, `}`, `(`, `)`, `"`, etc.).
- Keywords and identifiers are case-sensitive on the first letter by convention, but the interpreter is case-insensitive for all reserved words.
- Statements end with a **period** (`.`).
- **Commas** (`,`) are used as separators in argument lists and `Say` parts.
- Whitespace and newlines are ignored except as token separators.

---

## 2. Data Types

| Type    | Description                   | Examples         |
|---------|-------------------------------|------------------|
| Number  | Integer or decimal             | `25`, `3`, `1.5` |
| Text    | A word or sequence of words   | `hello`, `hello world` |
| Boolean | A truth value                  | `true`, `false`  |

---

## 3. Variables

### Declaration and Assignment

```
Let <name> be <expression>.
```

**Examples:**
```
Let age be 25.
Let name be John.
Let message be hello world.
Let flag be true.
```

- Variable names must be single words.
- Reassignment uses the same syntax.

---

## 4. Arithmetic Expressions

All operators are written as English words:

| Operation      | Keyword         | Example                        |
|----------------|-----------------|--------------------------------|
| Addition       | `plus`          | `age plus 10`                  |
| Subtraction    | `minus`         | `result minus age`             |
| Multiplication | `times`         | `total times 3`                |
| Division       | `divided by`    | `result divided by 2`          |

Precedence: `times` and `divided by` have higher precedence than `plus` and `minus`.

**Examples:**
```
Let total be age plus 10.
Let result be total times 3.
Let diff be result minus age.
Let half be result divided by 2.
```

---

## 5. Conditions

Conditions compare two expressions using the following operators:

| Condition                  | Keyword phrase                                |
|----------------------------|-----------------------------------------------|
| Equal                      | `is equal to` or `equals`                     |
| Not equal                  | `is not equal to`                             |
| Greater than               | `is greater than`                             |
| Less than                  | `is less than`                                |
| Greater than or equal      | `is greater than or equal to`                 |
| Less than or equal         | `is less than or equal to`                    |

---

## 6. Output

### Display (shows a single value)
```
Display <expression>.
```

### Say (concatenates multiple parts)
```
Say <part>, <part>, <part>.
```
Parts that match variable names are replaced with their values. Other parts are treated as literal text.

**Examples:**
```
Display age.
Display message.
Say hello world.
Say welcome, name, you are an adult.
```

---

## 7. Input

```
Ask the user for <name>.
```

The interpreter prompts the user. If the input looks like a number, it is stored as a number; otherwise it is stored as text.

**Example:**
```
Ask the user for name.
Ask the user for age.
```

---

## 8. Conditionals

```
If <condition> then do the following.
  <statements>
Otherwise do the following.
  <statements>
End if.
```

The `Otherwise` block is optional.

**Example:**
```
If age is greater than 18 then do the following.
  Display you are an adult.
Otherwise do the following.
  Display you are a minor.
End if.
```

---

## 9. Loops

### Repeat (fixed count)
```
Repeat <number> times do the following.
  <statements>
End repeat.
```

### While (condition-based)
```
While <condition> do the following.
  <statements>
End while.
```

**Examples:**
```
Repeat 5 times do the following.
  Display hello.
End repeat.

While age is less than 30 do the following.
  Let age be age plus 1.
End while.
```

---

## 10. Functions

### Definition
```
Define a function called <name> that takes <param1>, <param2>, and <paramN> and does the following.
  <statements>
End function.
```

For a single parameter, omit the `and`:
```
Define a function called <name> that takes <param> and does the following.
```

### Return Value
```
Give back <expression>.
```

### Calling a Function (standalone)
```
Call <name> with <arg1>, <arg2>.
```

### Calling a Function (capturing return value)
```
Let <variable> be the result of calling <name> with <arg1>, <arg2>.
```

**Examples:**
```
Define a function called greet that takes name and does the following.
  Say hello, name.
End function.

Call greet with John.

Define a function called add that takes a and b and does the following.
  Give back a plus b.
End function.

Let result be the result of calling add with 3, 5.
```

---

## 11. Formal Grammar (BNF)

```
program       := statement*

statement     := let_stmt
              |  display_stmt
              |  say_stmt
              |  ask_stmt
              |  if_stmt
              |  repeat_stmt
              |  while_stmt
              |  func_def
              |  call_stmt
              |  let_result_stmt
              |  give_back_stmt

let_stmt      := "Let" IDENT "be" expr "."
let_result    := "Let" IDENT "be" "the" "result" "of" "calling" IDENT "with" arg_list "."
display_stmt  := "Display" expr "."
say_stmt      := "Say" say_part { "," say_part } "."
ask_stmt      := "Ask" "the" "user" "for" IDENT "."

if_stmt       := "If" condition "then" "do" "the" "following" "."
                   block
                 [ "Otherwise" "do" "the" "following" "." block ]
                 "End" "if" "."

repeat_stmt   := "Repeat" NUMBER "times" "do" "the" "following" "."
                   block
                 "End" "repeat" "."

while_stmt    := "While" condition "do" "the" "following" "."
                   block
                 "End" "while" "."

func_def      := "Define" "a" "function" "called" IDENT
                   "that" "takes" param_list "and" "does" "the" "following" "."
                   block
                 "End" "function" "."

call_stmt     := "Call" IDENT "with" arg_list "."
give_back     := "Give" "back" expr "."

condition     := expr "is" "greater" "than" expr
              |  expr "is" "less" "than" expr
              |  expr "is" "greater" "than" "or" "equal" "to" expr
              |  expr "is" "less" "than" "or" "equal" "to" expr
              |  expr "is" "equal" "to" expr
              |  expr "is" "not" "equal" "to" expr
              |  expr "equals" expr
              |  expr "is" expr

expr          := term { ( "plus" | "minus" ) term }
term          := factor { ( "times" | "divided" "by" ) factor }
factor        := NUMBER | "true" | "false" | IDENT | word_sequence

param_list    := IDENT { "," IDENT } [ "and" IDENT ]
arg_list      := expr { "," expr }
block         := statement*

IDENT         := letter { letter }
NUMBER        := digit+ [ "." digit+ ]
```

---

## 12. Error Messages

All runtime errors are reported in plain English:

- `I could not find a variable called 'age'. Please make sure you have declared it before using it.`
- `I could not find a function called 'greet'. Please make sure you have defined it before calling it.`
- `I cannot divide by zero. Please check your program.`
- `I need a number for this comparison but 'hello' is not a number.`
- `I have been repeating this loop for a very long time and it does not seem to stop.`
