from enum import Enum

class Keyword(Enum):
    def __repr__(self) -> str:
        return f"Keyword({self.name}: \"{self.value}\")"
    
    # Variables and Methods/Functions
    SETVAR = "var"
    SETIMMUTABLEVAR = "const"
    SETFUNCTION = "func"
    SETCLASS = "class" # unused
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
    END = "end"
    RETURN = "return"
    SELFREF = "inst" # unused
    