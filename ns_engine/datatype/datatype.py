from dataclasses import dataclass, field
from typing import Any, Self
from ..components.position import Position
from ..components.context import Context

@dataclass(slots=True)
class Datatype:
    value: Any
    
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)
    context: Context = field(default=None, init=False)
    
    def set_pos(self, pos_start: Position = None, pos_end: Position = None) -> Self:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
        
    def set_context(self, context: Context) -> Self:
        self.context = context
        return self
    
    def added_to(self, other: Self) -> Self: pass
    def subtracted_by(self, other: Self) -> Self: pass
    def multiplied_by(self, other: Self) -> Self: pass
    def divided_by(self, other: Self) -> Self: pass
    def powered_by(self, other: Self) -> Self: pass
    def is_equal_to(self, other: Self) -> Self: pass
    def is_not_equal_to(self, other: Self) -> Self: pass
    def is_less_than(self, other: Self) -> Self: pass
    def is_greater_than(self, other: Self) -> Self: pass
    def is_less_equal_than(self, other: Self) -> Self: pass
    def is_greater_equal_than(self, other: Self) -> Self: pass
    def and_with(self, other: Self) -> Self:  pass
    def or_with(self, other: Self) -> Self: pass
    def notted(self) -> Self: pass
    
    def copy(self) -> Self:
        copy = type(self)(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    