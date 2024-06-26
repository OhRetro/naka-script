from dataclasses import dataclass
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from ..errors import NSRuntimeError

@dataclass(slots=True)
class String(Datatype):
    value: str
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f'"{self.value}"'
    
    def _number(self, value: int | float) -> DATATYPE_OR_ERROR:
        return Number(value).set_context(self.context), None

    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self._number(int(value))

    def index_at(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                return self.new(self.value[other.value])
            except IndexError:
                return None, NSRuntimeError(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return None, NSRuntimeError(
                "'String' datatype can be only indexed by 'Number: int'",
                other.pos_start, other.pos_end, self.context
            )
            
    def added_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, String):
            result = self.value + other.value
            return self.new(result)
        else:
            return self._illegal_operation(other)

    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            result = self.value * other.value
            return self.new(result)
        else:
            return self._illegal_operation(other)
        
    def is_equal_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value == other.value)
    
    def is_not_equal_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value != other.value)
     
    def and_with(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value and other.value)
    
    def or_with(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value or other.value)
    
    def notted(self) -> DATATYPE_OR_ERROR:
        return self._number(1 if self.value == "" else 0)
        
    def is_true(self) -> bool:
        return self.value != ""
    