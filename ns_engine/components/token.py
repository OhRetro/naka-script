from enum import Enum
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    # General types
    KEYWORD = None # "keyword"
    IDENTIFIER = None # "identifier"
    EQUALS = "="
    
    # Data types
    INT = None # "int"
    FLOAT = None # "float"
    
    NUMBER = None # "number"
    STRING = '"'
    
    # Mathmatic types
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    POWER = "**"
    DIV = "/"
    DIVREST = "%"
    
    # Parenthesis, Square and Brace
    LPAREN = "("
    RPAREN = ")"
    LSQUARE = "["
    RSQUARE = "]"
    LBRACE = "{"
    RBRACE = "}"
    
    # Conditional types
    EE = "=="
    NE = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    ISNULL = "?=" # Yet Unused
    
    # Other
    DOT = "."
    COMMA = ","
    ARROW = "->"
    SEMICOLON = ";"
    COLON = ":"
    NEWLINE = "\n"
    COMMENT = "#"
    COMMENTBLOCK = "###"
    
    EOF = None # "EOF"

@dataclass()
class Token:
    type: TokenType
    value: Any = None
    