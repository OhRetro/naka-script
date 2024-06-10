from dataclasses import dataclass, field
from typing import Any, Self, Tuple, Optional
from ..components.position import Position
from ..components.context import Context
from ..components.error import Error, ErrorRuntime

@dataclass(slots=True)
class Datatype:
    value: Any
    
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)
    context: Context = field(default=None, init=False)
    
    def _illegal_operation(self, other: Self = None) -> Tuple[None, ErrorRuntime]:
        other = other or self
        
        return None, ErrorRuntime(
            "Illegal operation",
            self.pos_start, other.pos_end, self.context
            )
        
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
        
        copy = type(self)(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
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
