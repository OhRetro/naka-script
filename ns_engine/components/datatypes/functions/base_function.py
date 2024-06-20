from dataclasses import dataclass, field
from typing import Never
from ..datatype import Datatype
from ns_engine.components.errors import NSRuntimeError
from ns_engine.components.runtime import RuntimeResult
from ns_engine.components.context import Context

@dataclass(slots=True)
class BaseFunction(Datatype):
    value: Never = field(default=None, init=False)
    name: str

    def __post_init__(self):
        self._values_to_copy = ("name", )

    def generate_new_context(self) -> Context:
        from ns_engine.components.symbol_table import SymbolTable

        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        
        return new_context
    
    def check_args(self, arg_names: list[str], args: list[Datatype]):
        rt_result = RuntimeResult()
        
        if len(args) > len(arg_names):
            return rt_result.failure(NSRuntimeError(
                f"{len(args) - len(arg_names)} too many arguments passed into '{self.name}'",
                self.pos_start, self.pos_end, self.context
            ))
            
        elif len(args) < len(arg_names):
            return rt_result.failure(NSRuntimeError(
                f"{len(arg_names) - len(args)} too few arguments passed into '{self.name}'",
                self.pos_start, self.pos_end, self.context
            ))
            
        return rt_result.success(None)
    
    def populate_args(self, arg_names: list[str], args: list[Datatype], context: Context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(context)
            context.symbol_table.set(arg_name, arg_value, "symbols")

    def check_populate_args(self, arg_names: list[str], args: list[Datatype], context: Context):
        rt_result = RuntimeResult()
        rt_result.register(self.check_args(arg_names, args))
        if rt_result.should_return(): return rt_result
        self.populate_args(arg_names, args, context)
        return rt_result.success(None)
