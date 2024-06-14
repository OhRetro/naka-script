from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .position import Position

class TokenType(Enum):
    def __repr__(self) -> str:
        return f"TokenType({self.name})"
    
    # General types
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    EQUALS = "="
    
    # Data types
    INT = "int"
    FLOAT = "float"
    
    NUMBER = "number"
    STRING = "string"
    
    # Mathmatic types
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    POWER = "**"
    DIV = "/"
    MOD = "%"
    
    # Parenthesis, Square and Brace
    LPAREN = "("
    RPAREN = ")"
    LSQUARE = "["
    RSQUARE = "]"
    LBRACE = "{"
    RBRACE = "}"
    
    # Conditional types
    ISEQUALS = "=="
    NE = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    ISNULL = "?=" # Yet Unused
    
    # Other
    DOT = "."
    COMMA = ","
    RIGHTARROW = "->"
    LEFTARROW = "<-"
    SEMICOLON = ";"
    COLON = ":"
    AT = "@"
    AND = "&"
    PIPE = "|"
    COMMENT = "#"
    
    NEWLINE = "newline"
    
    EOF = "EOF"

@dataclass(slots=True)
class Token:
    type: TokenType
    value: Any = field(default=None)
    pos_start: Position = field(default=None)
    pos_end: Position = field(default=None)
    
    def __post_init__(self):
        if self.pos_start:
            self.pos_start = self.pos_start.copy()
            if not self.pos_end:
                self.pos_end = self.pos_start.copy()
                self.pos_end.advance()
    
    def __repr__(self) -> str:
        if self.value:
            return f"Token({self.type.name}, {self.value})"
        else:
            return f"Token({self.type.name})"
    