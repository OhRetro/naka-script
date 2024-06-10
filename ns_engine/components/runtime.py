from dataclasses import dataclass, field
from typing import Self, TypeVar
from .error import Error
#from ..datatype.datatypes import Datatype

Datatype = TypeVar("Datatype")

@dataclass(slots=True)
class RuntimeResult:
    value: Datatype = field(default=None, init=False)
    error: Error = field(default=None, init=False)
    
    def register(self, result: Self) -> Datatype:
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value: Datatype) -> Self:
        self.value = value
        return self
    
    def failure(self, error: Error) -> Self:
        self.error = error
        return self
    