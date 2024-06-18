from dataclasses import dataclass
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from ..components.error import ErrorRuntime

@dataclass(slots=True)
class List(Datatype):
    value: list[Datatype]

    def __post_init__(self):
        self._values_to_copy = ("value", )

    # def __str__(self) -> str:
    #     return self._elements_str()

    def __repr__(self) -> str:
        return f"[{self._elements_repr()}]"
    
    # def _elements_str(self):
    #     return ", ".join([str(x) for x in self.value])

    def _elements_repr(self):
        return ", ".join([repr(x) for x in self.value])
    
    def _number(self, value: int | float) -> DATATYPE_OR_ERROR:
        return Number(value).set_context(self.context), None

    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self._number(int(value))

    def update_index_at(self, other: Datatype, new: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                self.value[other.value] = new
                return None, None
            except IndexError:
                return None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return None, ErrorRuntime(
                "'List' datatype can be only indexed by 'Number: int'",
                other.pos_start, other.pos_end, self.context
            )
    
    def index_at(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                return self.value[other.value], None
            except IndexError:
                return None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return None, ErrorRuntime(
                "'List' datatype can be only indexed by 'Number: int'",
                other.pos_start, other.pos_end, self.context
            )
            
    def added_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        self.value.append(other)
        return None, None
    
    def subtracted_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Number):
            try:
                self.value.pop(other.value)
                return None, None
            except IndexError:
                None, ErrorRuntime(
                    "Element at index doesn't exist, Out of bounds",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return self._illegal_operation(other)
    
    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, List):
            self.value.extend(other.value)
            return None, None
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
        
    def is_true(self) -> bool:
        return self.value != []
    