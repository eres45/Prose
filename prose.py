"""
rose.py — Entry point for the Prose language interpreter.

Usage:
    python prose.py <filename.prose>
    python prose.py --interactive
    python prose.py --help
"""

import sys
import os
import difflib

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError_, StopException, SkipException

# ─── Beautiful error formatting ───────────────────────────────────────────────

TIPS = {
    "variable": "💡 Tip: Create a variable first with:  Let {name} be ...",
    "function": "💡 Tip: Define a function first with:  Define a function called {name} that ...",
    "class":    "💡 Tip: Define a class first with:     Define a class called {name} with ...",
    "method":   "💡 Tip: Make sure you spelled the method name correctly.",
    "type":     "💡 Tip: Make sure you're using the right kind of value here.",
    "division": "💡 Tip: You cannot divide by zero. Check your divisor first.",
    "file":     "💡 Tip: Double-check the file path and make sure the file exists.",
    "generic":  "💡 Tip: Read the error above carefully — it says exactly what went wrong.",
}

def _suggest_name(name: str, candidates: list, n: int = 1) -> list:
    """Use difflib to find close matches from a list of candidates."""
    return difflib.get_close_matches(name, candidates, n=n, cutoff=0.6)

def _extract_name_from_error(msg: str) -> str:
    """Try to extract the variable/function name from an error message."""
    import re
    patterns = [
        r"variable called '([^']+)'",
        r"function called '([^']+)'",
        r"class called '([^']+)'",
        r"method '([^']+)'",
        r"'([^']+)' not found",
    ]
    for p in patterns:
        m = re.search(p, msg)
        if m:
            return m.group(1)
    return ""

def _get_tip_key(msg: str) -> str:
    msg_lower = msg.lower()
    if "variable" in msg_lower or "could not find" in msg_lower:
        return "variable"
    if "function" in msg_lower and "not found" in msg_lower:
        return "function"
    if "class" in msg_lower:
        return "class"
    if "method" in msg_lower and "not found" in msg_lower:
        return "method"
    if "divide by zero" in msg_lower or "division" in msg_lower:
        return "division"
    if "file" in msg_lower:
        return "file"
    if "cannot" in msg_lower or "expected" in msg_lower or "type" in msg_lower:
        return "type"
    return "generic"

def _format_runtime_error(e: RuntimeError_, interp: Interpreter = None) -> str:
    msg = str(e)
    lines = [f"\n❌  Something went wrong:\n"]
    lines.append(f"   {msg}\n")

    # Suggestion for misspelled names
    name = _extract_name_from_error(msg)
    if name and interp:
        all_names = (
            list(interp.global_env.vars.keys()) +
            list(interp.functions.keys()) +
            list(interp.classes.keys())
        )
        suggestions = _suggest_name(name, all_names)
        if suggestions:
            lines.append(f"   🤔 Did you mean:  '{suggestions[0]}'?\n")

    # Tip
    tip_key = _get_tip_key(msg)
    tip = TIPS.get(tip_key, TIPS["generic"])
    if "{name}" in tip and name:
        tip = tip.format(name=name)
    lines.append(f"   {tip}\n")

    # Stack trace
    if hasattr(e, 'plain_stack') and e.plain_stack:
        lines.append("   📍 Called from:")
        for frame in reversed(e.plain_stack):
            lines.append(f"      → {frame}")
        lines.append("")

    return "\n".join(lines)

def _format_parse_error(e: ParseError) -> str:
    msg = str(e)
    return (
        f"\n📖  I couldn't understand part of your program:\n"
        f"   {msg}\n\n"
        f"   💡 Tip: Check your spelling and make sure each sentence ends with a period.\n"
        f"   💡 Common keywords: Let, Say, If, While, For, Define, Call, Add, Set, Run, Create.\n"
    )

def _format_lexer_error(e: LexerError) -> str:
    msg = str(e)
    return (
        f"\n🔤  I found something I couldn't read:\n"
        f"   {msg}\n\n"
        f"   💡 Tip: Check for unusual characters or unclosed quotes in your program.\n"
    )

# ─── Runner ───────────────────────────────────────────────────────────────────

def run_source(source: str, filename: str = "<input>"):
    try:
        tokens = Lexer(source).tokenize()
    except LexerError as e:
        print(_format_lexer_error(e))
        return False, None

    try:
        ast = Parser(tokens).parse()
    except ParseError as e:
        print(_format_parse_error(e))
        return False, None

    interp = Interpreter()
    try:
        interp.execute(ast, interp.global_env)
    except RuntimeError_ as e:
        print(_format_runtime_error(e, interp))
        return False, interp
    except StopException:
        print("\n⚠️  'Stop loop.' can only be used inside a loop.\n")
        return False, interp
    except SkipException:
        print("\n⚠️  'Skip to next.' can only be used inside a loop.\n")
        return False, interp
    except KeyboardInterrupt:
        print("\n\n👋  Your program was stopped.")
        return False, interp

    return True, interp


def run_file(path: str):
    if not os.path.exists(path):
        print(
            f"\n📁  I couldn't find the file:  '{path}'\n"
            f"   💡 Check the spelling and make sure the file is in the right folder.\n"
        )
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    success, _ = run_source(source, path)
    if not success:
        sys.exit(1)


def run_interactive():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   Welcome to Prose — Write programs in plain English  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print("  Type your Prose code and press Enter twice to run it.")
    print("  Type 'help' to see examples.  Type 'quit' to leave.")
    print()
    interp = Interpreter()

    while True:
        lines = []
        try:
            while True:
                prompt = "... " if lines else ">>> "
                line = input(prompt)
                if line.strip().lower() in ("quit", "exit"):
                    print("\n👋  Goodbye! Happy coding!\n")
                    return
                if line.strip().lower() == "help":
                    _print_help()
                    lines = []
                    break
                lines.append(line)
                if line.strip() == "":
                    break
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋  Goodbye!\n")
            return

        source = "\n".join(lines)
        if not source.strip():
            continue

        try:
            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()
            interp.execute(ast, interp.global_env)
        except RuntimeError_ as e:
            print(_format_runtime_error(e, interp))
        except (LexerError, ParseError) as e:
            print(f"\n📖  {e}\n")


def _print_help():
    print("""
┌─────────────────────────────────────────────────────┐
│                   Prose Quick Guide                  │
├─────────────────────────────────────────────────────┤
│  Variables:   Let name be "Alice".                  │
│               Let age be 25.                        │
│               Let score be score + 10.              │
│                                                     │
│  Output:      Say "Hello, world!".                  │
│               Say name.                             │
│                                                     │
│  Input:       Ask user for name.                    │
│                                                     │
│  Conditions:  If age > 18 then do the following.   │
│               ...  End if.                          │
│                                                     │
│  Loops:       Repeat 5 times do the following.     │
│               ...  End repeat.                      │
│                                                     │
│               For each number from 1 to 10 do ...  │
│               End for.                              │
│                                                     │
│  Functions:   Define a function called greet that  │
│               takes name and does the following.   │
│                   Say "Hi, " plus name plus "!".  │
│               End function.                         │
│               Call greet with "Alice".              │
│                                                     │
│  Lists:       Let items be a list containing 1,2,3.│
│               Add 4 to items.                       │
│                                                     │
│  GUI:         Create a window called w with        │
│                 title "App" and size 400 by 300.   │
│               Add a button "Click" to w that does  │
│                 the following.                      │
│                   Say "Clicked!".                  │
│               End button.                           │
│               Run w.                                │
└─────────────────────────────────────────────────────┘
""")


def _print_usage():
    print("""
╔══════════════════════════════════════════════════════╗
║                       Prose                          ║
║       Write programs in plain English!               ║
╚══════════════════════════════════════════════════════╝

Usage:
  python prose.py <yourfile.prose>      Run a program
  python prose.py --interactive         Interactive mode
  python prose.py --help                Show this help

Examples:
  python prose.py hello.prose
  python prose.py samples/sample32_calculator.prose

Tip: Prose files end with .prose and read like plain English sentences!
""")


def run_build(path: str):
    if not os.path.exists(path):
        print(f"\n📁  I couldn't find the file:  '{path}'\n")
        sys.exit(1)
    
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    
    try:
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
    except Exception as e:
        print(f"\n❌  Build failed during parsing:\n{e}")
        sys.exit(1)
        
    from transpiler import Transpiler
    t = Transpiler()
    py_code = t.transpile(ast)
    
    out_path = path
    if out_path.endswith(".prose"):
        out_path = out_path[:-6] + ".py"
    elif out_path.endswith(".plain"):
        out_path = out_path[:-6] + ".py"
    else:
        out_path += ".py"
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(py_code)
        
    print(f"\n🚀 Successfully built native Python script: {out_path}")
    print(f"You can now run it instantly with: python {os.path.basename(out_path)}\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--interactive", "-i"):
        run_interactive()
    elif sys.argv[1] in ("--help", "-h"):
        _print_usage()
        _print_help()
    elif sys.argv[1] == "build" and len(sys.argv) == 3:
        run_build(sys.argv[2])
    else:
        run_file(sys.argv[1])


if __name__ == "__main__":
    main()
