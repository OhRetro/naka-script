from enum import Enum

class Keyword(Enum):
    def __repr__(self) -> str:
        return f"Keyword({self.name})"
    
    # Variables and Methods/Functions
    SETVAR = "var"
    SETIMMUTABLEVAR = "const"
    SETSCOPEDVAR = "local"
    SETFUNCTION = "func"
    SETCLASS = "class"
    DELETEVAR = "delvar"
      
    # Conditional
    AND = "and"
    OR = "or"
    NOT = "not"
    IF = "if"
    ELSEIF = "elseif"
    ELSE = "else"
    IS = "is"
    THEN = "then"
    
    # Loops
    FOR = "for"
    TO = "to"
    STEP = "step"
    WHILE = "while"
    
    CONTINUE = "continue"
    BREAK = "break"
    
    # Other
    RETURN = "return"
    SELFREF = "self"
    