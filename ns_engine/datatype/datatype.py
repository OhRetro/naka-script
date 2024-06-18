from dataclasses import dataclass, field
from typing import Any, Self, Tuple, Optional
from copy import deepcopy
from ..components.position import Position
from ..components.context import Context
from ..components.error import Error, ErrorRuntime

@dataclass(slots=True)
class Datatype:
    value: Any
    
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)
    context: Context = field(default=None, init=False)
    
    _values_to_copy: Tuple[str] = field(default=None, init=False)
    
    def _value_copy(self) -> Any:
        return deepcopy(self.value)
        
    def _illegal_operation(self, other: Self = None) -> Tuple[None, ErrorRuntime]:
        other = other or self
        
        return None, ErrorRuntime(
            "Illegal operation",
            self.pos_start, other.pos_end, self.context
            )
        
    def new(self, value: Any) -> Tuple[Self, None]:
        return type(self)(value).set_context(self.context), None
    
    def set_pos(self, pos_start: Position = None, pos_end: Position = None) -> Self:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
        
    def set_context(self, context: Context) -> Self:
        self.context = context
        return self
    
    def copy(self) -> Self:
        if type(self).__name__ == "Datatype":
            raise Exception("Cannot copy pure Datatype, only defined")
        
        values_to_copy = self._values_to_copy or ("value", )
        _temp = []
        for value in values_to_copy:
            if value.startswith(":"):
                _temp.append(getattr(self, value.removeprefix(":"))[:])
            else:
                _temp.append(getattr(self, value))
                
        values_to_copy = tuple(_temp)
        del _temp
        
        copy = type(self)(*values_to_copy)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def index_at(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def access_at(self, attribute_name: str) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation()

    def update_index_at(self, other: Self, new: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)
 
    def update_access_at(self, attribute_name: str, new: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation()
    
    def added_to(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def subtracted_by(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def multiplied_by(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def divided_by(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def powered_by(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def modulo_by(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_equal_to(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_not_equal_to(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_less_than(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_greater_than(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_less_equal_than(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def is_greater_equal_than(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def and_with(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def or_with(self, other: Self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation(other)

    def notted(self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation()
    
    def execute(self) -> Tuple[Optional[Self], Optional[Error]]:
        return self._illegal_operation()
    
    def is_true(self) -> bool:
        return False
    
DATATYPE_OR_ERROR = Tuple[Optional[Datatype], Optional[Error]]
