from dataclasses import dataclass
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from .string import String
from ..error import ErrorRuntime

@dataclass(slots=True)
class Dict(Datatype):
    value: dict[str, Datatype]

    def __repr__(self) -> str:
        display = ""

        for index, (k, v) in enumerate(self.value.items()):
            display += f"{k}: {repr(v)}" + (", " if index < len(self.value) - 1 and len(self.value) > 1 else "")
        
        return f"{{{display}}}"
    
    def _number(self, value: int | float) -> DATATYPE_OR_ERROR:
        return Number(value).set_context(self.context), None

    def _number_bool(self, value: bool) -> DATATYPE_OR_ERROR:
        return self._number(int(value))

    def index_at(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, String):
            try:
                return self.value[other.value], None
            except KeyError:
                return None, ErrorRuntime(
                    f"Key '{other.value}' doesn't exist",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return None, ErrorRuntime(
                "'Dict' datatype can be only indexed by 'String'",
                other.pos_start, other.pos_end, self.context
            )
    
    def update_index_at(self, other: Datatype, new: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, String):
            self.value[other.value] = new
            return None, None
        else:
            return None, ErrorRuntime(
                "'Dict' datatype can be only indexed by 'String'",
                other.pos_start, other.pos_end, self.context
            )
    
    def subtracted_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, String):
            try:
                del self.value[other.value]
                return None, None
            except KeyError:
                None, ErrorRuntime(
                    f"Key '{other.value}' doesn't exist",
                    other.pos_start, other.pos_end, self.context
                )
        else:
            return self._illegal_operation(other)
    
    def multiplied_by(self, other: Datatype) -> DATATYPE_OR_ERROR:
        if isinstance(other, Dict):
            self.value.update(other.value)
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
        return self._number(1 if self.value == {} else 0)

    def is_true(self) -> bool:
        return self.value != {}
    