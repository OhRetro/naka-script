from dataclasses import dataclass
from typing import Self
from .datatype import Datatype
from ..components.error import ErrorRuntime
from ..utils.strings_template import DIVISION_BY_ZERO_ERROR

@dataclass(slots=True)
class Number(Datatype):
    def __repr__(self) -> str:
        return str(self.value)
    
    def added_to(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
            
    def subtracted_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
            
    def multiplied_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
            
    def divided_by(self, other: Datatype) -> Self:
        if isinstance(other, Number):
            if other.value == 0:
                return None, ErrorRuntime(
                    DIVISION_BY_ZERO_ERROR,
                    other.pos_start, other.pos_end, self.context
                )
                
            return Number(self.value / other.value).set_context(self.context), None
    