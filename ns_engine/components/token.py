from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .position import Position
from .keyword import Keyword

class TokenType(Enum):
    def __repr__(self) -> str:
        return f"TokenType({self.name})"
    
    # General types
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    EQUALS = "="
    
    # Data types
    INT = "int" # unused
    FLOAT = "float" # unused
    
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
    ISNULL = "?=" # unused
    
    # Other
    DOT = "." # unused
    COMMA = ","
    RIGHTARROW = "->"
    LEFTARROW = "<-" # unused
    SEMICOLON = ";"
    COLON = ":"
    AT = "@" # unused
    AND = "&" # unused
    PIPE = "|" # unused
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
    
    def is_type_of(self, *types: TokenType) -> bool:
        return self.type in types
    
    def is_keyword_of(self, *keywords: Keyword) -> bool:
        return self.is_type_of(TokenType.KEYWORD) and self.value in keywords
    