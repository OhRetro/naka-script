from dataclasses import dataclass
from typing import Self
from .datatype import Datatype

@dataclass(slots=True)
class Number(Datatype):
    def __repr__(self) -> str:
        return str(self.value)
    
    def added_to(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value + other.value)
            
    def subtracted_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value - other.value)
            
    def multiplied_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value * other.value)
            
    def divided_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value / other.value)
    