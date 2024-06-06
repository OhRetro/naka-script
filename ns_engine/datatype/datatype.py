from dataclasses import dataclass, field
from typing import Any, Self
from ..components.position import Position

@dataclass(slots=True)
class Datatype:
    value: Any
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)
    
    def __post_init__(self):
        self.set_pos()

    def __repr__(self) -> str:
        return str(self.value)
    
    def set_pos(self, pos_start: Position = None, pos_end: Position = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        
    def added_to(self, other: Self) -> Self:
        pass
            
    def subtracted_by(self, other: Self) -> Self:
        pass
            
    def multiplied_by(self, other: Self) -> Self:
        pass
            
    def divided_by(self, other: Self) -> Self:
        pass
    