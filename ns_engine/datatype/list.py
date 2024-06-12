from dataclasses import dataclass
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from ..components.error import ErrorRuntime

@dataclass(slots=True)
class List(Datatype):
    value: list[Datatype]

    def __post_init__(self):
        self._values_to_copy = ("value", )

    def __str__(self) -> str:
        return self._elements_string()

    def __repr__(self) -> str:
        return f"[{self._elements_string()}]"
    
    def _elements_string(self):
        return ", ".join([str(x) for x in self.value])
    
    def _number(self, value: int | float) -> DATATYPE_OR_ERROR:
        return Number(value).set_context(self.context), None

    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self._number(int(value))

    def added_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        result: list = self._value_copy()
        result.append(other)
        return self._new(result)
    
    def subtracted_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            result: list = self._value_copy()
            
            try:
                result.pop(other.value)
                return self._new(result)
            except IndexError:
                None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return self._illegal_operation(other)
    
    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, List):
            result: list = self._value_copy()
            result.extend(other.value)
            return self._new(result)
        else:
            return self._illegal_operation(other)
    
    def divided_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                return self.value[other.value], None
            except IndexError:
                return None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
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
        return self._number(1 if self.value == [] else 0)

    def indexing_on(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                return self.value[other.value], None
            except IndexError:
                return None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return self._illegal_operation(other)
        
    def is_true(self) -> bool:
        return self.value != []
    