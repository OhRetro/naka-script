from dataclasses import dataclass
from .datatype import Datatype, DATATYPE_OR_ERROR
from ..error import ErrorRuntime

@dataclass(slots=True)
class Number(Datatype):
    value: int | float
    
    def __repr__(self) -> str:
        return str(self.value)
    
    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self.new(int(value))

    def _clone(self, other: Datatype, operation: str) -> DATATYPE_OR_ERROR:
        OPERATIONS = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "**": lambda a, b: a ** b,
            "%": lambda a, b: a % b,
        }

        if isinstance(other, Number):
            try:
                result = OPERATIONS[operation](self.value, other.value)
                return self.new(result)
            except ZeroDivisionError:
                return None, ErrorRuntime(
                    "Division by zero",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return self._illegal_operation(other)

    def added_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "+")

    def subtracted_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "-")
        
    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "*")
        
    def divided_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "/")
        
    def powered_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "**")

    def modulo_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._clone(other, "%")
          
    def is_equal_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value == other.value)
    
    def is_not_equal_to(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value != other.value)
    
    def is_less_than(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value < other.value)
    
    def is_greater_than(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value > other.value)
    
    def is_less_equal_than(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value <= other.value)
    
    def is_greater_equal_than(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value >= other.value)
    
    def and_with(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value and other.value)
    
    def or_with(self, other: Datatype) -> DATATYPE_OR_ERROR:
        return self._number_bool(self.value or other.value)
    
    def notted(self) -> DATATYPE_OR_ERROR:
        return self.new(1 if self.value == 0 else 0)

    def is_true(self) -> bool:
        return self.value != 0
    
Number.null = Number(-1)
Number.true = Number(1)
Number.false = Number(0)
