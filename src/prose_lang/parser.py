"""
prose Language Parser — Phase 2
Recursive-descent parser producing an AST.

New in Phase 2:
  - Compound conditions with 'and' / 'or'
  - Modulo operator (modulo keyword or %)
  - Negative number literals
  - List literals: a list containing 1, 2, 3
  - List access: item N of myList
  - List add: Add X to myList
  - List remove: Remove item N from myList
  - For-each loop: For each X in myList do the following.
  - String operations: the length of X, uppercase of X, lowercase of X
  - Type checking: X is a number / text / list / boolean
  - Comments: Note: ... (stripped at lexer level)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any

from .lexer import (
    Token, WORD, NUMBER, COMMA, PERIOD, COLON, STRING_QUOTED, INTERP_STRING, EOF,
    PLUS, MINUS, STAR, SLASH, PERCENT, LBRACE, RBRACE,
    EQ, NEQ, LT, GT, LTE, GTE,
)


# ─── AST Nodes ─────────────────────────────────────────────────────────────────

@dataclass
class NumberLiteral:
    value: float
    line: int = 0

@dataclass
class StringLiteral:
    value: str
    line: int = 0

@dataclass
class BoolLiteral:
    value: bool
    line: int = 0

@dataclass
class NoneLiteral:
    line: int = 0

@dataclass
class LiteralNode:
    value: Any
    line: int = 0

@dataclass
class Identifier:
    name: str
    line: int = 0

@dataclass
class BinOp:
    left: Any
    op: str    # plus, minus, times, divided_by, modulo
    right: Any
    line: int = 0

@dataclass
class UnaryMinus:
    operand: Any
    line: int = 0

# Compound condition: left (and|or) right
@dataclass
class CompoundCondition:
    left: Any        # Condition or CompoundCondition
    connective: str  # "and" | "or"
    right: Any
    line: int = 0

@dataclass
class Condition:
    left: Any
    op: str   # greater_than, less_than, equals, not_equals, greater_equal, less_equal,
              # is_number, is_text, is_list, is_boolean
    right: Any  # None for type-check ops
    line: int = 0

@dataclass
class ListLiteral:
    elements: List[Any]
    line: int = 0

@dataclass
class ListAccess:
    list_expr: Any
    index_expr: Any   # 1-based
    line: int = 0

@dataclass
class LengthOf:
    expr: Any
    line: int = 0

@dataclass
class UppercaseOf:
    expr: Any
    line: int = 0

@dataclass
class LowercaseOf:
    expr: Any
    line: int = 0

@dataclass
class ContainsExpr:
    """X contains Y → bool"""
    haystack: Any
    needle: Any
    line: int = 0

@dataclass
class JoinWith:
    list_expr: Any
    separator: Any
    line: int = 0

@dataclass
class TypeCheck:
    expr: Any
    expected: str
    line: int = 0

# ── Phase 3 string nodes ────────────────────────────────────────────────────────

@dataclass
class ReplaceIn:
    """replace Y in X with Z"""
    source: Any   # the string to operate on
    find: Any     # what to find
    replacement: Any
    line: int = 0

@dataclass
class SplitBy:
    """split X by Y → list"""
    source: Any
    delimiter: Any
    line: int = 0

@dataclass
class TrimOf:
    """trim X → removes leading/trailing whitespace"""
    expr: Any
    line: int = 0

@dataclass
class RepeatStr:
    """repeat X N times → string"""
    expr: Any
    count: Any
    line: int = 0

@dataclass
class ListContainsExpr:
    """myList contains X → bool"""
    list_expr: Any
    item: Any
    line: int = 0

@dataclass
class SortList:
    """sort myList (in place)"""
    list_name: str
    line: int = 0

@dataclass
class IndexOf:
    """index of X in myList → number (1-based, 0 if not found)"""
    item: Any
    list_expr: Any
    line: int = 0

# ── Phase 3 math nodes ──────────────────────────────────────────────────────────

@dataclass
class RoundOf:
    expr: Any
    places: Any   # None = round to integer
    line: int = 0

@dataclass
class AbsOf:
    expr: Any
    line: int = 0

@dataclass
class RandomBetween:
    low: Any
    high: Any
    line: int = 0

@dataclass
class MinOf:
    left: Any
    right: Any
    line: int = 0

@dataclass
class MaxOf:
    left: Any
    right: Any
    line: int = 0

@dataclass
class SqrtOf:
    expr: Any
    line: int = 0

@dataclass
class FloorOf:
    expr: Any
    line: int = 0

@dataclass
class CeilingOf:
    expr: Any
    line: int = 0

@dataclass
class PowerOf:
    base: Any
    exp: Any
    line: int = 0

# ── Phase 3 conversion nodes ────────────────────────────────────────────────────

@dataclass
class AsNumber:
    expr: Any
    line: int = 0

@dataclass
class AsText:
    expr: Any
    line: int = 0

# ── Phase 3 error handling ──────────────────────────────────────────────────────

@dataclass
class TryCatch:
    try_body: List[Any]
    error_var: str          # variable name that gets the error message
    catch_body: List[Any]
    line: int = 0

# ── Phase 4 Dictionary nodes ───────────────────────────────────────────────────

@dataclass
class DictLiteral:
    pairs: List[tuple[Any, Any]]
    line: int = 0

@dataclass
class DictAccess:
    dict_expr: Any
    key_expr: Any
    line: int = 0

@dataclass
class DictHasKey:
    dict_expr: Any
    key_expr: Any
    line: int = 0

@dataclass
class DictKeys:
    dict_expr: Any
    line: int = 0

@dataclass
class SetDictValueStmt:
    dict_expr: Any
    key_expr: Any
    value_expr: Any
    line: int = 0

@dataclass
class RemoveDictValueStmt:
    dict_expr: Any
    key_expr: Any
    line: int = 0

# ── Phase 4 File I/O & Module nodes ───────────────────────────────────────────

@dataclass
class FileContents:
    file_expr: Any
    line: int = 0

@dataclass
class FileExists:
    file_expr: Any
    line: int = 0

@dataclass
class WriteFileStmt:
    content_expr: Any
    file_expr: Any
    line: int = 0

@dataclass
class AppendFileStmt:
    content_expr: Any
    file_expr: Any
    line: int = 0

@dataclass
class ImportStmt:
    file_expr: Any
    alias: Optional[str] = None
    specific_imports: Optional[List[str]] = None
    line: int = 0

@dataclass
class ThrowStmt:
    msg_expr: Any
    line: int = 0

# ── Phase 5 ────────────────────────────────────────────────────────────────
@dataclass
class JsonParseExpr:
    text_expr: Any
    line: int = 0

@dataclass
class JsonStringifyExpr:
    dict_expr: Any
    line: int = 0

@dataclass
class ParamDef:
    name: str
    default_expr: Optional[Any] = None

@dataclass
class HttpGetExpr:
    url_expr: Any
    line: int = 0

@dataclass
class HttpPostExpr:
    url_expr: Any
    payload_expr: Any
    line: int = 0

@dataclass
class ClassDef:
    name: str
    properties: List[str]
    parent: Optional[str] = None
    line: int = 0

@dataclass
class MethodDef:
    class_name: str
    name: str
    params: List[ParamDef]
    body: List[Any]
    line: int = 0

@dataclass
class NewInstanceExpr:
    class_name: str
    args: List[tuple[str, Any]]  # (prop_name, expr)
    line: int = 0

@dataclass
class PropertyAccessExpr:
    obj_expr: Any
    prop_name: str
    line: int = 0

@dataclass
class SetPropertyStmt:
    obj_expr: Any
    prop_name: str
    value_expr: Any
    line: int = 0

@dataclass
class MethodCallStmt:
    obj_expr: Any
    method_name: str
    args: List[Any]
    line: int = 0
    line: int = 0

@dataclass
class TimeOp:
    op_type: str  # "datetime", "year", "timestamp"
    line: int = 0

# ── Phase 6 ────────────────────────────────────────────────────────────────────────
@dataclass
class InterpolatedString:
    parts: List[Any]  # list of StringLiteral and expression nodes
    line: int = 0

@dataclass
class CheckStmt:
    expr: Any
    cases: List[tuple]  # [(value_expr, body_stmts), ...]
    otherwise: List[Any]
    line: int = 0

@dataclass
class LambdaExpr:
    params: List[ParamDef]
    body_expr: Any
    line: int = 0

@dataclass
class BlockLambda:
    """Multi-line inline function: a function that takes X and does the following...End function."""
    params: List[ParamDef]
    body: List[Any]
    line: int = 0

    # Fields to match FunctionDef interface so _call_function can work with it
    name: str = "<inline>"
    is_async: bool = False

@dataclass
class MapExpr:
    func_expr: Any
    list_expr: Any
    line: int = 0

@dataclass
class FilterExpr:
    list_expr: Any
    var_name: str
    condition: Any
    line: int = 0

@dataclass
class EnumDef:
    name: str
    values: List[str]
    line: int = 0

# ── Phase 8 ───────────────────────────────────────────────────────────────────

@dataclass
class AttemptStmt:
    try_body: List[Any]
    error_var: str
    catch_body: List[Any]
    line: int = 0

@dataclass
class WaitExpr:
    expr: Any
    line: int = 0

# ── Phase B — Beginner Power Features ────────────────────────────────────

@dataclass
class RangeLoopStmt:
    var_name: str        # loop variable
    from_expr: Any       # start value
    to_expr: Any         # end value (inclusive)
    step_expr: Any       # step (None = 1)
    body: List[Any]
    line: int = 0

@dataclass
class AllWhereExpr:
    var_name: str        # iteration variable
    source_expr: Any     # the list to filter
    condition: Any       # filter condition (uses var_name)
    line: int = 0

@dataclass
class WhenStmt:
    event: str           # "enter", "closes", "click"
    widget_expr: Any     # widget to bind (None for window events)
    body: List[Any]
    line: int = 0

# ── Phase A — High-Level GUI ──────────────────────────────────────────────────

@dataclass
class CreateWindowStmt:
    var_name: str        # variable to bind the window to
    title_expr: Any
    width_expr: Any
    height_expr: Any
    line: int = 0

@dataclass
class AddWidgetStmt:
    widget_type: str     # "button", "label", "input"
    window_expr: Any
    label_expr: Any      # text/label (None for input)
    var_name: str        # binding name (optional for button/label, required for input)
    callback_body: Any   # BlockLambda / FunctionDef ref for buttons (None for others)
    row_expr: Any        # grid row (optional)
    col_expr: Any        # grid col (optional)
    colspan_expr: Any    # colspan (optional)
    line: int = 0

@dataclass
class RunWindowStmt:
    window_expr: Any
    line: int = 0

@dataclass
class SetTextStmt:
    widget_expr: Any
    value_expr: Any
    line: int = 0

@dataclass
class EnumAccess:
    enum_name: str
    value_name: str
    line: int = 0

@dataclass
class CliArgsExpr:
    line: int = 0

@dataclass
class EnvVarExpr:
    name_expr: Any
    line: int = 0

@dataclass
class TestBlock:
    name: str
    body: List[Any]
    line: int = 0

@dataclass
class AssertStmt:
    condition: Any
    line: int = 0

@dataclass
class RunTestsStmt:
    line: int = 0

@dataclass
class RegexMatchExpr:
    pattern_expr: Any
    text_expr: Any
    line: int = 0

@dataclass
class RegexTestExpr:
    text_expr: Any
    pattern_expr: Any
    line: int = 0

@dataclass
class StringIndexExpr:
    str_expr: Any
    index_expr: Any
    line: int = 0

@dataclass
class StringSliceExpr:
    str_expr: Any
    start_expr: Any
    end_expr: Any
    line: int = 0

# Statements

@dataclass
class LetStmt:
    name: str
    expr: Any
    line: int = 0

@dataclass
class DisplayStmt:
    expr: Any
    line: int = 0

@dataclass
class SayStmt:
    parts: List[Any]
    line: int = 0

@dataclass
class AskStmt:
    variable: str
    line: int = 0

@dataclass
class IfStmt:
    condition: Any      # Condition or CompoundCondition
    then_body: List[Any]
    else_body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class RepeatStmt:
    count: Any          # expression (not just int)
    body: List[Any]
    line: int = 0

@dataclass
class WhileStmt:
    condition: Any
    body: List[Any]
    line: int = 0

@dataclass
class ForEachStmt:
    var: str
    iterable: Any
    body: List[Any]
    line: int = 0

@dataclass
class FunctionDef:
    name: str
    params: List[ParamDef]
    body: List[Any]
    is_async: bool = False
    line: int = 0

@dataclass
class CallStmt:
    name: str
    args: List[Any]
    line: int = 0
    obj_expr: Optional[Any] = None
    chained_calls: Optional[List[tuple[str, List[Any], int]]] = None

@dataclass
class LetResultStmt:
    variable: str
    func_name: str
    args: List[Any]
    line: int = 0
    obj_expr: Optional[Any] = None
    chained_calls: Optional[List[tuple[str, List[Any], int]]] = None

@dataclass
class GiveBackStmt:
    expr: Any
    line: int = 0

@dataclass
class AddToListStmt:
    value: Any
    list_name: str
    line: int = 0

@dataclass
class RemoveFromListStmt:
    index: Any
    list_name: str
    line: int = 0

@dataclass
class StopStmt:
    line: int = 0

@dataclass
class SkipStmt:
    line: int = 0


# ─── Parser ────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── Utilities ──────────────────────────────────────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek_ahead(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect_word(self, *words: str) -> Token:
        tok = self.advance()
        if tok.type != WORD or tok.value.lower() not in [w.lower() for w in words]:
            expected = " or ".join(f"'{w}'" for w in words)
            raise ParseError(f"Line {tok.line}: I expected {expected} but found '{tok.value}'.")
        return tok

    def expect_period(self):
        tok = self.advance()
        if tok.type != PERIOD:
            raise ParseError(f"Line {tok.line}: I expected a period to end the statement but found '{tok.value}'.")

    def expect_rbrace(self):
        tok = self.advance()
        if tok.type != RBRACE:
            raise ParseError(f"Line {tok.line}: I expected a closing '}}' but found '{tok.value}'.")

    def word_is(self, *words: str) -> bool:
        tok = self.current()
        return tok.type == WORD and tok.value.lower() in [w.lower() for w in words]

    def match_word(self, *words: str) -> bool:
        if self.word_is(*words):
            self.advance()
            return True
        return False

    # ── Top-level ──────────────────────────────────────────────────────────────

    def parse(self) -> List[Any]:
        statements = []
        while self.current().type != EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def parse_block(self, end_keywords: List[str]) -> List[Any]:
        statements = []
        while self.current().type != EOF:
            if self.word_is(*end_keywords):
                break
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        return statements

    # ── Statement dispatch ─────────────────────────────────────────────────────

    def parse_statement(self) -> Optional[Any]:
        tok = self.current()
        line = tok.line

        if tok.type == EOF:
            return None

        if tok.type != WORD:
            raise ParseError(f"Line {line}: I expected a keyword to start a statement but found '{tok.value}'.")

        kw = tok.value.lower()

        if kw == "let":        return self.parse_let()
        elif kw == "display":  return self.parse_display()
        elif kw == "say":      return self.parse_say()
        elif kw == "ask":      return self.parse_ask()
        elif kw == "if":       return self.parse_if()
        elif kw == "repeat":   return self.parse_repeat()
        elif kw == "while":    return self.parse_while()
        elif kw == "for":      return self.parse_for_each()
        elif kw == "define":   return self.parse_define()
        elif kw == "call":     return self.parse_call_stmt()
        elif kw == "give":     return self.parse_give_back()
        elif kw == "add":      return self.parse_add_dispatch()
        elif kw == "set":      return self.parse_set_stmt_dispatch()
        elif kw == "write":    return self.parse_write_file()
        elif kw == "append":   return self.parse_append_file()
        elif kw == "import":   return self.parse_import()
        elif kw == "throw":    return self.parse_throw()
        elif kw == "attempt":  return self.parse_attempt()
        elif kw == "remove":
            if self.peek_ahead().type == WORD and self.peek_ahead().value.lower() == "the":
                return self.parse_remove_dict()
            else:
                return self.parse_remove_from_list()
        elif kw == "stop":
            self.advance()
            self.expect_word("loop")
            self.expect_period()
            return StopStmt(line)
        elif kw == "skip":
            self.advance()
            self.expect_word("to")
            self.expect_word("next")
            self.expect_period()
            return SkipStmt(line)
        elif kw == "try":    return self.parse_try()
        elif kw == "sort":   return self.parse_sort_list()
        # Phase 6
        elif kw == "check":  return self.parse_check()
        elif kw == "test":   return self.parse_test_block()
        elif kw == "assert": return self.parse_assert()
        elif kw == "run":    return self.parse_run_dispatch()
        # Phase A — GUI statements
        elif kw == "create": return self.parse_create_window()
        elif kw == "add":    return self.parse_add_dispatch()
        # Phase B — Beginner features
        elif kw == "when":   return self.parse_when_stmt()
        else:
            raise ParseError(
                f"Line {line}: I do not understand the keyword '{tok.value}'. "
                f"💡 Common keywords: Let, Say, If, While, Repeat, For, Define, Call, "
                f"Add, Set, Remove, Write, Append, Import, Create, Run, When, Stop, Skip."
            )

    # ── Let ───────────────────────────────────────────────────────────────────

    def parse_let(self) -> Any:
        line = self.current().line
        self.advance()  # "Let"

        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: After 'Let' I expected a variable name.")
        var_name = name_tok.value
        self.expect_word("be")

        # "Let X be the result of calling F [on obj] with args [then call G with args]."
        if self.word_is("the"):
            saved = self.pos
            self.advance()
            if self.word_is("result"):
                self.advance()
                if self.word_is("of"):
                    self.advance()
                    if self.word_is("calling"):
                        self.advance()
                        func_tok = self.advance()
                        if func_tok.type != WORD:
                            raise ParseError(f"Line {line}: Expected function name after 'calling'.")
                        func_name = func_tok.value
                        
                        obj_expr = None
                        if self.word_is("on"):
                            self.advance()
                            obj_expr = self.parse_expr()
                            
                        args = [] # Initialize args
                        if self.word_is("with"):
                            self.advance()
                            if self.word_is("no") and self.peek_ahead().value.lower() == "parameters":
                                self.advance() # "no"
                                self.advance() # "parameters"
                            else:
                                args = self.parse_arg_list()
                                
                        chained_calls = []
                        while self.word_is("then"):
                            self.advance()
                            self.expect_word("call")
                            c_name_tok = self.advance()
                            if c_name_tok.type != WORD:
                                 raise ParseError(f"Line {self.current().line}: Expected a method name after 'then call'.")
                            c_name = c_name_tok.value
                            c_line = c_name_tok.line
                            c_args = []
                            if self.word_is("with"):
                                 self.advance()
                                 if self.word_is("no") and self.peek_ahead().value.lower() == "parameters":
                                     self.advance(); self.advance()
                                 else:
                                     c_args = self.parse_arg_list()
                            chained_calls.append((c_name, c_args, c_line))
                                     
                        self.expect_period()
                        return LetResultStmt(var_name, func_name, args, line, obj_expr, chained_calls)
            
            # roll back "the" if it wasn't a LetResultStmt
            self.pos = saved

        expr = self.parse_expr()
        self.expect_period()
        return LetStmt(var_name, expr, line)

    # ── Display ───────────────────────────────────────────────────────────────

    def parse_display(self) -> DisplayStmt:
        line = self.current().line
        self.advance()
        expr = self.parse_expr()
        self.expect_period()
        return DisplayStmt(expr, line)

    # ── Say ───────────────────────────────────────────────────────────────────

    def parse_say(self) -> SayStmt:
        line = self.current().line
        self.advance()
        parts = [self.parse_say_part()]
        while self.current().type == COMMA:
            self.advance()
            parts.append(self.parse_say_part())
        self.expect_period()
        return SayStmt(parts, line)

    def parse_say_part(self) -> Any:
        """
        A say-part is comma/period delimited.
        Route to parse_expr only when we're sure it's a built-in expression,
        otherwise collect words greedily as a string or identifier.
        """
        tok = self.current()

        # Unambiguous built-in expression starters
        ALWAYS_EXPR = {"uppercase", "lowercase", "item", "an", "length"}
        # A standalone NUMBER (followed by comma/period/EOF) → evaluated expression.
        # A standalone negative number (-NUMBER) → also evaluated expression.
        # A NUMBER followed by WORDs (e.g. "3 plus 5 equals") → literal text label.
        is_num = tok.type == NUMBER
        is_neg_num = tok.type == MINUS and self.peek_ahead().type == NUMBER

        if is_num or is_neg_num:
            # Check the token after the number
            next_tok = self.peek_ahead() if is_num else self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else Token(EOF, "", tok.line)
            if next_tok.type in (COMMA, PERIOD, EOF):
                return self.parse_expr()
            # else fall through to word collector below
        if tok.type == WORD and tok.value.lower() in ALWAYS_EXPR:
            return self.parse_expr()
        # "a list containing …" or "a list"
        if tok.type == WORD and tok.value.lower() == "a":
            if self.peek_ahead().type == WORD and self.peek_ahead().value.lower() in ("list", "empty"):
                return self.parse_expr()
        # "the length of …", "the keys of ...", "the X of Y", etc.
        if tok.type == WORD and tok.value.lower() == "the":
            nxt_tok = self.peek_ahead()
            if nxt_tok.type == WORD:
                nxt = nxt_tok.value.lower()
                if nxt in ("length", "json", "result", "keys", "value", "contents", "current"):
                    return self.parse_expr()
                # Check for "the [prop] of [obj]"
                if self.pos + 2 < len(self.tokens):
                    after_nxt = self.tokens[self.pos + 2].value.lower() if self.tokens[self.pos+2].type == WORD else ""
                    if after_nxt == "of":
                        return self.parse_expr()
                
        # Explicit String syntax
        if tok.type == STRING_QUOTED:
            return self.parse_expr()
        if tok.type == INTERP_STRING:
            return self.parse_expr()

        # Otherwise: collect words until comma/period
        words = []
        while self.current().type not in (COMMA, PERIOD, EOF):
            t = self.current()
            if t.type in (NUMBER, WORD):
                words.append(t.value)
                self.advance()
            else:
                break
        if not words:
            raise ParseError(f"Line {self.current().line}: Nothing to say here.")
        if len(words) == 1:
            w = words[0]
            if w.lower() == "true":  return BoolLiteral(True)
            if w.lower() == "false": return BoolLiteral(False)
            try: return NumberLiteral(float(w))
            except ValueError: pass
            return Identifier(w)
        return StringLiteral(" ".join(words))

    # ── Ask ───────────────────────────────────────────────────────────────────

    def parse_ask(self) -> AskStmt:
        line = self.current().line
        self.advance()
        self.expect_word("the")
        self.expect_word("user")
        self.expect_word("for")
        var_tok = self.advance()
        if var_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a variable name after 'Ask the user for'.")
        self.expect_period()
        return AskStmt(var_tok.value, line)

    # ── If ────────────────────────────────────────────────────────────────────

    def parse_if(self) -> IfStmt:
        line = self.current().line
        self.advance()
        condition = self.parse_compound_condition()
        self.expect_word("then")
        self.expect_word("do")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        then_body = self.parse_block(["Otherwise", "End"])
        else_body = []
        if self.word_is("Otherwise"):
            self.advance()
            self.expect_word("do")
            self.expect_word("the")
            self.expect_word("following")
            self.expect_period()
            else_body = self.parse_block(["End"])
        self.expect_word("End")
        self.expect_word("if")
        self.expect_period()
        return IfStmt(condition, then_body, else_body, line)

    # ── Repeat ────────────────────────────────────────────────────────────────

    def parse_repeat(self) -> RepeatStmt:
        line = self.current().line
        self.advance()
        count = self.parse_factor()   # allow variable, not just literal
        self.expect_word("times")
        self.expect_word("do")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        body = self.parse_block(["End"])
        self.expect_word("End")
        self.expect_word("repeat")
        self.expect_period()
        return RepeatStmt(count, body, line)

    # ── While ─────────────────────────────────────────────────────────────────

    def parse_while(self) -> WhileStmt:
        line = self.current().line
        self.advance()
        condition = self.parse_compound_condition()
        self.expect_word("do")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        body = self.parse_block(["End"])
        self.expect_word("End")
        self.expect_word("while")
        self.expect_period()
        return WhileStmt(condition, body, line)

    # ── For Each ──────────────────────────────────────────────────────────────

    def parse_for_each(self) -> ForEachStmt:
        line = self.current().line
        self.advance()   # "For"
        self.expect_word("each")
        var_tok = self.advance()
        if var_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a variable name after 'For each'.")
        var_name = var_tok.value

        if self.word_is("from"):
            # Range loop: "For each X from N to M [step S] do the following."
            self.advance()  # "from"
            from_expr = self.parse_expr()
            self.expect_word("to")
            to_expr = self.parse_expr()
            step_expr = None
            if self.word_is("step"):
                self.advance()
                step_expr = self.parse_expr()
            self.expect_word("do")
            self.expect_word("the")
            self.expect_word("following")
            self.expect_period()
            body = self.parse_block(["End"])
            self.advance()  # "End"
            self.expect_word("for")
            self.expect_period()
            return RangeLoopStmt(var_name, from_expr, to_expr, step_expr, body, line)
        else:
            # Original: "For each X in ITERABLE do the following."
            self.expect_word("in")
            iterable = self.parse_expr()
            self.expect_word("do")
            self.expect_word("the")
            self.expect_word("following")
            self.expect_period()
            body = self.parse_block(["End"])
            self.advance()  # "End"
            self.expect_word("for")
            self.expect_period()
            return ForEachStmt(var_name, iterable, body, line)

    # ── Function Definition ───────────────────────────────────────────────────

    # ── Definitions (Function, Class, Method) ──────────────────────────────────
    def parse_define(self) -> Any:
        line = self.current().line
        self.advance()  # "Define"
        if self.word_is("a") or self.word_is("an"):
            self.advance()
        else:
            raise ParseError(f"Line {line}: Expected 'a' or 'an' after 'Define'.")
            
        is_async = False
        if self.word_is("async"):
            is_async = True
            self.advance()
        
        nxt = self.current().value.lower()
        if nxt == "function":
            func_def = self.parse_function_def_rest(line)
            func_def.is_async = is_async
            return func_def
        elif nxt == "class":
            return self.parse_class_def(line)
        elif nxt == "method":
            return self.parse_method_def(line)
        elif nxt == "enum":
            return self.parse_enum_def(line)
        else:
            raise ParseError(f"Line {line}: Expected 'function', 'class', 'method', or 'enum' after 'Define a/an'.")

    def parse_function_def_rest(self, line: int) -> FunctionDef:
        self.advance()  # "function"
        self.expect_word("called")
        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a function name after 'called'.")
        func_name = name_tok.value

        # "that takes X and does" or "with no parameters and does"
        self.expect_word("that")
        params = []
        if self.word_is("takes"):
            self.advance()
            if self.word_is("no"):
                self.advance()
                self.expect_word("parameters")
                params = []
            else:
                params = self.parse_param_list()
        elif self.word_is("with"):
            self.advance()
            self.expect_word("no")
            self.expect_word("parameters")
            params = []
        self.expect_word("and")
        self.expect_word("does")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        body = self.parse_block(["End"])
        self.advance() # "End"
        self.expect_word("function")
        self.expect_period()
        return FunctionDef(func_name, params, body, line)

    def parse_class_def(self, line: int) -> ClassDef:
        self.advance() # "class"
        self.expect_word("called")
        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a class name.")
        class_name = name_tok.value
        
        parent = None
        if self.word_is("that"):
            self.advance()
            self.expect_word("extends")
            parent_tok = self.advance()
            if parent_tok.type != WORD:
                raise ParseError(f"Line {line}: Expected a parent class name after 'extends'.")
            parent = parent_tok.value
        
        props = []
        if self.word_is("with"):
            self.advance()
            self.expect_word("properties")
            props = [p.name for p in self.parse_param_list()]
        self.expect_period()
        return ClassDef(class_name, props, parent, line)

    def parse_enum_def(self, line: int) -> EnumDef:
        self.advance()  # "enum"
        self.expect_word("called")
        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected an enum name.")
        enum_name = name_tok.value
        self.expect_word("with")
        self.expect_word("values")
        values = self.parse_param_list()
        self.expect_period()
        return EnumDef(enum_name, values, line)

    def parse_method_def(self, line: int) -> MethodDef:
        self.advance() # "method"
        self.expect_word("called")
        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a method name.")
        method_name = name_tok.value
        
        self.expect_word("for")
        class_tok = self.advance()
        if class_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a class name for the method.")
        class_name = class_tok.value
        
        self.expect_word("that")
        params = []
        if self.word_is("takes"):
            self.advance()
            if self.word_is("no"):
                self.advance()
                self.expect_word("parameters")
                params = []
            else:
                params = self.parse_param_list()
        elif self.word_is("with"):
            self.advance()
            self.expect_word("no")
            self.expect_word("parameters")
            params = []
            
        self.expect_word("and")
        self.expect_word("does")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        
        body = self.parse_block(["End"])
        self.advance() # "End"
        self.expect_word("method")
        self.expect_period()
        return MethodDef(class_name, method_name, params, body, line)

    def parse_param_list(self) -> List[ParamDef]:
        params = []
        while True:
            if self.word_is("and"):
                saved = self.pos
                self.advance()
                if self.word_is("does", "following", "with", "gives"):
                    self.pos = saved
                    break
                else:
                    param_tok = self.advance()
                    if param_tok.type != WORD:
                        raise ParseError(f"Line {self.current().line}: Expected a parameter name.")
                    default_expr = None
                    if self.word_is("defaulting"):
                        self.advance()
                        self.expect_word("to")
                        default_expr = self.parse_expr()
                    params.append(ParamDef(param_tok.value, default_expr))
                    break
            elif self.current().type == COMMA:
                self.advance()
            elif self.current().type == WORD and not self.word_is("and", "does", "following", "that", "with"):
                name = self.advance().value
                default_expr = None
                if self.word_is("defaulting"):
                    self.advance()
                    self.expect_word("to")
                    default_expr = self.parse_expr()
                params.append(ParamDef(name, default_expr))
            else:
                break
        return params

    # ── Call ──────────────────────────────────────────────────────────────────

    def parse_call_stmt(self) -> Any:
        line = self.current().line
        self.advance()
        name_tok = self.advance()
        if name_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a function name after 'Call'.")
        func_name = name_tok.value

        obj_expr = None
        if self.word_is("on"):
            self.advance()
            obj_expr = self.parse_expr()

        if self.word_is("with"):
            self.advance()
            if self.word_is("no") and self.peek_ahead().value.lower() == "parameters":
                self.advance() # "no"
                self.advance() # "parameters"
                args = []
            else:
                args = self.parse_arg_list()
        else:
            args = []
            
        chained_calls = []
        while self.word_is("then"):
            self.advance()
            self.expect_word("call")
            c_name_tok = self.advance()
            if c_name_tok.type != WORD:
                 raise ParseError(f"Line {self.current().line}: Expected a method name after 'then call'.")
            c_name = c_name_tok.value
            c_line = c_name_tok.line
            c_args = []
            if self.word_is("with"):
                 self.advance()
                 if self.word_is("no") and self.peek_ahead().value.lower() == "parameters":
                     self.advance(); self.advance()
                 else:
                     c_args = self.parse_arg_list()
            chained_calls.append((c_name, c_args, c_line))

        self.expect_period()
        return CallStmt(func_name, args, line, obj_expr, chained_calls)

    def parse_arg_list(self) -> List[Any]:
        args = [self.parse_expr()]
        while self.current().type == COMMA:
            self.advance()
            args.append(self.parse_expr())
        return args

    def parse_dict_arg_list(self) -> List[tuple[Any, Any]]:
        pairs = []
        while True:
            key_expr = self.parse_expr()
            if self.current().type != COLON:
                raise ParseError(f"Line {self.current().line}: Expected a colon ':' after dictionary key.")
            self.advance()
            value_expr = self.parse_expr()
            pairs.append((key_expr, value_expr))
            if self.current().type == COMMA:
                self.advance()
            else:
                break
        return pairs

    # ── Give Back ────────────────────────────────────────────────────────────

    def parse_give_back(self) -> GiveBackStmt:
        line = self.current().line
        self.advance()
        self.expect_word("back")
        expr = self.parse_expr()
        self.expect_period()
        return GiveBackStmt(expr, line)

    # ── Add to List ───────────────────────────────────────────────────────────

    def parse_add_to_list(self) -> AddToListStmt:
        line = self.current().line
        self.advance()  # "Add"
        value = self.parse_expr()
        self.expect_word("to")
        list_tok = self.advance()
        if list_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a list variable name after 'to'.")
        self.expect_period()
        return AddToListStmt(value, list_tok.value, line)

    # ── Remove from List ──────────────────────────────────────────────────────

    def parse_remove_from_list(self) -> RemoveFromListStmt:
        line = self.current().line
        self.advance()  # "Remove"
        self.expect_word("item")
        index = self.parse_expr()
        self.expect_word("from")
        list_tok = self.advance()
        if list_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a list variable name after 'from'.")
        self.expect_period()
        return RemoveFromListStmt(index, list_tok.value, line)

    # ── Dictionary / Object Statements ──────────────────────────────────────────

    def parse_set_stmt_dispatch(self) -> Any:
        line = self.current().line
        self.advance()  # "Set"
        self.expect_word("the")
        
        # Look ahead to see if it's dictionary value or object property
        if self.word_is("value") and self.peek_ahead().value.lower() == "for":
            # Dictionary case: Set the value for K in D to V.
            self.advance() # "value"
            self.expect_word("for")
            key_expr = self.parse_expr()
            self.expect_word("in")
            dict_expr = self.parse_expr()
            self.expect_word("to")
            value_expr = self.parse_expr()
            self.expect_period()
            return SetDictValueStmt(dict_expr, key_expr, value_expr, line)
        else:
            # Object property case: Set the age of p to 31.
            prop_tok = self.advance()
            if prop_tok.type != WORD:
                raise ParseError(f"Line {line}: Expected a property name after 'the'.")
            prop_name = prop_tok.value
            self.expect_word("of")
            obj_expr = self.parse_expr()
            self.expect_word("to")
            value_expr = self.parse_expr()
            self.expect_period()
            return SetPropertyStmt(obj_expr, prop_name, value_expr, line)

    def parse_remove_dict(self) -> RemoveDictValueStmt:
        line = self.current().line
        self.advance()  # "Remove"
        self.expect_word("the")
        self.expect_word("value")
        self.expect_word("for")
        key_expr = self.parse_expr()
        self.expect_word("in")
        dict_expr = self.parse_expr()
        self.expect_period()
        return RemoveDictValueStmt(dict_expr, key_expr, line)



    # ── Phase 4 File / System Statements ──────────────────────────────────────

    def parse_write_file(self) -> WriteFileStmt:
        line = self.current().line
        self.advance()  # "Write"
        content_expr = self.parse_expr()
        self.expect_word("to")
        self.expect_word("file")
        file_expr = self.parse_expr()
        self.expect_period()
        return WriteFileStmt(content_expr, file_expr, line)

    def parse_append_file(self) -> AppendFileStmt:
        line = self.current().line
        self.advance()  # "Append"
        content_expr = self.parse_expr()
        self.expect_word("to")
        self.expect_word("file")
        file_expr = self.parse_expr()
        self.expect_period()
        return AppendFileStmt(content_expr, file_expr, line)

    def parse_import(self) -> ImportStmt:
        line = self.current().line
        self.advance()  # "Import"
        
        specific_imports = None
        if self.current().type == LBRACE:
            self.advance() # "{"
            specific_imports = []
            while self.current().type != RBRACE:
                name_tok = self.advance()
                if name_tok.type != WORD:
                    raise ParseError(f"Line {line}: Expected an identifier to import.")
                specific_imports.append(name_tok.value)
                if self.current().type == COMMA:
                    self.advance()
            self.expect_rbrace()
            self.expect_word("from")
            
        elif self.word_is("functions"):
            self.advance()
            self.expect_word("from")
            
        file_expr = self.parse_expr()
        
        alias = None
        if self.word_is("as"):
            self.advance()
            alias_tok = self.advance()
            if alias_tok.type != WORD:
                raise ParseError(f"Line {line}: Expected an alias name after 'as'.")
            alias = alias_tok.value
            
        self.expect_period()
        return ImportStmt(file_expr, alias, specific_imports, line)

    def parse_throw(self) -> ThrowStmt:
        line = self.current().line
        self.advance()  # "Throw"
        self.expect_word("error")
        msg_expr = self.parse_expr()
        self.expect_period()
        return ThrowStmt(msg_expr, line)

    def parse_attempt(self) -> AttemptStmt:
        line = self.current().line
        self.advance() # "Attempt"
        self.expect_word("to")
        self.expect_word("do")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        
        try_body = self.parse_block(["Rescue"])
        
        self.advance() # "Rescue"
        self.expect_word("error")
        self.expect_word("as")
        var_tok = self.advance()
        if var_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a variable name after 'as'.")
        error_var = var_tok.value
        self.expect_period()
        
        catch_body = self.parse_block(["End"])
        
        self.advance() # "End"
        self.expect_word("attempt")
        self.expect_period()
        
        return AttemptStmt(try_body, error_var, catch_body, line)

    # ── Compound Condition (and / or) ─────────────────────────────────────────

    def parse_condition(self) -> Any:
        return self.parse_compound_condition()

    def parse_compound_condition(self) -> Any:
        line = self.current().line
        left = self.parse_single_condition()
        while self.word_is("and", "or"):
            connective = self.advance().value.lower()
            right = self.parse_single_condition()
            left = CompoundCondition(left, connective, right, line)
        return left

    # ── Single Condition ──────────────────────────────────────────────────────

    def parse_single_condition(self) -> Condition:
        line = self.current().line

        # "file F exists"
        if self.word_is("file"):
            self.advance()  # 'file'
            file_expr = self.parse_expr()
            self.expect_word("exists")
            return FileExists(file_expr, line)

        left = self.parse_expr()
        tok = self.current()

        # If parse_expr already consumed a full boolean expr (ContainsExpr, etc.),
        # just return it directly — no comparison operator needed.
        boolean_expr_types = ("ContainsExpr", "StartsWithExpr", "EndsWithExpr", "BoolLiteral")
        if type(left).__name__ in boolean_expr_types:
            return left

        # ── Symbol operators ──────────────────────────────────────────────────
        if tok.type == GT:
            self.advance(); op = "greater_than"
        elif tok.type == GTE:
            self.advance(); op = "greater_equal"
        elif tok.type == LT:
            self.advance(); op = "less_than"
        elif tok.type == LTE:
            self.advance(); op = "less_equal"
        elif tok.type == EQ:
            self.advance(); op = "equals"
        elif tok.type == NEQ:
            self.advance(); op = "not_equals"

        # ── English operators ─────────────────────────────────────────────────
        elif self.word_is("equals"):
            self.advance(); op = "equals"
        elif self.word_is("is"):
            self.advance()
            if self.word_is("greater"):
                self.advance(); self.expect_word("than")
                if self.word_is("or"):
                    self.advance(); self.expect_word("equal"); self.expect_word("to")
                    op = "greater_equal"
                else:
                    op = "greater_than"
            elif self.word_is("less"):
                self.advance(); self.expect_word("than")
                if self.word_is("or"):
                    self.advance(); self.expect_word("equal"); self.expect_word("to")
                    op = "less_equal"
                else:
                    op = "less_than"
            elif self.word_is("equal"):
                self.advance(); self.expect_word("to"); op = "equals"
            elif self.word_is("not"):
                self.advance()
                if self.word_is("equal"):
                    self.advance(); self.expect_word("to"); op = "not_equals"
                else:
                    op = "not_equals"   # bare "is not X"
            # ── Type checks — "X is a number / text / list / boolean" ─────────
            elif self.word_is("a"):
                self.advance()
                type_tok = self.advance()
                type_word = type_tok.value.lower()
                if type_word not in ("number", "text", "list", "boolean"):
                    raise ParseError(
                        f"Line {line}: After 'is a' I expected 'number', 'text', 'list', or 'boolean' "
                        f"but found '{type_tok.value}'."
                    )
                return Condition(left, f"is_{type_word}", None, line)
            # bare "is number / text / list / boolean" (without 'a')
            elif self.word_is("number", "text", "list", "boolean"):
                type_word = self.advance().value.lower()
                return Condition(left, f"is_{type_word}", None, line)
            else:
                op = "equals"  # bare "is X"
        elif self.word_is("has"):
            self.advance()
            self.expect_word("the")
            self.expect_word("key")
            op = "has_key"
        else:
            raise ParseError(
                f"Line {line}: I expected a comparison operator "
                f"(like 'is greater than', '>', '=', etc.) but found '{tok.value}'."
            )

        right = self.parse_expr()
        return Condition(left, op, right, line)

    # ── Expression (arithmetic) ───────────────────────────────────────────────

    def parse_expr(self) -> Any:
        """expr := term {('+' | '-' | 'plus' | 'minus') term} ... plus Phase 3 infix ops"""
        line = self.current().line
        left = self.parse_term()

        while True:
            if self.word_is("plus", "minus") or self.current().type in (PLUS, MINUS):
                tok = self.advance()
                op = "plus" if tok.value in ("+", "plus") else "minus"
                right = self.parse_term()
                left = BinOp(left, op, right, line)

            elif self.word_is("contains"):
                self.advance()
                right = self.parse_expr()
                # Determine if left is a list or string by falling back to ContainsExpr, 
                # which handles both dynamically in the interpreter.
                left = ContainsExpr(left, right, line)

            elif self.word_is("as"):
                saved_pos = self.pos
                self.advance()
                if self.word_is("a"):
                    self.advance()
                if self.word_is("number", "numbers"):
                    self.advance()
                    left = AsNumber(left, line)
                elif self.word_is("text"):
                    self.advance()
                    left = AsText(left, line)
                else:
                    # rollback if it isn't 'as a number' or 'as text' (though unlikely)
                    self.pos = saved_pos
                    break
            else:
                break

        return left

    def parse_term(self) -> Any:
        """term := factor {('*'|'/'|'%'|'times'|'divided by'|'modulo') factor}"""
        line = self.current().line
        left = self.parse_factor()
        while (self.word_is("times", "divided", "modulo") or
               self.current().type in (STAR, SLASH, PERCENT)):
            tok = self.advance()
            v = tok.value.lower()
            if v == "/" or tok.type == SLASH:
                op = "divided_by"
            elif v == "%" or tok.type == PERCENT:
                op = "modulo"
            elif v == "divided":
                self.expect_word("by")
                op = "divided_by"
            elif v == "modulo":
                op = "modulo"
            else:
                op = "times"
            right = self.parse_factor()
            left = BinOp(left, op, right, line)
        return left

    def parse_factor(self) -> Any:
        tok = self.current()
        line = tok.line

        # ── Unary minus ───────────────────────────────────────────────────────
        if tok.type == MINUS:
            self.advance()
            operand = self.parse_factor()
            return UnaryMinus(operand, line)

        # ── Number literal ────────────────────────────────────────────────────
        if tok.type == NUMBER:
            self.advance()
            return NumberLiteral(float(tok.value), line)

        # ── Quoted String literal ─────────────────────────────────────────────
        if tok.type == STRING_QUOTED:
            self.advance()
            return StringLiteral(tok.value, line)

        # ── Interpolated String ──────────────────────────────────────────────
        if tok.type == INTERP_STRING:
            self.advance()
            return self._parse_interpolated_string(tok.value, line)

        if tok.type == WORD:
            val = tok.value.lower()

            if val == "true":  self.advance(); return BoolLiteral(True, line)
            if val == "false": self.advance(); return BoolLiteral(False, line)
            if val == "nothing" or val == "empty": self.advance(); return NoneLiteral(line)

            # ── Built-in expressions starting with keywords ────────────────────

            # "a list containing X, Y, Z"  or  "an empty list"
            # "a dictionary containing K: V" or "an empty dictionary"
            # "a new Person with name: 'Alice', age: 30"
            # "a function that takes X and gives back EXPR"
            if (val == "a" or val == "an") and (
                self.peek_ahead().type == WORD and
                self.peek_ahead().value.lower() in ("list", "empty", "dictionary", "new", "function")
            ):
                self.advance()  # consume 'a' / 'an'
                nxt = self.current().value.lower()
                if nxt == "list":
                    self.advance()
                    if self.word_is("containing"):
                        self.advance()
                        elements = self.parse_arg_list()
                        return ListLiteral(elements, line)
                    else:
                        return ListLiteral([], line)  # bare "a list"
                elif nxt == "dictionary":
                    self.advance()
                    if self.word_is("containing"):
                        self.advance()
                        pairs = self.parse_dict_arg_list()
                        return DictLiteral(pairs, line)
                    else:
                        return DictLiteral([], line)
                elif nxt == "new":
                    self.advance() # "new"
                    class_tok = self.advance()
                    if class_tok.type != WORD:
                        raise ParseError(f"Line {line}: Expected a class name after 'new'.")
                    class_name = class_tok.value
                    args = []
                    if self.word_is("with"):
                        self.advance()
                        args = self.parse_dict_arg_list() # name: value pairs
                    return NewInstanceExpr(class_name, args, line)
                elif nxt == "function":
                    # "a function that takes X and gives back EXPR"     (single-expression lambda)
                    # "a function that takes X and does the following... End function."  (multi-line BlockLambda)
                    self.advance()  # "function"
                    self.expect_word("that")
                    params = []
                    if self.word_is("takes"):
                        self.advance()
                        if self.word_is("no"):
                            self.advance()
                            self.expect_word("parameters")
                        else:
                            params = self.parse_param_list()
                    self.expect_word("and")
                    if self.word_is("gives"):
                        # Single-expression form: "and gives back EXPR"
                        self.expect_word("gives")
                        self.expect_word("back")
                        body_expr = self.parse_expr()
                        return LambdaExpr(params, body_expr, line)
                    elif self.word_is("does"):
                        # Multi-line block form: "and does the following...End function."
                        self.expect_word("does")
                        self.expect_word("the")
                        self.expect_word("following")
                        self.expect_period()
                        body = self.parse_block(["End"])
                        self.advance()  # "End"
                        self.expect_word("function")
                        self.expect_period()
                        return BlockLambda(params, body, line)
                    else:
                        raise ParseError(f"Line {line}: Expected 'gives back' or 'does the following' after function parameters.")
                else:  # "empty"
                    self.advance()
                    if self.word_is("list"):
                        self.advance()
                        return ListLiteral([], line)
                    elif self.word_is("dictionary"):
                        self.advance()
                        return DictLiteral([], line)
                    else:
                        raise ParseError(f"Line {line}: Expected 'list' or 'dictionary' after 'an empty'.")

            # Enum access: "Color Red"
            # Check if current word is a known identifier followed by another word
            # This will be handled at interpret-time by checking if it's an enum

            # "waiting for X"
            if val == "waiting":
                self.advance() # "waiting"
                self.expect_word("for")
                expr = self.parse_expr()
                return WaitExpr(expr, line)

            # "all X in LIST where CONDITION"  (inline filter)
            if val == "all":
                self.advance()  # "all"
                var_tok = self.advance()  # item variable name
                var_name = var_tok.value
                self.expect_word("in")
                source_expr = self.parse_factor()
                self.expect_word("where")
                condition = self.parse_condition()   # supports > >= < <= is contains
                return AllWhereExpr(var_name, source_expr, condition, line)

            # "the length of X" or "the value for K in D" or "the keys of D"
            if val == "the" and self.peek_ahead().type == WORD:
                nxt = self.peek_ahead().value.lower()
                if nxt == "length":
                    self.advance(); self.advance()
                    self.expect_word("of")
                    expr = self.parse_factor()
                    return LengthOf(expr, line)
                elif nxt == "value":
                    self.advance(); self.advance()
                    self.expect_word("for")
                    key_expr = self.parse_factor()
                    self.expect_word("in")
                    dict_expr = self.parse_factor()
                    return DictAccess(dict_expr, key_expr, line)
                elif nxt == "keys":
                    self.advance(); self.advance()
                    self.expect_word("of")
                    dict_expr = self.parse_factor()
                    return DictKeys(dict_expr, line)
                elif nxt == "contents":
                    self.advance(); self.advance()
                    self.expect_word("of")
                    self.expect_word("file")
                    file_expr = self.parse_factor()
                    return FileContents(file_expr, line)
                elif nxt == "current":
                    self.advance(); self.advance()
                    if self.word_is("date"):
                        self.advance()
                        self.expect_word("and")
                        self.expect_word("time")
                        return TimeOp("datetime", line)
                    elif self.word_is("year"):
                        self.advance()
                        return TimeOp("year", line)
                    elif self.word_is("timestamp"):
                        self.advance()
                        return TimeOp("timestamp", line)
                    else:
                        raise ParseError(f"Line {line}: Expected 'date and time', 'year', or 'timestamp' after 'the current'.")
                elif nxt == "command":
                    # "the command line arguments"
                    self.advance(); self.advance()  # consume "the" and "command"
                    self.expect_word("line")
                    self.expect_word("arguments")
                    return CliArgsExpr(line)
                elif nxt == "environment":
                    # "the environment variable NAME"
                    self.advance(); self.advance()  # consume "the" and "environment"
                    self.expect_word("variable")
                    name_expr = self.parse_factor()
                    return EnvVarExpr(name_expr, line)
                elif nxt == "json":
                    self.advance(); self.advance()
                    if self.word_is("parsed"):
                        self.advance()
                        self.expect_word("from")
                        self.expect_word("text")
                        text_expr = self.parse_factor()
                        return JsonParseExpr(text_expr, line)
                    if self.word_is("for"):
                        self.advance()
                        dict_expr = self.parse_factor()
                        return JsonStringifyExpr(dict_expr, line)
                    self.pos -= 2 # rollback
                elif nxt == "result":
                    self.advance(); self.advance()
                    if self.word_is("of"):
                        self.advance()
                        if self.word_is("fetching"):
                            self.advance()
                            self.expect_word("url")
                            url_expr = self.parse_factor()
                            return HttpGetExpr(url_expr, line)
                        elif self.word_is("posting"):
                            self.advance()
                            self.expect_word("payload")
                            payload_expr = self.parse_factor()
                            self.expect_word("to")
                            self.expect_word("url")
                            url_expr = self.parse_factor()
                            return HttpPostExpr(url_expr, payload_expr, line)
                        elif self.word_is("mapping"):
                            # "the result of mapping F over L"
                            self.advance()
                            func_expr = self.parse_factor()
                            self.expect_word("over")
                            list_expr = self.parse_factor()
                            return MapExpr(func_expr, list_expr, line)
                        elif self.word_is("filtering"):
                            # "the result of filtering L where CONDITION"
                            # The condition uses "item" as the implicit loop variable
                            self.advance()
                            list_expr = self.parse_factor()
                            self.expect_word("where")
                            cond = self.parse_condition()
                            return FilterExpr(list_expr, "item", cond, line)
                        elif self.word_is("matching"):
                            # "the result of matching pattern P in T"
                            self.advance()
                            self.expect_word("pattern")
                            pattern_expr = self.parse_factor()
                            self.expect_word("in")
                            text_expr = self.parse_factor()
                            return RegexMatchExpr(pattern_expr, text_expr, line)
                    self.pos -= 2 # rollback
                else:
                    # General property access: the age of p
                    # We expect "the [prop] of [obj]"
                    # Try to parse it:
                    saved = self.pos
                    self.advance() # "the"
                    prop_tok = self.advance() # [prop]
                    if prop_tok.type == WORD and self.word_is("of"):
                        self.advance() # "of"
                        # Special case: don't accidentally capture "the ... of file" if handled above
                        # Actually we are in the 'else' of the special ones, so it's safe.
                        obj_expr = self.parse_factor()
                        return PropertyAccessExpr(obj_expr, prop_tok.value, line)
                    else:
                        self.pos = saved # rollback "the"

            # bare "keys of D"
            if val == "keys":
                self.advance()
                self.expect_word("of")
                dict_expr = self.parse_factor()
                return DictKeys(dict_expr, line)
            # 'the' NOT followed by 'length' → falls through to multi-word string

            # "substring of text from A to B"
            if val == "substring":
                saved = self.pos
                self.advance()
                if self.word_is("of"):
                    self.advance()
                    text_expr = self.parse_factor()
                    self.expect_word("from")
                    start_expr = self.parse_factor()
                    self.expect_word("to")
                    end_expr = self.parse_factor()
                    return StringSliceExpr(text_expr, start_expr, end_expr, line)
                self.pos = saved
                self.advance()
                return Identifier("substring", line)

            # "character N of text"
            if val == "character":
                saved = self.pos
                self.advance()
                if self.current().type in (NUMBER, WORD) and not self.word_is("is", "equals", "has", "and", "or", "plus", "minus", "times", "divided", "modulo"):
                    index_expr = self.parse_factor()
                    if self.word_is("of"):
                        self.advance()
                        text_expr = self.parse_factor()
                        return StringIndexExpr(text_expr, index_expr, line)
                self.pos = saved
                self.advance()
                return Identifier("character", line)

            # "item N of myList" — or treat as bare identifier if no "of" follows
            if val == "item":
                saved = self.pos
                self.advance()
                if self.current().type in (NUMBER, WORD) and not self.word_is("is", "equals", "has", "and", "or", "plus", "minus", "times", "divided", "modulo"):
                    index = self.parse_factor()
                    if self.word_is("of"):
                        self.advance()
                        list_tok = self.advance()
                        if list_tok.type != WORD:
                            raise ParseError(f"Line {line}: Expected list name after 'of'.")
                        return ListAccess(Identifier(list_tok.value, line), index, line)
                # Rollback — treat "item" as a prose identifier
                self.pos = saved
                self.advance()
                return Identifier("item", line)

            # "uppercase of X"
            if val == "uppercase":
                self.advance()
                self.expect_word("of")
                expr = self.parse_factor()
                return UppercaseOf(expr, line)

            # "lowercase of X"
            if val == "lowercase":
                self.advance()
                self.expect_word("of")
                expr = self.parse_factor()
                return LowercaseOf(expr, line)

            # ── Phase 3 expression keywords ───────────────────────────────────

            # "trim X"
            if val == "trim":
                self.advance()
                expr = self.parse_factor()
                return TrimOf(expr, line)

            # "split X by Y"
            if val == "split":
                self.advance()
                source = self.parse_factor()
                self.expect_word("by")
                delim = self.parse_factor()
                return SplitBy(source, delim, line)

            # "join X with Y"
            if val == "join":
                self.advance()
                lst = self.parse_factor()
                self.expect_word("with")
                sep = self.parse_factor()
                return JoinWith(lst, sep, line)

            # "replace Y in X with Z"
            if val == "replace":
                self.advance()
                find = self.parse_factor()
                self.expect_word("in")
                source = self.parse_factor()
                self.expect_word("with")
                repl = self.parse_factor()
                return ReplaceIn(source, find, repl, line)

            # "round X" or "round X to N places"
            if val == "round":
                self.advance()
                expr = self.parse_factor()
                if self.word_is("to"):
                    self.advance()
                    places = self.parse_factor()
                    if self.word_is("places") or self.word_is("place"):
                        self.advance()
                    return RoundOf(expr, places, line)
                return RoundOf(expr, None, line)

            # "absolute value of X"
            if val == "absolute":
                self.advance()
                self.expect_word("value")
                self.expect_word("of")
                expr = self.parse_factor()
                return AbsOf(expr, line)

            # "square root of X"
            if val == "square":
                self.advance()
                self.expect_word("root")
                self.expect_word("of")
                expr = self.parse_factor()
                return SqrtOf(expr, line)

            # "floor of X"
            if val == "floor":
                self.advance()
                self.expect_word("of")
                expr = self.parse_factor()
                return FloorOf(expr, line)

            # "ceiling of X"
            if val == "ceiling":
                self.advance()
                self.expect_word("of")
                expr = self.parse_factor()
                return CeilingOf(expr, line)

            # "random number between A and B"
            if val == "random":
                self.advance()
                self.expect_word("number")
                self.expect_word("between")
                low = self.parse_factor()
                self.expect_word("and")
                high = self.parse_factor()
                return RandomBetween(low, high, line)

            # "minimum of A and B" / "maximum of A and B"
            if val == "minimum":
                self.advance()
                self.expect_word("of")
                a = self.parse_factor()
                self.expect_word("and")
                b = self.parse_factor()
                return MinOf(a, b, line)

            if val == "maximum":
                self.advance()
                self.expect_word("of")
                a = self.parse_factor()
                self.expect_word("and")
                b = self.parse_factor()
                return MaxOf(a, b, line)

            # "X to the power of N" — handled as BinOp during word-collecting
            # but we also support "power of X to N" as prefix form:
            if val == "power":
                self.advance()
                self.expect_word("of")
                base = self.parse_factor()
                self.expect_word("to")
                exp = self.parse_factor()
                return PowerOf(base, exp, line)

            # "index of X in myList"
            if val == "index":
                self.advance()
                self.expect_word("of")
                item = self.parse_factor()
                self.expect_word("in")
                lst = self.parse_factor()
                return IndexOf(item, lst, line)

            # "repeat X N times"
            if val == "repeat":
                self.advance()
                expr = self.parse_factor()
                count = self.parse_factor()
                if self.word_is("times"):
                    self.advance()
                return RepeatStr(expr, count, line)

            # "X as a number" / "X as text"
            # Handled as postfix in parse_expr via a wrapper
            # Also supported as prefix: "as a number X"
            if val == "as":
                self.advance()
                if self.word_is("a"):
                    self.advance()
                type_word = self.advance().value.lower()
                expr = self.parse_factor()
                if type_word in ("number", "numbers"):
                    return AsNumber(expr, line)
                elif type_word in ("text",):
                    return AsText(expr, line)
                else:
                    raise ParseError(f"Line {line}: After 'as' expected 'a number' or 'text'.")

            # Multi-word string / identifier collection
            STOP_WORDS = {
                "plus", "minus", "times", "divided", "modulo", "is", "equals",
                "then", "do", "following", "end", "otherwise",
                "and", "or", "with", "that", "does", "takes", "back",
                "greater", "less", "equal", "not", "than", "to",
                "result", "of", "calling", "repeat", "while", "if",
                "give", "define", "call", "ask", "say", "display", "let",
                "be", "function", "called", "user", "for", "times",
                "add", "remove", "each", "in", "from", "item", "stop", "skip",
                "containing", "length", "uppercase", "lowercase", "a", "an",
                "error", "sort", "split", "join", "replace", "trim", "round",
                "absolute", "value", "square", "root", "floor", "ceiling",
                "random", "number", "between", "minimum", "maximum", "power",
                "index", "by", "places", "place", "contains", "as",
                "dictionary", "keys", "set", "has", "exists", "json", "parsed",
                "fetching", "posting", "payload", "url", "class", "method",
                "properties", "new", "on", "parameters",
                # Phase 6
                "over", "where", "extends", "enum", "check", "when", "otherwise",
                "test", "assert", "run", "tests", "command", "arguments",
                "environment", "variable", "mapping", "filtering", "matching",
                "pattern", "gives", "function", "values",
            }

            words = [tok.value]
            self.advance()
            while self.current().type == WORD and self.current().value.lower() not in STOP_WORDS:
                words.append(self.current().value)
                self.advance()

            if len(words) == 1:
                return Identifier(words[0], line)
            return StringLiteral(" ".join(words), line)

        raise ParseError(
            f"Line {line}: I expected a value (number, word, true, false, a list, etc.) "
            f"but found '{tok.value}'."
        )

    # ── Try / Catch ────────────────────────────────────────────────────────────

    def parse_try(self) -> TryCatch:
        line = self.current().line
        self.advance()  # "Try"
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        try_body = self.parse_block(["Handle"])
        self.expect_word("Handle")
        self.expect_word("error")
        # Optional: "and save it as X"
        error_var = "error"
        if self.word_is("and"):
            self.advance()
            self.expect_word("save")
            self.expect_word("it")
            self.expect_word("as")
            error_var = self.advance().value
        self.expect_period()
        catch_body = self.parse_block(["End"])
        self.expect_word("End")
        self.expect_word("try")
        self.expect_period()
        return TryCatch(try_body, error_var, catch_body, line)

    # ── Sort List ─────────────────────────────────────────────────────────────

    def parse_sort_list(self) -> SortList:
        line = self.current().line
        self.advance()  # "Sort"
        list_tok = self.advance()
        if list_tok.type != WORD:
            raise ParseError(f"Line {line}: Expected a list variable name after 'Sort'.")
        self.expect_period()
        return SortList(list_tok.value, line)

    # ── Phase 6 Parsing Methods ────────────────────────────────────────────────

    def _parse_interpolated_string(self, raw: str, line: int) -> InterpolatedString:
        """Parse a string with {expr} interpolation into parts."""
        from lexer import Lexer as InnerLexer
        parts = []
        i = 0
        buf = []
        while i < len(raw):
            if raw[i] == '{':
                # Flush text buffer
                if buf:
                    parts.append(StringLiteral("".join(buf), line))
                    buf = []
                # Find matching closing brace
                depth = 1
                i += 1
                expr_buf = []
                while i < len(raw) and depth > 0:
                    if raw[i] == '{':
                        depth += 1
                    elif raw[i] == '}':
                        depth -= 1
                        if depth == 0:
                            break
                    expr_buf.append(raw[i])
                    i += 1
                if depth != 0:
                    raise ParseError(f"Line {line}: Unclosed '{{' in interpolated string.")
                i += 1  # skip '}'
                # Parse the expression
                expr_str = "".join(expr_buf).strip()
                if not expr_str:
                    raise ParseError(f"Line {line}: Empty interpolation {{}} in string.")
                tokens = InnerLexer(expr_str + ".").tokenize()
                mini_parser = Parser(tokens)
                expr_node = mini_parser.parse_expr()
                parts.append(expr_node)
            else:
                buf.append(raw[i])
                i += 1
        if buf:
            parts.append(StringLiteral("".join(buf), line))
        return InterpolatedString(parts, line)

    def parse_check(self) -> CheckStmt:
        """Check value. When 1, do X. When 2, do Y. Otherwise, do Z. End check."""
        line = self.current().line
        self.advance()  # "Check"
        expr = self.parse_expr()
        self.expect_period()

        cases = []
        otherwise = []
        while self.current().type != EOF:
            if self.word_is("End"):
                break
            if self.word_is("When"):
                self.advance()  # "When"
                case_val = self.parse_factor()
                self.expect(COMMA)
                # Parse body until next When/Otherwise/End
                body = []
                while self.current().type != EOF:
                    if self.word_is("When", "Otherwise", "End"):
                        break
                    stmt = self.parse_statement()
                    if stmt is not None:
                        body.append(stmt)
                cases.append((case_val, body))
            elif self.word_is("Otherwise"):
                self.advance()  # "Otherwise"
                if self.current().type == COMMA:
                    self.advance()
                # Parse body until End
                while self.current().type != EOF:
                    if self.word_is("End"):
                        break
                    stmt = self.parse_statement()
                    if stmt is not None:
                        otherwise.append(stmt)
            else:
                raise ParseError(f"Line {self.current().line}: Expected 'When', 'Otherwise', or 'End' inside Check block.")

        self.expect_word("End")
        self.expect_word("check")
        self.expect_period()
        return CheckStmt(expr, cases, otherwise, line)

    def parse_test_block(self) -> TestBlock:
        """Test 'test name'. ... End test."""
        line = self.current().line
        self.advance()  # "Test"
        name_tok = self.current()
        if name_tok.type == STRING_QUOTED or name_tok.type == INTERP_STRING:
            test_name = name_tok.value
            self.advance()
        else:
            raise ParseError(f"Line {line}: Expected a quoted test name after 'Test'.")
        self.expect_period()
        body = self.parse_block(["End"])
        self.expect_word("End")
        self.expect_word("test")
        self.expect_period()
        return TestBlock(test_name, body, line)

    def parse_assert(self) -> AssertStmt:
        """Assert CONDITION."""
        line = self.current().line
        self.advance()  # "Assert"
        cond = self.parse_condition()
        self.expect_period()
        return AssertStmt(cond, line)

    def parse_run_tests(self) -> RunTestsStmt:
        """Run all tests."""
        line = self.current().line
        self.advance()  # "Run"
        self.expect_word("all")
        self.expect_word("tests")
        self.expect_period()
        return RunTestsStmt(line)

    # ── Phase A GUI Parse Methods ─────────────────────────────────────────────

    def parse_run_dispatch(self):
        """Dispatch between 'Run all tests.' and 'Run <window>.'"""
        line = self.current().line
        self.advance()  # "Run"
        if self.word_is("all"):
            self.expect_word("all")
            self.expect_word("tests")
            self.expect_period()
            return RunTestsStmt(line)
        # Otherwise: "Run <window_expr>."
        window_expr = self.parse_expr()
        self.expect_period()
        return RunWindowStmt(window_expr, line)

    def parse_create_window(self):
        """Create a window called X with title "T" and size W by H."""
        line = self.current().line
        self.advance()  # "Create"
        self.expect_word("a")
        self.expect_word("window")
        self.expect_word("called")
        name_tok = self.advance()
        var_name = name_tok.value
        self.expect_word("with")
        self.expect_word("title")
        title_expr = self.parse_factor()
        self.expect_word("and")
        self.expect_word("size")
        width_expr = self.parse_factor()
        self.expect_word("by")
        height_expr = self.parse_factor()
        self.expect_period()
        return CreateWindowStmt(var_name, title_expr, width_expr, height_expr, line)

    def parse_add_dispatch(self):
        """Dispatch between list 'Add X to Y' and GUI 'Add a/an button/label/input ...'"""
        line = self.current().line
        # Peek: is it a GUI widget? (handles both 'Add a button' and 'Add an input')
        if self.peek_ahead().type == WORD and self.peek_ahead().value.lower() in ("a", "an"):
            saved = self.pos
            self.advance()  # "Add"
            self.advance()  # "a" or "an"
            widget_type = self.current().value.lower() if self.current().type == WORD else ""
            if widget_type in ("button", "label", "input"):
                return self.parse_add_widget(line, widget_type)
            else:
                self.pos = saved  # not a GUI widget, restore
        return self.parse_add_to_list()

    def parse_add_widget(self, line: int, widget_type: str):
        """
        Add a button "label" to <window> [at row R column C [spanning S]] [that does the following...].
        Add a label "text" to <window>.
        Add an input called <varname> to <window> [at row R column C [spanning S]].
        """
        self.advance()  # consume widget_type word
        var_name = None
        label_expr = None
        callback_body = None
        row_expr = None
        col_expr = None
        colspan_expr = None

        if widget_type == "input":
            # "Add an input called X to <window>"
            if self.word_is("called"):
                self.advance()  # "called"
                name_tok = self.advance()
                var_name = name_tok.value
        else:
            # "Add a button "label"..." or "Add a label "text"..."
            label_expr = self.parse_factor()
            # Optional variable binding: "called X"
            if self.word_is("called"):
                self.advance()
                var_name = self.advance().value

        self.expect_word("to")
        win_tok = self.advance()
        window_expr = Identifier(win_tok.value, win_tok.line)

        # Optional position: "at row R column C [spanning S columns]"
        if self.word_is("at"):
            self.advance()  # "at"
            self.expect_word("row")
            # Read a simple number or variable — don't use parse_factor which consumes too greedily
            tok = self.advance()
            row_expr = NumberLiteral(float(tok.value), tok.line) if tok.type == NUMBER else Identifier(tok.value, tok.line)
            self.expect_word("column")
            tok2 = self.advance()
            col_expr = NumberLiteral(float(tok2.value), tok2.line) if tok2.type == NUMBER else Identifier(tok2.value, tok2.line)
            if self.word_is("spanning"):
                self.advance()
                tok3 = self.advance()
                colspan_expr = NumberLiteral(float(tok3.value), tok3.line) if tok3.type == NUMBER else Identifier(tok3.value, tok3.line)
                if self.word_is("columns") or self.word_is("column"):
                    self.advance()

        # Optional inline callback: "that does the following...End button."
        if widget_type == "button" and self.word_is("that"):
            self.advance()  # "that"
            self.expect_word("does")
            self.expect_word("the")
            self.expect_word("following")
            self.expect_period()
            body = self.parse_block(["End"])
            self.advance()  # "End"
            self.expect_word("button")
            self.expect_period()
            callback_body = BlockLambda([], body, line)
        else:
            self.expect_period()

        return AddWidgetStmt(widget_type, window_expr, label_expr, var_name,
                             callback_body, row_expr, col_expr, colspan_expr, line)

    def parse_when_stmt(self):
        """
        When user presses Enter on <widget> do the following...End when.
        When user presses a key on <widget> do the following...End when.
        When window closes do the following...End when.
        When <widget> changes do the following...End when.
        """
        line = self.current().line
        self.advance()  # "When"

        event = "generic"
        widget_expr = None

        if self.word_is("user"):
            self.advance()  # "user"
            self.expect_word("presses")
            key_tok = self.advance().value.lower()  # e.g. "Enter", "a"
            if key_tok == "enter":
                event = "enter"
            elif key_tok == "escape":
                event = "escape"
            else:
                event = f"key:{key_tok}"
            if self.word_is("on"):
                self.advance()
                w = self.advance()
                widget_expr = Identifier(w.value, w.line)
        elif self.word_is("window"):
            self.advance()  # "window"
            self.expect_word("closes")
            event = "close"
        else:
            # "When <widget> changes"
            w = self.advance()
            widget_expr = Identifier(w.value, w.line)
            self.expect_word("changes")
            event = "change"

        self.expect_word("do")
        self.expect_word("the")
        self.expect_word("following")
        self.expect_period()
        body = self.parse_block(["End"])
        self.advance()  # "End"
        self.expect_word("when")
        self.expect_period()
        return WhenStmt(event, widget_expr, body, line)

    def expect(self, token_type: str):
        """Expect and consume a specific token type."""
        if self.current().type != token_type:
            raise ParseError(f"Line {self.current().line}: Expected '{token_type}' but found '{self.current().value}'.")
        return self.advance()

