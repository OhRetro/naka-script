from dataclasses import dataclass, field
from .position import Position
from .context import Context
from ..utils.string_with_arrows import string_with_arrows

@dataclass(frozen=True, slots=True)
class Error:
    name: str
    details: str
    pos_start: Position
    pos_end: Position
    
    def __repr__(self) -> str:
        return f"Error({self.name}, {self.pos_start}, {self.pos_end}, \"{self.details}\")"
    
    def as_string(self) -> str:
        message = f"File \"{self.pos_start.filename}\", line {self.pos_start.line + 1}\n"
        message += f"{self.name}: {self.details}\n"
        message += f"\n{string_with_arrows(self.pos_start.filedata, self.pos_start, self.pos_end)}"
        return message

@dataclass(frozen=True, slots=True)
class NSIllegalCharacterError(Error):
    name: str = field(default="Illegal Character Error", init=False)

    def __repr__(self) -> str:
        return f"ErrorIllegalCharacter({self.pos_start}, {self.pos_end}, \"{self.details}\")"
    
@dataclass(frozen=True, slots=True)
class NSExpectedCharacterError(Error):
    name: str = field(default="Expected Character Error", init=False)

    def __repr__(self) -> str:
        return f"ErrorExpectedCharacter({self.pos_start}, {self.pos_end}, \"{self.details}\")"
    
@dataclass(frozen=True, slots=True)
class NSInvalidSyntaxError(Error):
    name: str = field(default="Invalid Syntax Error", init=False)

    def __repr__(self) -> str:
        return f"ErrorInvalidSyntax({self.pos_start}, {self.pos_end}, \"{self.details}\")"
    
@dataclass(frozen=True, slots=True)
class NSRuntimeError(Error):
    name: str = field(default="Runtime Error", init=False)
    context: Context

    def __repr__(self) -> str:
        return f"ErrorRuntime({self.pos_start}, {self.pos_end}, \"{self.details}\")"
     
    def as_string(self) -> str:
        message = self.generate_traceback()
        message += f"{self.name}: {self.details}\n"
        message += f"\n{string_with_arrows(self.pos_start.filedata, self.pos_start, self.pos_end)}"
        return message
    
    def generate_traceback(self) -> str:
        traceback_string = ""
        pos = self.pos_start
        ctx = self.context
        
        while ctx:
            traceback_string = f"    File {pos.filename}, line {pos.line + 1}, in {ctx.name}\n" + traceback_string
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
            
        return "Traceback (most recent call last):\n" + traceback_string
    