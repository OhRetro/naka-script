from dataclasses import dataclass, field
from .position import Position

@dataclass(frozen=True, slots=True)
class Error:
    name: str
    details: str
    pos_start: Position
    pos_end: Position
    
    def as_string(self):
        message = f"{self.name}: {self.details}"
        message += f"\nFile {self.pos_start.filename}, line {self.pos_start.line + 1}"
        return message

@dataclass(frozen=True, slots=True)
class ErrorIllegalCharacter(Error):
    name: str = field(default="Illegal Character Error", init=False)
