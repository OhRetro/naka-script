from dataclasses import dataclass
from typing import Self
from .datatype import Datatype
from ..components.error import ErrorRuntime
from ..utils.strings_template import DIVISION_BY_ZERO_ERROR

@dataclass(slots=True)
class Number(Datatype):
    value: int | float
    
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
        
    def powered_by(self, other: Self) -> Self:
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def modulo_by(self, other: Self) -> Self:
        if isinstance(other, Number):
            return Number(self.value % other.value).set_context(self.context), None
          
    def is_equal_to(self, other: Self) -> Self:
        return Number(int(self.value == other.value)).set_context(self.context), None
    
    def is_not_equal_to(self, other: Self) -> Self:
        return Number(int(self.value != other.value)).set_context(self.context), None
    
    def is_less_than(self, other: Self) -> Self:
        return Number(int(self.value < other.value)).set_context(self.context), None
    
    def is_greater_than(self, other: Self) -> Self:
        return Number(int(self.value > other.value)).set_context(self.context), None
    
    def is_less_equal_than(self, other: Self) -> Self:
        return Number(int(self.value <= other.value)).set_context(self.context), None
    
    def is_greater_equal_than(self, other: Self) -> Self:
        return Number(int(self.value >= other.value)).set_context(self.context), None
    
    def and_with(self, other: Self) -> Self:
        return Number(int(self.value and other.value)).set_context(self.context), None
    
    def or_with(self, other: Self) -> Self:
        return Number(int(self.value or other.value)).set_context(self.context), None
    
    def notted(self) -> Self:
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    