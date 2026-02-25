"""
prose Language Interpreter — Phase 3
All Phase 2 features plus:
  - String ops: split, join, trim, replace, repeat, contains, index of
  - Math stdlib: round, abs, sqrt, floor, ceiling, random, min, max, power
  - Type conversion: as a number, as text
  - Error handling: Try / Handle error / End try
  - List: sort, contains, index of
"""

from __future__ import annotations
import math
import random
import sys
import os
import datetime
import json
import urllib.request
import urllib.error
import re
import threading
from typing import Any, Dict, List, Optional
from .parser import (
    NumberLiteral, StringLiteral, BoolLiteral, NoneLiteral, LiteralNode,
    Identifier, BinOp, UnaryMinus,
    Condition, CompoundCondition,
    LetStmt, DisplayStmt, SayStmt, AskStmt,
    IfStmt, RepeatStmt, WhileStmt, ForEachStmt,
    FunctionDef, CallStmt, LetResultStmt, GiveBackStmt,
    AddToListStmt, RemoveFromListStmt,
    ListLiteral, ListAccess, LengthOf, UppercaseOf, LowercaseOf,
    TypeCheck, StopStmt, SkipStmt,
    # Phase 3
    ContainsExpr, ReplaceIn, SplitBy, JoinWith, TrimOf, RepeatStr,
    ListContainsExpr, SortList, IndexOf,
    RoundOf, AbsOf, RandomBetween, MinOf, MaxOf, SqrtOf, FloorOf, CeilingOf, PowerOf,
    AsNumber, AsText,
    TryCatch,
    # Phase 4
    DictLiteral, DictAccess, DictKeys, SetDictValueStmt, RemoveDictValueStmt,
    FileContents, FileExists, WriteFileStmt, AppendFileStmt, ImportStmt, ThrowStmt, TimeOp,
    # Phase 5
    JsonParseExpr, JsonStringifyExpr, HttpGetExpr, HttpPostExpr,
    ClassDef, MethodDef, NewInstanceExpr, PropertyAccessExpr, SetPropertyStmt, MethodCallStmt,
    # Phase 6
    InterpolatedString, CheckStmt, LambdaExpr, MapExpr, FilterExpr,
    EnumDef, EnumAccess, CliArgsExpr, EnvVarExpr,
    TestBlock, AssertStmt, RunTestsStmt,
    RegexMatchExpr, RegexTestExpr,
    StringIndexExpr, StringSliceExpr,
    AttemptStmt, ParamDef, WaitExpr, BlockLambda,
    CreateWindowStmt, AddWidgetStmt, RunWindowStmt, SetTextStmt,
    RangeLoopStmt, AllWhereExpr, WhenStmt
)

# ─── Control-flow signals ──────────────────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

class StopException(Exception): pass
class SkipException(Exception): pass
class RuntimeError_(Exception): pass


# ─── Environment (Scope) ──────────────────────────────────────────────────────

class Environment:
    def __init__(self, parent: Optional[Environment] = None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str, line: int = 0) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise RuntimeError_(
            f"Line {line}: I could not find a variable called '{name}'. "
            f"Please make sure you have declared it before using it."
        )

    def assign(self, name: str, value: Any):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            self.vars[name] = value

    def set_local(self, name: str, value: Any):
        self.vars[name] = value


class Closure:
    """A function combined with the environment in which it was defined."""
    def __init__(self, node: Any, env: Environment):
        self.node = node
        self.env = env
        
    def __str__(self):
        return "<function>"


# ─── OOP Runtime Objects ──────────────────────────────────────────────────────

class Instance:
    def __init__(self, class_def: ClassDef, properties: Dict[str, Any]):
        self.class_name = class_def.name
        self.properties = properties
        
    def __str__(self):
        return f"<Object {self.class_name} {self.properties}>"

    def __repr__(self):
        return self.__str__()


# ─── Interpreter ──────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions: Dict[str, FunctionDef] = {}
        self.classes: dict[str, Any] = {}
        self.methods: dict[str, dict[str, Any]] = {}
        self.enums: Dict[str, EnumDef] = {}
        self.tests: List[TestBlock] = []

    def execute(self, statements: List[Any], env: Environment):
        for stmt in statements:
            self.execute_stmt(stmt, env)

    def execute_stmt(self, node: Any, env: Environment):
        t = type(node)
        if t is LetStmt:            self._exec_let(node, env)
        elif t is LetResultStmt:    self._exec_let_result(node, env)
        elif t is DisplayStmt:      self._exec_display(node, env)
        elif t is SayStmt:          self._exec_say(node, env)
        elif t is AskStmt:          self._exec_ask(node, env)
        elif t is IfStmt:           self._exec_if(node, env)
        elif t is RepeatStmt:       self._exec_repeat(node, env)
        elif t is WhileStmt:        self._exec_while(node, env)
        elif t is ForEachStmt:      self._exec_for_each(node, env)
        elif t is FunctionDef:      self.functions[node.name] = node
        elif t is CallStmt:         self._exec_call(node, env)
        elif t is GiveBackStmt:
            raise ReturnException(self.evaluate(node.expr, env))
        elif t is AddToListStmt:    self._exec_add_to_list(node, env)
        elif t is RemoveFromListStmt: self._exec_remove_from_list(node, env)
        elif t is StopStmt:         raise StopException()
        elif t is SkipStmt:         raise SkipException()
        elif t is SortList:         self._exec_sort_list(node, env)
        elif t is TryCatch:         self._exec_try_catch(node, env)
        elif t is SetDictValueStmt: self._exec_set_dict_value(node, env)
        elif t is RemoveDictValueStmt: self._exec_remove_dict_value(node, env)
        elif t is WriteFileStmt:    self._exec_write_file(node, env)
        elif t is AppendFileStmt:   self._exec_append_file(node, env)
        elif t is ImportStmt:       self._exec_import(node, env)
        elif t is ThrowStmt:        self._exec_throw(node, env)
        # Phase 5
        elif t is ClassDef:         self._exec_class_def(node, env)
        elif t is MethodDef:        self._exec_method_def(node, env)
        elif t is SetPropertyStmt:  self._exec_set_property(node, env)
        elif t is MethodCallStmt:   self._exec_method_call(node, env)
        # Phase 6
        elif t is CheckStmt:        self._exec_check(node, env)
        elif t is EnumDef:          self._exec_enum_def(node, env)
        elif t is TestBlock:        self._exec_test_block(node, env)
        elif t is AssertStmt:       self._exec_assert(node, env)
        elif t is RunTestsStmt:     self._exec_run_tests(node, env)
        # Phase 8
        elif t is AttemptStmt:      self._exec_attempt(node, env)
        # Phase A — GUI
        elif t is CreateWindowStmt: self._exec_create_window(node, env)
        elif t is AddWidgetStmt:    self._exec_add_widget(node, env)
        elif t is RunWindowStmt:    self._exec_run_window(node, env)
        elif t is SetTextStmt:      self._exec_set_text(node, env)
        # Phase B — Beginner features
        elif t is RangeLoopStmt:    self._exec_range_loop(node, env)
        elif t is WhenStmt:         self._exec_when(node, env)
        else:
            raise RuntimeError_(f"I do not know how to execute: {type(node).__name__}.")

    # ── Statements ────────────────────────────────────────────────────────────

    def _exec_let(self, node: LetStmt, env: Environment):
        env.assign(node.name, self.evaluate(node.expr, env))

    def _exec_let_result(self, node: LetResultStmt, env: Environment):
        val = self._execute_call_chain(node.func_name, node.args, getattr(node, "obj_expr", None), getattr(node, "chained_calls", None), env, node.line)
        env.assign(node.variable, val)

    def _exec_display(self, node: DisplayStmt, env: Environment):
        print(self._to_display(self.evaluate(node.expr, env)))

    def _exec_say(self, node: SayStmt, env: Environment):
        parts = []
        for part in node.parts:
            if isinstance(part, Identifier):
                try:
                    parts.append(self._to_display(self.evaluate(part, env)))
                except RuntimeError_:
                    parts.append(part.name)
            else:
                parts.append(self._to_display(self.evaluate(part, env)))
        print(" ".join(parts))

    def _exec_ask(self, node: AskStmt, env: Environment):
        try:
            raw = input(f"Please enter a value for {node.variable}: ")
        except EOFError:
            raw = ""
        try:
            v = float(raw)
            value: Any = int(v) if v == int(v) else v
        except ValueError:
            value = raw
        env.assign(node.variable, value)

    def _exec_if(self, node: IfStmt, env: Environment):
        if self.evaluate_condition(node.condition, env):
            self.execute(node.then_body, Environment(parent=env))
        elif node.else_body:
            self.execute(node.else_body, Environment(parent=env))

    def _exec_repeat(self, node: RepeatStmt, env: Environment):
        count = self.evaluate(node.count, env)
        if not isinstance(count, (int, float)):
            raise RuntimeError_(f"Line {node.line}: Repeat needs a number, got '{count}'.")
        try:
            for _ in range(int(count)):
                try:
                    self.execute(node.body, Environment(parent=env))
                except SkipException:
                    continue
        except StopException:
            pass

    def _exec_while(self, node: WhileStmt, env: Environment):
        count = 0
        try:
            while self.evaluate_condition(node.condition, env):
                count += 1
                if count > 10_000_000:
                    raise RuntimeError_("I have been repeating this loop for far too long. Please check your While condition.")
                try:
                    self.execute(node.body, Environment(parent=env))
                except SkipException:
                    continue
        except StopException:
            pass

    def _exec_for_each(self, node: ForEachStmt, env: Environment):
        iterable = self.evaluate(node.iterable, env)
        if isinstance(iterable, str):
            items: Any = list(iterable)
        elif isinstance(iterable, list):
            items = list(iterable)   # copy so mutations mid-loop are safe
        else:
            raise RuntimeError_(f"Line {node.line}: I can only use 'For each' on a list or text.")
        child_env = Environment(parent=env)
        try:
            for item in items:
                child_env.assign(node.var, item)
                try:
                    self.execute(node.body, Environment(parent=child_env))
                except SkipException:
                    continue
        except StopException:
            pass

    def _exec_call(self, node: CallStmt, env: Environment):
        self._execute_call_chain(node.name, node.args, getattr(node, "obj_expr", None), getattr(node, "chained_calls", None), env, node.line)

    def _execute_call_chain(self, name: str, args: List[Any], obj_expr: Optional[Any], chained_calls: Optional[List[tuple[str, List[Any], int]]], env: Environment, line: int) -> Any:
        if obj_expr is not None:
            obj = self.evaluate(obj_expr, env)
            arg_vals = [self.evaluate(a, env) for a in args]
            current_val = self._call_method(obj, name, arg_vals, env, line)
        else:
            current_val = self._call_function(name, args, env, line)
            
        if chained_calls:
            for c_name, c_args, c_line in chained_calls:
                if current_val is None:
                    raise RuntimeError_(f"Line {c_line}: Cannot call method '{c_name}' on nothing (previous call returned nothing).")
                c_arg_vals = [self.evaluate(a, env) for a in c_args]
                current_val = self._call_method(current_val, c_name, c_arg_vals, env, c_line)
                
        return current_val

    def _exec_add_to_list(self, node: AddToListStmt, env: Environment):
        lst = env.get(node.list_name, node.line)
        if not isinstance(lst, list):
            raise RuntimeError_(f"Line {node.line}: '{node.list_name}' is not a list.")
        lst.append(self.evaluate(node.value, env))

    def _exec_remove_from_list(self, node: RemoveFromListStmt, env: Environment):
        lst = env.get(node.list_name, node.line)
        if not isinstance(lst, list):
            raise RuntimeError_(f"Line {node.line}: '{node.list_name}' is not a list.")
        idx = int(self.evaluate(node.index, env)) - 1
        if idx < 0 or idx >= len(lst):
            raise RuntimeError_(f"Line {node.line}: Item {idx+1} is out of range (list has {len(lst)} items).")
        lst.pop(idx)

    def _exec_sort_list(self, node: SortList, env: Environment):
        lst = env.get(node.list_name, node.line)
        if not isinstance(lst, list):
            raise RuntimeError_(f"Line {node.line}: '{node.list_name}' is not a list.")
        try:
            lst.sort(key=lambda x: (str(type(x)), x))
        except TypeError:
            lst.sort(key=str)

    def _exec_try_catch(self, node: TryCatch, env: Environment):
        try:
            self.execute(node.try_body, Environment(parent=env))
        except (RuntimeError_, Exception) as e:
            catch_env = Environment(parent=env)
            msg = str(e).replace("RuntimeError_: ", "")
            catch_env.set_local(node.error_var, msg)
            self.execute(node.catch_body, catch_env)

    def _exec_set_dict_value(self, node: SetDictValueStmt, env: Environment):
        d = self.evaluate(node.dict_expr, env)
        if not isinstance(d, dict):
            raise RuntimeError_(f"Line {node.line}: Can only set a value in a dictionary.")
        k = self.evaluate(node.key_expr, env)
        v = self.evaluate(node.value_expr, env)
        if isinstance(k, (list, dict)):
            raise RuntimeError_(f"Line {node.line}: A list or dictionary cannot be used as a key.")
        d[k] = v

    def _exec_remove_dict_value(self, node: RemoveDictValueStmt, env: Environment):
        d = self.evaluate(node.dict_expr, env)
        if not isinstance(d, dict):
            raise RuntimeError_(f"Line {node.line}: Can only remove a value from a dictionary.")
        k = self.evaluate(node.key_expr, env)
        if k in d:
            del d[k]

    # ── Phase 4 File / System Statements ──────────────────────────────────────

    def _exec_write_file(self, node: WriteFileStmt, env: Environment):
        content = self._to_display(self.evaluate(node.content_expr, env))
        filepath = str(self.evaluate(node.file_expr, env))
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Could not write to file '{filepath}'. ({e})")

    def _exec_append_file(self, node: AppendFileStmt, env: Environment):
        content = self._to_display(self.evaluate(node.content_expr, env))
        filepath = str(self.evaluate(node.file_expr, env))
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Could not append to file '{filepath}'. ({e})")

    def _exec_import(self, node: ImportStmt, env: Environment):
        filepath = str(self.evaluate(node.file_expr, env))
        
        # Intercept standard libraries
        if filepath == "time":
            import time
            self.functions["time_now"] = lambda: time.time()
            return
        elif filepath == "math":
            import math
            self.functions["math_sin"] = math.sin
            self.functions["math_cos"] = math.cos
            self.functions["math_tan"] = math.tan
            self.functions["math_log"] = math.log
            self.functions["math_pi"] = lambda: math.pi
            return
        elif filepath == "database":
            import sqlite3
            # Per-interpreter shared connection (in-memory by default)
            if not hasattr(self, "_db_conn"):
                self._db_conn = sqlite3.connect(":memory:")
                self._db_conn.row_factory = sqlite3.Row
            conn = self._db_conn
            module_env = Environment()

            def db_create_table(table_name, *columns):
                cols_sql = ", ".join(f"{c} TEXT" for c in columns)
                conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql})")
                conn.commit()

            def db_save(table_name, *values):
                placeholders = ", ".join("?" for _ in values)
                conn.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
                conn.commit()

            def db_find_all(table_name):
                rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
                return [dict(r) for r in rows]

            def db_find_where(table_name, column, value):
                rows = conn.execute(
                    f"SELECT * FROM {table_name} WHERE {column} = ?", (value,)
                ).fetchall()
                return [dict(r) for r in rows]

            def db_delete_where(table_name, column, value):
                conn.execute(f"DELETE FROM {table_name} WHERE {column} = ?", (value,))
                conn.commit()

            def db_count(table_name):
                row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
                return row[0] if row else 0

            module_env.set_local("create_table", db_create_table)
            module_env.set_local("save",         db_save)
            module_env.set_local("find_all",     db_find_all)
            module_env.set_local("find_where",   db_find_where)
            module_env.set_local("delete_where", db_delete_where)
            module_env.set_local("count",        db_count)

            if node.alias:
                env.assign(node.alias, module_env)
            elif node.specific_imports:
                for name in node.specific_imports:
                    try:
                        val = module_env.get(name, node.line)
                        env.assign(name, val)
                    except RuntimeError_:
                        raise RuntimeError_(f"Line {node.line}: Cannot import '{name}' from database library.")
            return
        elif filepath == "string":
            self.functions["string_startsWith"] = lambda s, p: str(s).startswith(str(p))
            self.functions["string_endsWith"] = lambda s, p: str(s).endswith(str(p))
            self.functions["string_substring"] = lambda s, a, b: str(s)[int(a):int(b)]
            return
        elif filepath == "collections":
            self.functions["collections_sort"] = lambda l: sorted(list(l))
            self.functions["collections_reverse"] = lambda l: list(reversed(list(l)))
            self.functions["collections_unique"] = lambda l: list(dict.fromkeys(list(l)))
            return
        elif filepath == "gui":
            try:
                import tkinter as tk
                from tkinter import font as tkfont
            except ImportError:
                raise RuntimeError_(f"Line {node.line}: The 'tkinter' library is required for GUI support but was not found.")

            interp_ref = self  # ref to avoid late-binding issues

            module_env = Environment()

            def _plain_instance(class_name, tk_widget, extra_props=None):
                from parser import ClassDef
                dummy_class = ClassDef(name=class_name, properties=[], parent=None)
                props = {"_tk": tk_widget}
                if extra_props:
                    props.update(extra_props)
                inst = Instance(dummy_class, props)
                return inst

            def gui_create_window(title, w=400, h=500):
                root = tk.Tk()
                root.title(str(title))
                root.geometry(f"{int(w)}x{int(h)}")
                root.configure(bg="#1e1e2e")
                inst = _plain_instance("Window", root)
                def _run():
                    root.mainloop()
                inst.properties["run"] = _run
                inst.properties["set_title"] = lambda t: root.title(str(t))
                return inst

            def gui_create_label(parent_inst, text, font_size=14, color="#cdd6f4", bg="#1e1e2e"):
                tk_parent = parent_inst.properties["_tk"]
                lbl = tk.Label(tk_parent, text=str(text),
                               font=("Segoe UI", int(font_size)),
                               fg=str(color), bg=str(bg))
                inst = _plain_instance("Label", lbl)
                def _pack(): lbl.pack(padx=8, pady=4)
                def _grid(r, c, cs=1): lbl.grid(row=int(r), column=int(c), columnspan=int(cs), padx=4, pady=4, sticky="nsew")
                def _set_text(t): lbl.config(text=str(t))
                def _get_text(): return lbl.cget("text")
                inst.properties["pack"] = _pack
                inst.properties["grid"] = _grid
                inst.properties["set_text"] = _set_text
                inst.properties["get_text"] = _get_text
                return inst

            def gui_create_input(parent_inst, font_size=18, width=20):
                tk_parent = parent_inst.properties["_tk"]
                var = tk.StringVar()
                entry = tk.Entry(tk_parent, textvariable=var,
                                 font=("Segoe UI", int(font_size)),
                                 width=int(width), justify="right",
                                 relief="flat", bg="#313244", fg="#cdd6f4",
                                 insertbackground="#cdd6f4")
                inst = _plain_instance("Input", entry)
                def _pack(): entry.pack(padx=8, pady=8, fill="x")
                def _grid(r, c, cs=1): entry.grid(row=int(r), column=int(c), columnspan=int(cs), padx=4, pady=4, sticky="nsew")
                def _set_text(t): var.set(str(t))
                def _get_text(): return var.get()
                def _append(t): var.set(var.get() + str(t))
                def _clear(): var.set("")
                inst.properties["pack"] = _pack
                inst.properties["grid"] = _grid
                inst.properties["set_text"] = _set_text
                inst.properties["get_text"] = _get_text
                inst.properties["append_text"] = _append
                inst.properties["clear"] = _clear
                return inst

            def gui_create_button(parent_inst, text, plain_callback=None, bg="#89b4fa", fg="#1e1e2e", font_size=14):
                tk_parent = parent_inst.properties["_tk"]
                def _cmd():
                    if plain_callback is not None:
                        interp_ref._call_function(plain_callback, [], interp_ref.global_env, 0)
                btn = tk.Button(tk_parent, text=str(text),
                                font=("Segoe UI", int(font_size), "bold"),
                                bg=str(bg), fg=str(fg),
                                relief="flat", cursor="hand2",
                                activebackground="#b5c8f9", activeforeground="#1e1e2e",
                                command=_cmd)
                inst = _plain_instance("Button", btn)
                def _pack(): btn.pack(padx=4, pady=4, fill="both")
                def _grid(r, c, cs=1, rs=1): btn.grid(row=int(r), column=int(c), columnspan=int(cs), rowspan=int(rs), padx=3, pady=3, sticky="nsew")
                def _set_text(t): btn.config(text=str(t))
                inst.properties["pack"] = _pack
                inst.properties["grid"] = _grid
                inst.properties["set_text"] = _set_text
                return inst

            def gui_configure_grid(parent_inst, rows, cols):
                tk_parent = parent_inst.properties["_tk"]
                for i in range(int(rows)):
                    tk_parent.rowconfigure(i, weight=1)
                for j in range(int(cols)):
                    tk_parent.columnconfigure(j, weight=1)

            module_env.set_local("create_window", gui_create_window)
            module_env.set_local("create_label", gui_create_label)
            module_env.set_local("create_input", gui_create_input)
            module_env.set_local("create_button", gui_create_button)
            module_env.set_local("configure_grid", gui_configure_grid)

            if node.alias:
                env.assign(node.alias, module_env)
            elif node.specific_imports:
                for name in node.specific_imports:
                    try:
                        val = module_env.get(name, node.line)
                        env.assign(name, val)
                    except RuntimeError_:
                        raise RuntimeError_(f"Line {node.line}: Cannot import '{name}' from gui library.")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Could not read file '{filepath}' for import. ({e})")
        
        from lexer import Lexer
        from parser import Parser
        try:
            tokens = Lexer(source).tokenize()
            statements = Parser(tokens).parse()
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Failed to understand '{filepath}': {e}")
        
        # Execute the imported file using an isolated interpreter if aliased or specific
        if node.alias or node.specific_imports:
            # Create a sandboxed interpreter to capture definitions
            sandbox = Interpreter()
            sandbox.global_env = Environment() # Isolated
            try:
                sandbox.execute(statements, sandbox.global_env)
            except StopException:
                pass
                
            module_env = sandbox.global_env
            
            # Inject functions and classes into this module scope so they can be accessed via property lookup
            for fn_name, fn_def in sandbox.functions.items():
                module_env.set_local(fn_name, fn_def)
            for cls_name, cls_def in sandbox.classes.items():
                module_env.set_local(cls_name, cls_def)
                
        else:
            module_env = self.global_env # Legacy global injection
            try:
                self.execute(statements, module_env)
            except StopException:
                pass # Stop in library just stops its initialization
            
        # Bind back into caller scope
        if node.alias:
            env.assign(node.alias, module_env)
        elif node.specific_imports:
            for name in node.specific_imports:
                try:
                    val = module_env.get(name, node.line)
                    env.assign(name, val)
                except RuntimeError_:
                    raise RuntimeError_(f"Line {node.line}: Cannot import '{name}' because it was not found in '{filepath}'.")

    def _exec_throw(self, node: ThrowStmt, env: Environment):
        msg = str(self.evaluate(node.msg_expr, env))
        raise RuntimeError_(f"Line {node.line}: " + msg)

    # ── Phase A GUI Handlers ────────────────────────────────────────────────────

    def _gui_get_tk(self):
        """Lazily import tkinter and ensure Tk is available."""
        try:
            import tkinter as tk
            return tk
        except ImportError:
            raise RuntimeError_("GUI support requires tkinter (built into Python).")

    def _exec_create_window(self, node: CreateWindowStmt, env: Environment):
        tk = self._gui_get_tk()
        from parser import ClassDef
        title  = str(self.evaluate(node.title_expr, env))
        width  = int(self.evaluate(node.width_expr, env))
        height = int(self.evaluate(node.height_expr, env))

        root = tk.Tk()
        root.title(title)
        root.geometry(f"{width}x{height}")
        root.configure(bg="#1e1e2e")
        root.resizable(True, True)

        dummy_cls = ClassDef(name="Window", properties=[], parent=None)
        inst = Instance(dummy_cls, {"_tk": root, "_type": "window", "_row": 0})

        # Add a callable run method
        inst.properties["run"] = lambda: root.mainloop()
        inst.properties["set_title"] = lambda t: root.title(str(t))

        env.assign(node.var_name, inst)

    def _exec_add_widget(self, node: AddWidgetStmt, env: Environment):
        tk = self._gui_get_tk()
        from parser import ClassDef
        window_inst = self.evaluate(node.window_expr, env)
        if not isinstance(window_inst, Instance) or "_tk" not in window_inst.properties:
            raise RuntimeError_(f"Line {node.line}: Expected a Window object.")
        tk_parent = window_inst.properties["_tk"]

        # Track current row for auto-layout
        row = window_inst.properties.get("_row", 0)
        label_text = str(self.evaluate(node.label_expr, env)) if node.label_expr else ""
        col = int(self.evaluate(node.col_expr, env)) if node.col_expr else 0
        colspan = int(self.evaluate(node.colspan_expr, env)) if node.colspan_expr else 1
        explicit_row = int(self.evaluate(node.row_expr, env)) if node.row_expr else row

        dummy_cls = ClassDef(name=node.widget_type.capitalize(), properties=[], parent=None)

        if node.widget_type == "label":
            lbl = tk.Label(tk_parent, text=label_text,
                           font=("Segoe UI", 14), fg="#cdd6f4", bg="#1e1e2e")
            lbl.grid(row=explicit_row, column=col, columnspan=colspan,
                     padx=6, pady=4, sticky="nsew")
            inst = Instance(dummy_cls, {"_tk": lbl})
            inst.properties["set_text"] = lambda t: lbl.config(text=str(t))
            inst.properties["get_text"] = lambda: lbl.cget("text")

        elif node.widget_type == "input":
            var = tk.StringVar()
            entry = tk.Entry(tk_parent, textvariable=var,
                             font=("Segoe UI", 20), justify="right",
                             relief="flat", bg="#313244", fg="#cdd6f4",
                             insertbackground="#cdd6f4")
            entry.grid(row=explicit_row, column=col, columnspan=colspan,
                       padx=6, pady=8, sticky="nsew")
            inst = Instance(dummy_cls, {"_tk": entry, "_var": var})
            inst.properties["set_text"] = lambda t: var.set(str(t))
            inst.properties["get_text"] = lambda: var.get()
            inst.properties["append_text"] = lambda t: var.set(var.get() + str(t))
            inst.properties["clear"] = lambda: var.set("")

        elif node.widget_type == "button":
            closure = self.evaluate(node.callback_body, env) if node.callback_body else None

            def make_cmd(saved_closure, saved_env):
                def _cmd():
                    if saved_closure is not None:
                        # Execute the closure body in its captured env
                        fn_node = saved_closure.node if hasattr(saved_closure, "node") else saved_closure
                        closure_env = saved_closure.env if hasattr(saved_closure, "env") else saved_env
                        call_env = Environment(parent=closure_env)
                        try:
                            self.execute(fn_node.body, call_env)
                        except ReturnException:
                            pass
                return _cmd
            cmd = make_cmd(closure, env)

            # Choose a color based on label
            bg_color = "#a6e3a1" if label_text == "=" else (
                        "#f38ba8" if label_text in ("AC", "C") else (
                        "#fab387" if label_text in ("+", "−", "×", "÷", "*", "/", "-") else
                        "#89dceb" if label_text in ("%", "⌫") else
                        "#313244"))
            fg_color = "#1e1e2e"
            btn = tk.Button(tk_parent, text=label_text,
                            font=("Segoe UI", 16, "bold"),
                            bg=bg_color, fg=fg_color,
                            relief="flat", cursor="hand2",
                            activebackground="#cdd6f4", activeforeground="#1e1e2e",
                            command=cmd)
            btn.grid(row=explicit_row, column=col, columnspan=colspan,
                     padx=3, pady=3, sticky="nsew")
            inst = Instance(dummy_cls, {"_tk": btn})
            inst.properties["set_text"] = lambda t: btn.config(text=str(t))

        else:
            raise RuntimeError_(f"Line {node.line}: Unknown widget type '{node.widget_type}'.")

        # Configure grid weights for responsive layout
        for c in range(4):
            tk_parent.columnconfigure(c, weight=1)
        for r in range(8):
            tk_parent.rowconfigure(r, weight=1)

        # Auto-advance row if no explicit row given
        if node.row_expr is None:
            window_inst.properties["_row"] = row + 1

        # Bind to var_name if one was given
        if node.var_name:
            env.assign(node.var_name, inst)

    def _exec_run_window(self, node: RunWindowStmt, env: Environment):
        window_inst = self.evaluate(node.window_expr, env)
        if isinstance(window_inst, Instance) and "_tk" in window_inst.properties:
            window_inst.properties["_tk"].mainloop()
        else:
            raise RuntimeError_(f"Line {node.line}: Expected a Window object to run.")

    def _exec_set_text(self, node: SetTextStmt, env: Environment):
        widget_inst = self.evaluate(node.widget_expr, env)
        value = str(self.evaluate(node.value_expr, env))
        if isinstance(widget_inst, Instance) and "set_text" in widget_inst.properties:
            widget_inst.properties["set_text"](value)
        else:
            raise RuntimeError_(f"Line {node.line}: Can only set text on a label or input widget.")

    # ── Phase B Handler Methods ────────────────────────────────────────────────

    def _exec_range_loop(self, node: RangeLoopStmt, env: Environment):
        """For each X from N to M [step S] do the following."""
        start = int(self.evaluate(node.from_expr, env))
        stop  = int(self.evaluate(node.to_expr, env)) + 1  # inclusive
        step  = int(self.evaluate(node.step_expr, env)) if node.step_expr else 1
        try:
            for i in range(start, stop, step):
                loop_env = Environment(parent=env)
                loop_env.set_local(node.var_name, i)
                try:
                    self.execute(node.body, loop_env)
                except SkipException:
                    continue
                except StopException:
                    break
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Error in range loop: {e}")

    def _exec_when(self, node: WhenStmt, env: Environment):
        """When user presses Enter on X / When window closes do the following."""
        try:
            import tkinter as tk
        except ImportError:
            raise RuntimeError_(f"Line {node.line}: 'When' events require GUI (tkinter).")

        body = node.body
        captured_env = env

        def make_handler(b, e):
            def _handler(event=None):
                call_env = Environment(parent=e)
                try:
                    self.execute(b, call_env)
                except ReturnException:
                    pass
            return _handler

        handler = make_handler(body, captured_env)

        if node.event == "close":
            # "When window closes" — bind to the root window
            # Walk through all Instance objects in env looking for Window type
            for val in env.vars.values():
                if isinstance(val, Instance) and val.class_name == "Window":
                    val.properties["_tk"].protocol("WM_DELETE_WINDOW", handler)
                    return

        if node.widget_expr is not None:
            widget_inst = self.evaluate(node.widget_expr, env)
            if isinstance(widget_inst, Instance) and "_tk" in widget_inst.properties:
                tk_widget = widget_inst.properties["_tk"]
                event_map = {
                    "enter":  "<Return>",
                    "escape": "<Escape>",
                    "change": "<KeyRelease>",
                }
                tk_event = event_map.get(node.event, f"<{node.event}>")
                tk_widget.bind(tk_event, handler)

    def _exec_attempt(self, node: AttemptStmt, env: Environment):

        try:
            self.execute(node.try_body, env)
        except RuntimeError_ as e:
            catch_env = Environment(parent=env)
            
            error_msg = str(e)
            if hasattr(e, 'plain_stack') and e.plain_stack:
                error_msg += "\nTraceback (most recent call last):\n"
                for frame in reversed(e.plain_stack):
                    error_msg += f"  in {frame}\n"
                    
            catch_env.set_local(node.error_var, error_msg.strip())
            self.execute(node.catch_body, catch_env)

    # ── Phase 5 Evaluation Helpers ────────────────────────────────────────────

    def _eval_json_parse(self, node: JsonParseExpr, env: Environment) -> Any:
        text = str(self.evaluate(node.text_expr, env))
        try:
            return json.loads(text)
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Could not parse JSON. ({e})")

    def _eval_json_stringify(self, node: JsonStringifyExpr, env: Environment) -> str:
        data = self.evaluate(node.dict_expr, env)
        try:
            return json.dumps(data)
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: Could not stringify to JSON. ({e})")

    def _eval_http_get(self, node: HttpGetExpr, env: Environment) -> Any:
        url = str(self.evaluate(node.url_expr, env))
        try:
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: HTTP GET failed for '{url}'. ({e})")

    def _eval_http_post(self, node: HttpPostExpr, env: Environment) -> Any:
        url = str(self.evaluate(node.url_expr, env))
        payload = self.evaluate(node.payload_expr, env)
        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise RuntimeError_(f"Line {node.line}: HTTP POST failed for '{url}'. ({e})")

    def _exec_class_def(self, node: ClassDef, env: Environment):
        self.classes[node.name] = node
        if node.name not in self.methods:
            self.methods[node.name] = {}

    def _exec_method_def(self, node: MethodDef, env: Environment):
        if node.class_name not in self.methods:
            self.methods[node.class_name] = {}
        self.methods[node.class_name][node.name] = node

    def _exec_set_property(self, node: SetPropertyStmt, env: Environment):
        obj = self.evaluate(node.obj_expr, env)
        val = self.evaluate(node.value_expr, env)
        if isinstance(obj, Instance):
            obj.properties[node.prop_name] = val
        elif isinstance(obj, dict):
            obj[node.prop_name] = val
        else:
            raise RuntimeError_(f"Line {node.line}: Can only set properties on objects or dictionaries.")

    def _call_method(self, obj: Any, method_name: str, arg_vals: List[Any], env: Environment, line: int) -> Any:
        if isinstance(obj, Environment):
            # Treat the environment like a giant closure (a module)
            try:
                fn = obj.get(method_name, line)
            except RuntimeError_:
                raise RuntimeError_(f"Line {line}: Function '{method_name}' not found in namespace.")
            
            # A. Native Python callables (e.g. from the `gui` standard library)
            if callable(fn) and not hasattr(fn, "params") and not hasattr(fn, "node"):
                try:
                    return fn(*arg_vals)
                except Exception as e:
                    raise RuntimeError_(f"Line {line}: Error calling '{method_name}': {e}")
                    
            # B. prose FunctionDef or Closure — route through _call_function
            if hasattr(fn, "params") or hasattr(fn, "node"):
                return self._call_function(method_name, [LiteralNode(v) for v in arg_vals], env, line)
                
            raise RuntimeError_(f"Line {line}: Export '{method_name}' is not callable.")
                 
        if not isinstance(obj, Instance):
            raise RuntimeError_(f"Line {line}: Can only call methods on objects or modules (got {type(obj).__name__}).")
        
        # Check if the method is a native callable stored directly in properties (e.g. from gui stdlib)
        if method_name in obj.properties:
            fn = obj.properties[method_name]
            if callable(fn) and not hasattr(fn, "params") and not hasattr(fn, "node"):
                try:
                    return fn(*arg_vals)
                except Exception as e:
                    raise RuntimeError_(f"Line {line}: Error calling method '{method_name}': {e}")

        # Walk inheritance chain to find the method
        class_name = obj.class_name
        method_def = None
        search_class = class_name
        while search_class:
            if search_class in self.methods and method_name in self.methods[search_class]:
                method_def = self.methods[search_class][method_name]
                break
            # Walk up inheritance chain
            if search_class in self.classes and self.classes[search_class].parent:
                search_class = self.classes[search_class].parent
            else:
                break
        
        if method_def is None:
            raise RuntimeError_(f"Line {line}: Method '{method_name}' not found for class '{class_name}'.")
            
        min_args = sum(1 for p in method_def.params if p.default_expr is None)
        if len(arg_vals) < min_args or len(arg_vals) > len(method_def.params):
             err_msg = f"{len(method_def.params)}" if min_args == len(method_def.params) else f"between {min_args} and {len(method_def.params)}"
             raise RuntimeError_(f"Line {line}: Method '{method_name}' expects {err_msg} parameters but got {len(arg_vals)}.")
        
        method_env = Environment(self.global_env)
        method_env.set_local("self", obj)
        for prop, val in obj.properties.items():
            method_env.set_local(prop, val)
        
        for i, param in enumerate(method_def.params):
            if i < len(arg_vals):
                method_env.set_local(param.name, arg_vals[i])
            else:
                val = self.evaluate(param.default_expr, self.global_env)
                method_env.set_local(param.name, val)
            
        # --- Asynchronous execution block ---
        if getattr(method_def, "is_async", False):
            class AsyncMethodThread(threading.Thread):
                def __init__(self, interp, bdy, en):
                    super().__init__()
                    self.interp = interp
                    self.bdy = bdy
                    self.en = en
                    self.thread_result = None
                    self.thread_error = None
                def run(self):
                    try:
                        self.interp.execute(self.bdy, self.en)
                    except ReturnException as ret:
                        self.thread_result = ret.value
                    except Exception as e:
                        self.thread_error = e

            t = AsyncMethodThread(self, method_def.body, method_env)
            t.start()
            return t
            
        # --- Synchronous execution block ---
        try:
            self.execute(method_def.body, method_env)
            ret_val = None
        except ReturnException as e:
            ret_val = e.value
        except RuntimeError_ as e:
            if not hasattr(e, 'plain_stack'):
                e.plain_stack = []
            e.plain_stack.append(f"method '{method_name}' on class '{class_name}' at line {line}")
            raise
                
        return ret_val

    def _eval_new_instance(self, node: NewInstanceExpr, env: Environment) -> Instance:
        if node.class_name not in self.classes:
            raise RuntimeError_(f"Line {node.line}: Class '{node.class_name}' not found.")
        class_def = self.classes[node.class_name]
        
        # Merge properties from parent chain
        all_props = []
        current = class_def
        while current is not None:
            all_props = list(current.properties) + all_props
            if current.parent:
                if current.parent not in self.classes:
                    raise RuntimeError_(f"Line {node.line}: Parent class '{current.parent}' not found.")
                current = self.classes[current.parent]
            else:
                current = None
        
        props = {p: None for p in all_props}
        for key_expr, val_expr in node.args:
            k = self.evaluate(key_expr, env)
            v = self.evaluate(val_expr, env)
            props[str(k)] = v
            
        return Instance(class_def, props)

    def _eval_property_access(self, node: PropertyAccessExpr, env: Environment) -> Any:
        obj = self.evaluate(node.obj_expr, env)
        if isinstance(obj, Instance):
            if node.prop_name not in obj.properties:
                 raise RuntimeError_(f"Line {node.line}: Property '{node.prop_name}' not found on object of class '{obj.class_name}'.")
            return obj.properties[node.prop_name]
        elif isinstance(obj, dict):
            if node.prop_name not in obj:
                 raise RuntimeError_(f"Line {node.line}: Key '{node.prop_name}' not found in dictionary.")
            return obj[node.prop_name]
        elif isinstance(obj, Environment):
            try:
                return obj.get(node.prop_name, node.line)
            except RuntimeError_:
                raise RuntimeError_(f"Line {node.line}: Export '{node.prop_name}' not found in namespace.")
        else:
             raise RuntimeError_(f"Line {node.line}: Can only access properties on objects, modules or dictionaries (got {type(obj).__name__}).")

    # ── Phase 6 Evaluation Methods ─────────────────────────────────────────────

    def _eval_interpolated_string(self, node, env: Environment) -> str:
        parts = []
        for part in node.parts:
            parts.append(self._to_display(self.evaluate(part, env)))
        return "".join(parts)

    def _exec_check(self, node, env: Environment):
        val = self.evaluate(node.expr, env)
        for case_val_expr, body in node.cases:
            case_val = self.evaluate(case_val_expr, env)
            if self._loose_eq(val, case_val):
                self.execute(body, env)
                return
        if node.otherwise:
            self.execute(node.otherwise, env)

    def _exec_enum_def(self, node, env: Environment):
        self.enums[node.name] = node

    def _exec_test_block(self, node, env: Environment):
        self.tests.append(node)

    def _exec_assert(self, node, env: Environment):
        result = self.evaluate_condition(node.condition, env)
        if not result:
            raise RuntimeError_(f"Line {node.line}: Assertion failed.")

    def _exec_run_tests(self, node, env: Environment):
        passed = 0
        failed = 0
        print(f"\n{'='*50}")
        print(f"  Running {len(self.tests)} test(s)...")
        print(f"{'='*50}\n")
        for test in self.tests:
            try:
                test_env = Environment(parent=self.global_env)
                self.execute(test.body, test_env)
                print(f"  ✓ {test.name}")
                passed += 1
            except (RuntimeError_, Exception) as e:
                print(f"  ✗ {test.name}")
                print(f"    → {e}")
                failed += 1
        print(f"\n{'='*50}")
        print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
        print(f"{'='*50}\n")

    def _eval_map(self, node, env: Environment) -> list:
        func = self.evaluate(node.func_expr, env)
        lst = self.evaluate(node.list_expr, env)
        if not isinstance(lst, list):
            raise RuntimeError_(f"Line {node.line}: 'mapping' requires a list.")
        result = []
        for item in lst:
            result.append(self._apply_lambda_or_func(func, [item], env, node.line))
        return result

    def _eval_filter(self, node, env: Environment) -> list:
        lst = self.evaluate(node.list_expr, env)
        if not isinstance(lst, list):
            raise RuntimeError_(f"Line {node.line}: 'filtering' requires a list.")
        result = []
        for item in lst:
            filter_env = Environment(parent=env)
            filter_env.set_local(node.var_name, item)
            if self.evaluate_condition(node.condition, filter_env):
                result.append(item)
        return result

    def _eval_regex_match(self, node, env: Environment) -> Any:
        pattern = str(self.evaluate(node.pattern_expr, env))
        text = str(self.evaluate(node.text_expr, env))
        try:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if groups:
                    return list(groups)
                return match.group(0)
            return None
        except re.error as e:
            raise RuntimeError_(f"Line {node.line}: Invalid regex pattern. ({e})")

    def _eval_regex_test(self, node, env: Environment) -> bool:
        pattern = str(self.evaluate(node.pattern_expr, env))
        text = str(self.evaluate(node.text_expr, env))
        try:
            return bool(re.search(pattern, text))
        except re.error as e:
            raise RuntimeError_(f"Line {node.line}: Invalid regex pattern. ({e})")

    def _apply_lambda_or_func(self, func, args: list, env: Environment, line: int) -> Any:
        """Apply a lambda or named function to a list of argument values."""
        # 1. Closure (captures environment)
        if hasattr(func, "node") and hasattr(func.node, "params"):
            if len(args) != len(func.node.params):
                raise RuntimeError_(f"Line {line}: Lambda expects {len(func.node.params)} argument(s) but got {len(args)}.")
            lambda_env = Environment(parent=func.env)
            for param, val in zip(func.node.params, args):
                lambda_env.set_local(param, val)
            return self.evaluate(func.node.body_expr, lambda_env)
        
        # 2. Named function (string identifier)
        elif isinstance(func, str):
            # Named function
            if func not in self.functions:
                raise RuntimeError_(f"Line {line}: Function '{func}' not found.")
            f = self.functions[func]
            
            # Support native Python functions from standard libraries
            if callable(f) and not hasattr(f, "params"):
                try:
                    return f(*args)
                except Exception as e:
                    raise RuntimeError_(f"Line {line}: Native function '{func}' failed when applying: {e}")
                    
            if len(args) != len(f.params):
                raise RuntimeError_(f"Line {line}: '{func}' needs {len(f.params)} argument(s) but got {len(args)}.")
                
            func_env = Environment(parent=self.global_env)
            for param, val in zip(f.params, args):
                func_env.set_local(param, val)
            try:
                self.execute(f.body, func_env)
            except ReturnException as e:
                return e.value
            return None
        else:
            raise RuntimeError_(f"Line {line}: Expected a function or lambda for mapping/filtering.")

    def _eval_string_index(self, node: StringIndexExpr, env: Environment) -> str:
        s = str(self.evaluate(node.str_expr, env))
        idx = int(self.evaluate(node.index_expr, env)) - 1
        if idx < 0 or idx >= len(s):
            raise RuntimeError_(f"Line {node.line}: Character index {idx+1} out of bounds for text of length {len(s)}.")
        return s[idx]
        
    def _eval_string_slice(self, node: StringSliceExpr, env: Environment) -> str:
        s = str(self.evaluate(node.str_expr, env))
        start = int(self.evaluate(node.start_expr, env)) - 1
        end = int(self.evaluate(node.end_expr, env))
        if start < 0: start = 0
        if end > len(s): end = len(s)
        if start >= end: return ""
        return s[start:end]

    # ── Function calls ────────────────────────────────────────────────────────

    def _call_function(self, name: str, arg_nodes: List[Any], env: Environment, line: int) -> Any:
        func = None
        
        # 1. Check if name is a variable holding a function/closure
        try:
            val = env.get(name, line)
            if hasattr(val, "node") or callable(val) or hasattr(val, "params"):
                func = val
        except RuntimeError_:
            pass
            
        # 2. Fallback to global functions
        if func is None and name in self.functions:
            func = self.functions[name]
            
        if func is None:
            raise RuntimeError_(f"Line {line}: I could not find a function called '{name}'.")
            
        arg_vals = [self.evaluate(a, env) for a in arg_nodes]
        
        # A. Native Python functions
        if callable(func) and not hasattr(func, "params") and not hasattr(func, "node"):
            try:
                return func(*arg_vals)
            except Exception as e:
                raise RuntimeError_(f"Line {line}: Native function '{name}' failed: {e}")
                
        # B. Closure or FunctionDef
        node = func.node if hasattr(func, "node") else func
        parent_env = func.env if hasattr(func, "env") else self.global_env
        
        min_args = sum(1 for p in node.params if p.default_expr is None)
        if len(arg_vals) < min_args or len(arg_vals) > len(node.params):
            err_msg = f"{len(node.params)}" if min_args == len(node.params) else f"between {min_args} and {len(node.params)}"
            raise RuntimeError_(
                f"Line {line}: '{name}' needs {err_msg} argument(s), "
                f"but I was given {len(arg_vals)}."
            )
            
        func_env = Environment(parent=parent_env)
        for i, param in enumerate(node.params):
            if i < len(arg_vals):
                func_env.set_local(param.name, arg_vals[i])
            else:
                val = self.evaluate(param.default_expr, parent_env)
                func_env.set_local(param.name, val)
            
        body = node.body_expr if hasattr(node, "body_expr") else node.body
        
        # --- Asynchronous execution block ---
        if getattr(node, "is_async", False):
            class AsyncThread(threading.Thread):
                def __init__(self, interp, bdy, en):
                    super().__init__()
                    self.interp = interp
                    self.bdy = bdy
                    self.en = en
                    self.thread_result = None
                    self.thread_error = None
                def run(self):
                    try:
                        if hasattr(node, "body_expr"):
                            self.thread_result = self.interp.evaluate(self.bdy, self.en)
                        else:
                            self.interp.execute(self.bdy, self.en)
                    except ReturnException as ret:
                        self.thread_result = ret.value
                    except Exception as e:
                        self.thread_error = e

            t = AsyncThread(self, body, func_env)
            t.start()
            return t
            
        # --- Synchronous execution block ---
        try:
            if hasattr(node, "body_expr"): 
                # Lambdas return their body expression directly
                return self.evaluate(body, func_env)
            else:
                self.execute(body, func_env)
                return None
        except ReturnException as ret:
            return ret.value
        except RuntimeError_ as e:
            if not hasattr(e, 'plain_stack'):
                e.plain_stack = []
            fn_name = getattr(node, "name", name)
            e.plain_stack.append(f"function '{fn_name}' at line {line}")
            raise

    # ── Evaluate expressions ──────────────────────────────────────────────────

    def evaluate(self, node: Any, env: Environment) -> Any:
        t = type(node)

        if t is NumberLiteral:
            v = node.value
            return int(v) if v == int(v) else v
        if t is LiteralNode:    return node.value
        if t is StringLiteral:  return node.value
        if t is BoolLiteral:    return node.value
        if t is NoneLiteral:    return None

        if t is Identifier:
            try:   
                return env.get(node.name, node.line)
            except RuntimeError_: 
                if node.name in self.functions:
                    func_def = self.functions[node.name]
                    # If it's already a python callable, return it
                    if callable(func_def) and not hasattr(func_def, "params") and not hasattr(func_def, "node"):
                        return func_def
                    # Otherwise, wrap the FunctionDef in a Closure attached to global env
                    return Closure(func_def, self.global_env)
                return node.name

        if t is UnaryMinus:
            val = self.evaluate(node.operand, env)
            if not isinstance(val, (int, float)):
                raise RuntimeError_(f"Line {node.line}: Cannot negate '{val}'.")
            return -val

        if t is BinOp:
            return self._apply_op(node.op,
                                  self.evaluate(node.left, env),
                                  self.evaluate(node.right, env),
                                  node.line)

        if t is ListLiteral:
            return [self.evaluate(e, env) for e in node.elements]

        if t is ListAccess:
            lst = self.evaluate(node.list_expr, env)
            idx = int(self.evaluate(node.index_expr, env)) - 1
            if not isinstance(lst, list):
                raise RuntimeError_(f"Line {node.line}: Can only index into a list.")
            if idx < 0 or idx >= len(lst):
                raise RuntimeError_(f"Line {node.line}: Index {idx+1} out of range (list has {len(lst)} items).")
            return lst[idx]

        if t is DictLiteral:
            d = {}
            for key_expr, val_expr in node.pairs:
                k = self.evaluate(key_expr, env)
                v = self.evaluate(val_expr, env)
                if isinstance(k, (list, dict)):
                    raise RuntimeError_(f"Line {node.line}: A list or dictionary cannot be used as a key.")
                d[k] = v
            return d

        if t is DictAccess:
            d = self.evaluate(node.dict_expr, env)
            if not isinstance(d, dict):
                raise RuntimeError_(f"Line {node.line}: Can only get a value from a dictionary.")
            k = self.evaluate(node.key_expr, env)
            if k not in d:
                raise RuntimeError_(f"Line {node.line}: The dictionary does not have the key '{k}'.")
            return d[k]

        if t is DictKeys:
            d = self.evaluate(node.dict_expr, env)
            if not isinstance(d, dict):
                raise RuntimeError_(f"Line {node.line}: Can only get keys from a dictionary.")
            return list(d.keys())

        if t is FileContents:
            filepath = str(self.evaluate(node.file_expr, env))
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError_(f"Line {node.line}: Could not read file '{filepath}'. ({e})")

        if t is TimeOp:
            now = datetime.datetime.now()
            if node.op_type == "datetime":
                return now.isoformat()
            if node.op_type == "year":
                return now.year
            if node.op_type == "timestamp":
                return int(now.timestamp())

        if t is LengthOf:
            val = self.evaluate(node.expr, env)
            if isinstance(val, (list, str)): return len(val)
            raise RuntimeError_(f"Line {node.line}: Can only get length of a list or text.")

        if t is UppercaseOf:
            return str(self.evaluate(node.expr, env)).upper()

        if t is LowercaseOf:
            return str(self.evaluate(node.expr, env)).lower()

        # ── Phase 3 string nodes ───────────────────────────────────────────────

        if t is TrimOf:
            return str(self.evaluate(node.expr, env)).strip()

        if t is SplitBy:
            src = str(self.evaluate(node.source, env))
            delim = str(self.evaluate(node.delimiter, env))
            return src.split(delim)

        if t is JoinWith:
            lst = self.evaluate(node.list_expr, env)
            sep = str(self.evaluate(node.separator, env))
            if not isinstance(lst, list):
                raise RuntimeError_(f"Line {node.line}: 'join' needs a list.")
            return sep.join(self._to_display(v) for v in lst)

        if t is ReplaceIn:
            src  = str(self.evaluate(node.source, env))
            find = str(self.evaluate(node.find, env))
            repl = str(self.evaluate(node.replacement, env))
            return src.replace(find, repl)

        if t is RepeatStr:
            s = str(self.evaluate(node.expr, env))
            n = int(self.evaluate(node.count, env))
            return s * n

        if t is ContainsExpr:
            hay  = self.evaluate(node.haystack, env)
            nail = self.evaluate(node.needle, env)
            if isinstance(hay, str):
                return str(nail) in hay
            if isinstance(hay, list):
                return nail in hay
            raise RuntimeError_(f"Line {node.line}: 'contains' needs a list or text.")

        if t is ListContainsExpr:
            lst  = self.evaluate(node.list_expr, env)
            item = self.evaluate(node.item, env)
            if not isinstance(lst, list):
                raise RuntimeError_(f"Line {node.line}: 'contains' needs a list.")
            return item in lst

        if t is IndexOf:
            item = self.evaluate(node.item, env)
            lst  = self.evaluate(node.list_expr, env)
            if isinstance(lst, list):
                try:   return lst.index(item) + 1   # 1-based
                except ValueError: return 0
            if isinstance(lst, str):
                idx = lst.find(str(item))
                return idx + 1 if idx >= 0 else 0
            raise RuntimeError_(f"Line {node.line}: 'index of' needs a list or text.")

        # ── Phase 5 Web nodes (JSON & HTTP) ────────────────────────────────────

        if t is JsonParseExpr:
            text = self.evaluate(node.text_expr, env)
            if not isinstance(text, str):
                raise RuntimeError_(f"Line {node.line}: JSON parsing requires text.")
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                raise RuntimeError_(f"Line {node.line}: Invalid JSON text format. {str(e)}")

        if t is JsonStringifyExpr:
            data = self.evaluate(node.dict_expr, env)
            try:
                return json.dumps(data)
            except TypeError as e:
                raise RuntimeError_(f"Line {node.line}: Could not convert to JSON. {str(e)}")

        if t is HttpGetExpr:
            url = self.evaluate(node.url_expr, env)
            if not isinstance(url, str):
                raise RuntimeError_(f"Line {node.line}: URL must be text.")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    body = response.read().decode('utf-8')
                    # Automatically parse JSON if possible, else return string
                    try: return json.loads(body)
                    except json.JSONDecodeError: return body
            except urllib.error.URLError as e:
                raise RuntimeError_(f"Line {node.line}: Network error fetching URL. {str(e)}")

        if t is HttpPostExpr:
            url = self.evaluate(node.url_expr, env)
            payload = self.evaluate(node.payload_expr, env)
            if not isinstance(url, str):
                raise RuntimeError_(f"Line {node.line}: URL must be text.")
            try:
                data_bytes = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data_bytes, headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Content-Type': 'application/json'
                }, method='POST')
                with urllib.request.urlopen(req) as response:
                    body = response.read().decode('utf-8')
                    try: return json.loads(body)
                    except json.JSONDecodeError: return body
            except urllib.error.URLError as e:
                raise RuntimeError_(f"Line {node.line}: Network error posting to URL. {str(e)}")
            except TypeError as e:
                raise RuntimeError_(f"Line {node.line}: Could not convert payload to JSON. {str(e)}")

        # ── Phase 3 math nodes ─────────────────────────────────────────────────

        if t is RoundOf:
            val = self.evaluate(node.expr, env)
            self._assert_num(val, "round", node.line)
            if node.places is None:
                r = round(float(val))
                return r
            places = int(self.evaluate(node.places, env))
            r2 = round(float(val), places)
            return int(r2) if places <= 0 else r2

        if t is AbsOf:
            val = self.evaluate(node.expr, env)
            self._assert_num(val, "absolute value", node.line)
            r = abs(float(val))
            return int(r) if r == int(r) else r

        if t is SqrtOf:
            val = self.evaluate(node.expr, env)
            self._assert_num(val, "square root", node.line)
            if float(val) < 0:
                raise RuntimeError_(f"Line {node.line}: I cannot take the square root of a negative number.")
            r = math.sqrt(float(val))
            return int(r) if r == int(r) else r

        if t is FloorOf:
            val = self.evaluate(node.expr, env)
            self._assert_num(val, "floor", node.line)
            return math.floor(float(val))

        if t is CeilingOf:
            val = self.evaluate(node.expr, env)
            self._assert_num(val, "ceiling", node.line)
            return math.ceil(float(val))

        if t is RandomBetween:
            lo = self.evaluate(node.low, env)
            hi = self.evaluate(node.high, env)
            self._assert_num(lo, "random", node.line)
            self._assert_num(hi, "random", node.line)
            if isinstance(lo, int) and isinstance(hi, int):
                return random.randint(int(lo), int(hi))
            return round(random.uniform(float(lo), float(hi)), 6)

        if t is MinOf:
            a = self.evaluate(node.left, env)
            b = self.evaluate(node.right, env)
            self._assert_num(a, "minimum", node.line)
            self._assert_num(b, "minimum", node.line)
            r = min(float(a), float(b))
            return int(r) if r == int(r) else r

        if t is MaxOf:
            a = self.evaluate(node.left, env)
            b = self.evaluate(node.right, env)
            self._assert_num(a, "maximum", node.line)
            self._assert_num(b, "maximum", node.line)
            r = max(float(a), float(b))
            return int(r) if r == int(r) else r

        if t is PowerOf:
            base = self.evaluate(node.base, env)
            exp  = self.evaluate(node.exp, env)
            self._assert_num(base, "power", node.line)
            self._assert_num(exp,  "power", node.line)
            r = float(base) ** float(exp)
            return int(r) if r == int(r) else r

        # ── Phase 3 conversion nodes ───────────────────────────────────────────

        if t is AsNumber:
            val = self.evaluate(node.expr, env)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return val
            try:
                v = float(str(val))
                return int(v) if v == int(v) else v
            except (ValueError, TypeError):
                raise RuntimeError_(
                    f"Line {node.line}: I could not convert '{val}' to a number. "
                    f"Please make sure it looks like a number."
                )

        if t is AsText:
            val = self.evaluate(node.expr, env)
            return self._to_display(val)

        # Phase 5
        if t is JsonParseExpr:      return self._eval_json_parse(node, env)
        if t is JsonStringifyExpr:  return self._eval_json_stringify(node, env)
        if t is HttpGetExpr:        return self._eval_http_get(node, env)
        if t is HttpPostExpr:       return self._eval_http_post(node, env)
        if t is NewInstanceExpr:    return self._eval_new_instance(node, env)
        if t is PropertyAccessExpr: return self._eval_property_access(node, env)

        # Phase 6 & 7
        if t is InterpolatedString: return self._eval_interpolated_string(node, env)
        if t is LambdaExpr:         return Closure(node, env)
        if t is BlockLambda:         return Closure(node, env)  # Multi-line inline closure capturing current env
        # Phase B — Inline filtering
        if t is AllWhereExpr:
            source = self.evaluate(node.source_expr, env)
            if not isinstance(source, list):
                raise RuntimeError_(f"Line {node.line}: 'all ... where' can only filter a list.")
            result = []
            for item in source:
                filter_env = Environment(parent=env)
                filter_env.set_local(node.var_name, item)
                # Use evaluate_condition for Condition nodes, evaluate for bool expressions
                cond_node = node.condition
                if type(cond_node).__name__ in ("Condition", "CompoundCondition", "FileExists"):
                    passed = self.evaluate_condition(cond_node, filter_env)
                else:
                    passed = self.evaluate(cond_node, filter_env)
                if passed:
                    result.append(item)
            return result
        if t is MapExpr:            return self._eval_map(node, env)
        if t is FilterExpr:         return self._eval_filter(node, env)
        if t is CliArgsExpr:        return sys.argv[2:] if len(sys.argv) > 2 else []
        if t is EnvVarExpr:         return os.environ.get(str(self.evaluate(node.name_expr, env)), None)
        if t is RegexMatchExpr:     return self._eval_regex_match(node, env)
        if t is RegexTestExpr:      return self._eval_regex_test(node, env)
        if t is StringIndexExpr:    return self._eval_string_index(node, env)
        if t is StringSliceExpr:    return self._eval_string_slice(node, env)

        if t is WaitExpr:
            future = self.evaluate(node.expr, env)
            if hasattr(future, "result"): # Supports concurrent.futures.Future
                try:
                    return future.result()
                except Exception as e:
                    raise RuntimeError_(f"Line {node.line}: Background task failed: {e}")
            elif hasattr(future, "join"): # Supports standard threading.Thread if overridden to return value
                future.join()
                if hasattr(future, "thread_error") and future.thread_error is not None:
                    raise future.thread_error
                try:
                    return future.thread_result
                except AttributeError:
                    return None
            else:
                raise RuntimeError_(f"Line {node.line}: Cannot 'waiting for' something that is not an active background task.")

        raise RuntimeError_(f"I do not know how to evaluate: {type(node).__name__}.")

    # ── Operators ─────────────────────────────────────────────────────────────

    def _apply_op(self, op: str, left: Any, right: Any, line: int) -> Any:
        if op == "plus":
            if isinstance(left, list) and isinstance(right, list): return left + right
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + " " + str(right)
            return left + right
        if op == "minus":
            self._assert_num(left, op, line); self._assert_num(right, op, line)
            return self._clean(left - right)
        if op == "times":
            self._assert_num(left, op, line); self._assert_num(right, op, line)
            return self._clean(left * right)
        if op == "divided_by":
            self._assert_num(left, op, line); self._assert_num(right, op, line)
            if right == 0: raise RuntimeError_(f"Line {line}: I cannot divide by zero.")
            return self._clean(left / right)
        if op == "modulo":
            self._assert_num(left, op, line); self._assert_num(right, op, line)
            if right == 0: raise RuntimeError_(f"Line {line}: I cannot take the remainder of dividing by zero.")
            return self._clean(left % right)
        raise RuntimeError_(f"Line {line}: Unknown operator '{op}'.")

    def _clean(self, v: Any) -> Any:
        """Return int if whole number, else float."""
        if isinstance(v, float) and v == int(v): return int(v)
        return v

    def _assert_num(self, val: Any, op: str, line: int):
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise RuntimeError_(f"Line {line}: '{val}' is not a number, so I cannot use '{op}'.")

    # ── Conditions ────────────────────────────────────────────────────────────

    def evaluate_condition(self, node: Any, env: Environment) -> bool:
        if type(node) is CompoundCondition:
            left = self.evaluate_condition(node.left, env)
            if node.connective == "and":
                return left and self.evaluate_condition(node.right, env)
            return left or self.evaluate_condition(node.right, env)

        if type(node) is FileExists:
            filepath = str(self.evaluate(node.file_expr, env))
            return os.path.exists(filepath)

        left = self.evaluate(node.left, env)
        op   = node.op
        line = node.line

        if op == "is_number":  return isinstance(left, (int, float)) and not isinstance(left, bool)
        if op == "is_text":    return isinstance(left, str)
        if op == "is_list":    return isinstance(left, list)
        if op == "is_boolean": return isinstance(left, bool)

        right = self.evaluate(node.right, env)

        if op == "equals":      return self._loose_eq(left, right)
        if op == "not_equals":  return not self._loose_eq(left, right)
        
        if op == "has_key":
            if not isinstance(left, dict):
                raise RuntimeError_(f"Line {line}: 'has the key' can only be used on a dictionary.")
            return right in left

        ln = self._to_num(left, line)
        rn = self._to_num(right, line)
        if op == "greater_than":  return ln > rn
        if op == "less_than":     return ln < rn
        if op == "greater_equal": return ln >= rn
        if op == "less_equal":    return ln <= rn
        raise RuntimeError_(f"Line {line}: Unknown comparison '{op}'.")

    def _loose_eq(self, a: Any, b: Any) -> bool:
        if type(a) == type(b): return a == b
        try: return float(a) == float(b)
        except: return str(a).lower() == str(b).lower()

    def _to_num(self, val: Any, line: int) -> float:
        if isinstance(val, (int, float)) and not isinstance(val, bool): return float(val)
        try: return float(val)
        except: raise RuntimeError_(f"Line {line}: '{val}' is not a number — I need one for this comparison.")

    # ── Display helpers ───────────────────────────────────────────────────────

    def _to_display(self, value: Any) -> str:
        if value is None:           return "nothing"
        if isinstance(value, bool): return "true" if value else "false"
        if isinstance(value, list): return "[" + ", ".join(self._to_display(v) for v in value) + "]"
        if isinstance(value, dict):
            pairs = []
            for k, v in value.items():
                pairs.append(f"{self._to_display(k)}: {self._to_display(v)}")
            return "{" + ", ".join(pairs) + "}"
        if isinstance(value, float) and value == int(value): return str(int(value))
        return str(value)
