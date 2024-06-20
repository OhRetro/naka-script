from dataclasses import dataclass, field
from typing import Self, TypeVar, TYPE_CHECKING
from .errors import Error

if TYPE_CHECKING:
    from .datatypes import Datatype
else:
    Datatype = TypeVar("Datatype")

@dataclass(slots=True)
class RuntimeResult:
    value: Datatype = field(default=None, init=False)
    func_return_value: Datatype = field(default=None, init=False)
    error: Error = field(default=None, init=False)
    loop_should_continue: bool = field(default=False, init=False)
    loop_should_break: bool = field(default=False, init=False)

    def reset(self) -> None:
        self.value = None
        self.func_return_value = None
        self.error = None
        self.loop_should_continue = False
        self.loop_should_break = False
        
    def register(self, result: Self) -> Datatype:
        self.error = result.error
        self.func_return_value = result.func_return_value
        self.loop_should_continue = result.loop_should_continue
        self.loop_should_break = result.loop_should_break
        
        return result.value
    
    def success(self, value: Datatype) -> Self:
        self.reset()
        self.value = value
        return self

    def success_return(self, value: Datatype) -> Self:
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self) -> Self:
        self.reset()
        self.loop_should_continue = True
        return self
    
    def success_break(self) -> Self:
        self.reset()
        self.loop_should_break = True
        return self
 
    def failure(self, error: Error) -> Self:
        self.reset()
        self.error = error
        return self
    
    def should_return(self) -> bool:
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )
        
    def an_error_occurred(self) -> bool:
        return self.should_return() and not self.loop_should_continue and not self.loop_should_break
    