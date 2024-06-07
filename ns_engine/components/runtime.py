from dataclasses import dataclass, field
from typing import Any, Self
from .error import Error
from ..datatype.datatypes import Datatype

@dataclass(slots=True)
class RuntimeResult:
    value: Any = field(default=None)
    error: Error = field(default=None)
    
    def register(self, result: Self) -> Datatype:
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value: Datatype) -> Self:
        self.value = value
        return self
    
    def failure(self, error: Error) -> Self:
        self.error = error
        return self
    