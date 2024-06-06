from dataclasses import dataclass, field
from .position import Position
from ..utils.string_with_arrows import string_with_arrows

@dataclass(frozen=True, slots=True)
class Error:
    name: str
    details: str
    pos_start: Position
    pos_end: Position
    
    def as_string(self):
        message = f"{self.name}: {self.details}"
        message += f"\nFile {self.pos_start.filename}, line {self.pos_start.line + 1}"
        message += f"\n\n{string_with_arrows(self.pos_start.filedata, self.pos_start, self.pos_end)}"
        return message

@dataclass(frozen=True, slots=True)
class ErrorIllegalCharacter(Error):
    name: str = field(default="Illegal Character Error", init=False)

@dataclass(frozen=True, slots=True)
class ErrorInvalidSyntax(Error):
    name: str = field(default="Invalid Syntax Error", init=False)