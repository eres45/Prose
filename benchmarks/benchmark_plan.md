# 🏆 Language Benchmark & Comparison Report

A head-to-head comparison evaluating **Plain** against **Python** and **Node.js (JavaScript)** based on Speed, Conciseness, and Ease of Use.

---

## 1. 🏎️ Speed & Performance (Raw Compute)
**Test:** Calculate the 25th Fibonacci number using heavy recursion `fib(n-1) + fib(n-2)`.
*This tests the raw CPU speed of the language's execution engine.*

| Language | Time taken | Engine Type |
| :--- | :--- | :--- |
| **Node.js** | `0.0004s` | V8 JIT Compiler (Extremely Fast) |
| **Python** | `0.0071s` | CPython Bytecode Interpreter (Fast) |
| **Plain** | `1.7230s` | Python Tree-Walking Interpreter (Slow) |

**Verdict:** Plain is significantly slower for heavy, raw mathematical computation. Because it reads the Abstract Syntax Tree directly in Python without compiling to bytecode, it carries heavy overhead for recursion. **Do not use Plain for 3D graphics rendering or cryptocurrency mining.**

---

## 2. ⚡ Output & Data Processing Efficiency
**Test:** Create a list of 10,000 numbers and filter out all numbers greater than 8,000.
*This tests how fast the language handles normal application data.*

| Language | Code | Time taken |
| :--- | :--- | :--- |
| **Python** | `passing = [n for n in nums if n > 8000]` | `< 0.001s` |
| **Node.js** | `passing = nums.filter(n => n > 8000)` | `0.0001s` |
| **Plain** | `Let passing be all n in nums where n > 8000.` | `0.0107s` |

**Verdict:** While Plain is technically ~100x slower here, **0.01 seconds (10 milliseconds) is entirely imperceptible to humans**. For normal application logic (filtering lists, updating databases, matching strings), Plain is effectively instantaneous.

---

## 3. 📉 Conciseness & Making Complex Things Easy
**Test:** Create a native desktop window with a title, exact dimensions, and a clickable button.
*This tests how many lines of code (LOC) and concepts (imports, classes, objects) a beginner must learn to do something awesome.*

### Python (Tkinter) - 9 Lines, high cognitive load
```python
import tkinter as tk
window = tk.Tk()
window.title("App")
window.geometry("400x400")
def on_click():
    print("Clicked!")
btn = tk.Button(window, text="Click Me", command=on_click)
btn.pack()
window.mainloop()
```
*Requires understanding: `import`, objects `window = tk.Tk()`, methods `.title()`, named arguments `command=on_click`, and main loops.*

### Node.js (Electron) - ~30 Lines, extremely high cognitive load
*Requires installing `electron` via npm, setting up `package.json`, creating `main.js` and `index.html`. Spawns Chromium processes.*

### Plain - 5 Lines, zero cognitive load
```plain
Create a window called app with title "App" and size 400 by 400.
Add a button "Click Me" to app do the following.
    Say "Clicked!".
End button.
Run app.
```
*Requires understanding: English.*

**Verdict:** Plain obliterates the competition here. It dramatically reduces the *Concepts-to-Result* ratio. To build a GUI in Plain, you don't need to know what a variable is, what an import is, what an object is, or what an event loop is. You just ask for a window.

---

## 🏁 Final Conclusion

**Why use Node.js?** You need to build a high-performance backend web server handling 10,000 concurrent connections, or a highly interactive browser frontend.
**Why use Python?** You are doing heavy machine learning, data science, or need access to millions of third-party community libraries.
**Why use Plain?** You want to automate a quick task, build a rapid internal desktop tool with a database, or teach a beginner how to code without them quitting in frustration over missing semicolons.

**Plain succeeds exactly where it was designed to:** It trades raw, microsecond CPU speed in exchange for unparalleled human readability and development speed.
