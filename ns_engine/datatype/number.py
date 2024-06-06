from dataclasses import dataclass
from typing import Self
from .datatype import Datatype

@dataclass(slots=True)
class Number(Datatype):
    def added_to(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value + other.value), None
            
    def subtracted_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value - other.value), None
            
    def multiplied_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value * other.value), None
            
    def divided_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value / other.value), None
    