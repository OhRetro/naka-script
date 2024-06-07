from enum import Enum

class Keyword(Enum):
    # Variables and Methods/Functions
    SETVAR = "var"
    SETIMMUTABLEVAR = "const"
    SETSCOPEDVAR = "local"
    SETFUNCTION = "func"
    SETCLASS = "class"
      
    # Conditional
    AND = "and"
    OR = "or"
    NOT = "not"
    IF = "if"
    ELSEIF = "elseif"
    ELSE = "else"
    IS = "is"
    
    # Loops
    FOR = "for"
    WHILE = "while"
    CONTINUE = "continue"
    BREAK = "break"
    
    # Other
    RETURN = "return"
    SELFREF = "self"
    