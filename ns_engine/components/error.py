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
        return f"Error({self.name}, {self.details})"
    
    def as_string(self) -> str:
        message = f"File {self.pos_start.filename}, line {self.pos_start.line + 1}\n"
        message += f"{self.name}: {self.details}\n"
        message += f"\n{string_with_arrows(self.pos_start.filedata, self.pos_start, self.pos_end)}"
        return message

@dataclass(frozen=True, slots=True)
class ErrorIllegalCharacter(Error):
    name: str = field(default="Illegal Character Error", init=False)

@dataclass(frozen=True, slots=True)
class ErrorExpectedCharacter(Error):
    name: str = field(default="Expected Character Error", init=False)
    
@dataclass(frozen=True, slots=True)
class ErrorInvalidSyntax(Error):
    name: str = field(default="Invalid Syntax Error", init=False)

@dataclass(frozen=True, slots=True)
class ErrorIllegalOperation(Error):
    name: str = field(default="Illegal Operation Error", init=False)
    
@dataclass(frozen=True, slots=True)
class ErrorRuntime(Error):
    name: str = field(default="Runtime Error", init=False)
    context: Context
    
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
    