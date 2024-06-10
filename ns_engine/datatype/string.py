from dataclasses import dataclass
from typing import Self
from .datatype import Datatype, DATATYPE_OR_ERROR
from .datatypes import Number

@dataclass(slots=True)
class String(Datatype):
    value: str
    
    def __repr__(self) -> str:
        return str(self.value)
    
    def _number(self, value: int | float) -> DATATYPE_OR_ERROR:
        return Number(value).set_context(self.context), None

    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self._number(int(value))

    def added_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, String):
            result = self.value + other.value
            return self._new(result)
        else:
            return self._illegal_operation(other)

    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            result = self.value * other.value
            return self._new(result)
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
    