"""
prose Language Lexer — Phase 6
Tokenizes prose source code.
Allowed punctuation: , and .
Math symbols: + - * / % = < > <= >= !=
Comments: any line starting with 'Note:' is ignored.
Inline comments: --- or // skip to end of line.
String interpolation: {expr} inside "..." strings.
"""

from dataclasses import dataclass
from typing import List


# ─── Token Types ───────────────────────────────────────────────────────────────

WORD          = "WORD"
NUMBER        = "NUMBER"
COMMA         = "COMMA"
PERIOD        = "PERIOD"
COLON         = "COLON"
LBRACE        = "LBRACE"
RBRACE        = "RBRACE"
STRING_QUOTED = "STRING_QUOTED"
INTERP_STRING = "INTERP_STRING"  # string with {expr} interpolation
EOF           = "EOF"

# Math symbol tokens
PLUS   = "PLUS"    # +
MINUS  = "MINUS"   # -
STAR   = "STAR"    # *
SLASH  = "SLASH"   # /
PERCENT = "PERCENT" # %
EQ     = "EQ"      # =
NEQ    = "NEQ"     # !=
LTE    = "LTE"     # <=
GTE    = "GTE"     # >=
LT     = "LT"      # <
GT     = "GT"      # >


@dataclass
class Token:
    type: str
    value: str
    line: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


# ─── Lexer ─────────────────────────────────────────────────────────────────────

class LexerError(Exception):
    pass


def strip_comments(source: str) -> str:
    """
    Remove comment lines. A comment is any line whose first non-whitespace
    content begins with 'Note:' (case-insensitive).
    """
    lines = []
    for line in source.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.lower().startswith("note:"):
            # Replace with an empty line to preserve line numbers
            lines.append("\n")
        else:
            lines.append(line)
    return "".join(lines)


class Lexer:
    def __init__(self, source: str):
        self.source = strip_comments(source)
        self.pos = 0
        self.line = 1

    def error(self, ch: str):
        raise LexerError(
            f"I am sorry, but I do not understand the character {ch!r} on line {self.line}. "
            f"prose allows letters, digits, spaces, quotes, commas, periods, colons, and math symbols (+ - * / % = < > !)."
        )

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in " \t\r\n":
            self.advance()

    def read_number(self) -> Token:
        start_line = self.line
        buf = []
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == "."):
            ch = self.source[self.pos]
            if ch == ".":
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
                    buf.append(ch)
                    self.pos += 1
                else:
                    break
            else:
                buf.append(ch)
                self.pos += 1
        return Token(NUMBER, "".join(buf), start_line)

    def read_word(self) -> Token:
        start_line = self.line
        buf = [self.source[self.pos]]
        self.pos += 1
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            buf.append(self.source[self.pos])
            self.pos += 1
        return Token(WORD, "".join(buf), start_line)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.source[self.pos]

            if ch == ".":
                if self.pos + 2 < len(self.source) and self.source[self.pos + 1] == "." and self.source[self.pos + 2] == ".":
                    self.pos += 3
                    continue
                tokens.append(Token(PERIOD, ".", self.line)); self.pos += 1
            elif ch == ",":
                tokens.append(Token(COMMA, ",", self.line)); self.pos += 1
            elif ch == ":":
                tokens.append(Token(COLON, ":", self.line)); self.pos += 1
            elif ch == "{":
                tokens.append(Token(LBRACE, "{", self.line)); self.pos += 1
            elif ch == "}":
                tokens.append(Token(RBRACE, "}", self.line)); self.pos += 1
            elif ch == '"':
                start_line = self.line
                self.pos += 1
                buf = []
                has_interp = False
                while self.pos < len(self.source):
                    c = self.source[self.pos]
                    if c == '"':
                        break
                    if c == '\\' and self.pos + 1 < len(self.source):
                        nxt = self.source[self.pos + 1]
                        if nxt == 'n':
                            buf.append('\n'); self.pos += 2; continue
                        elif nxt == 't':
                            buf.append('\t'); self.pos += 2; continue
                        elif nxt == '{':
                            buf.append('{'); self.pos += 2; continue
                        elif nxt == '"':
                            buf.append('"'); self.pos += 2; continue
                        elif nxt == '\\':
                            buf.append('\\'); self.pos += 2; continue
                    if c == '{':
                        has_interp = True
                    buf.append(c)
                    if c == '\n':
                        self.line += 1
                    self.pos += 1
                if self.pos >= len(self.source):
                    raise LexerError(f"Line {start_line}: Unclosed string.")
                self.pos += 1 # Consume closing quote
                raw = "".join(buf)
                if has_interp:
                    tokens.append(Token(INTERP_STRING, raw, start_line))
                else:
                    tokens.append(Token(STRING_QUOTED, raw, start_line))
            elif ch == "+":
                tokens.append(Token(PLUS, "+", self.line)); self.pos += 1
            elif ch == "-":
                # Check for inline comment ---
                if self.pos + 2 < len(self.source) and self.source[self.pos+1] == '-' and self.source[self.pos+2] == '-':
                    # Skip to end of line
                    while self.pos < len(self.source) and self.source[self.pos] != '\n':
                        self.pos += 1
                else:
                    tokens.append(Token(MINUS, "-", self.line)); self.pos += 1
            elif ch == "*":
                tokens.append(Token(STAR, "*", self.line)); self.pos += 1
            elif ch == "/":
                # Check for inline comment //
                if self.pos + 1 < len(self.source) and self.source[self.pos+1] == '/':
                    while self.pos < len(self.source) and self.source[self.pos] != '\n':
                        self.pos += 1
                else:
                    tokens.append(Token(SLASH, "/", self.line)); self.pos += 1
            elif ch == "%":
                tokens.append(Token(PERCENT, "%", self.line)); self.pos += 1
            elif ch == "!":
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                    tokens.append(Token(NEQ, "!=", self.line)); self.pos += 2
                else:
                    self.error(ch)
            elif ch == "<":
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                    tokens.append(Token(LTE, "<=", self.line)); self.pos += 2
                else:
                    tokens.append(Token(LT, "<", self.line)); self.pos += 1
            elif ch == ">":
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                    tokens.append(Token(GTE, ">=", self.line)); self.pos += 2
                else:
                    tokens.append(Token(GT, ">", self.line)); self.pos += 1
            elif ch == "=":
                tokens.append(Token(EQ, "=", self.line)); self.pos += 1
            elif ch.isdigit():
                tokens.append(self.read_number())
            elif ch.isalpha() or ch == "_":
                tokens.append(self.read_word())
            else:
                self.error(ch)

        tokens.append(Token(EOF, "", self.line))
        return tokens
