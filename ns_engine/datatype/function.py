from dataclasses import dataclass, field
from typing import Self, Never
from .datatype import Datatype, DATATYPE_OR_ERROR
from ..components.error import ErrorRuntime
from ..components.node import Node
# from ..components.runtime import RuntimeResult
# from ..components.interpreter import Interpreter
# from ..components.context import Context
# from ..components.symbol_table import SymbolTable


@dataclass(slots=True)
class Function(Datatype):
    value: Never = field(default=None, init=False)
    name: str
    body_node: Node
    arg_names: list
    
    def __repr__(self) -> str:
        return f"<function {self.name}>"
    
    def copy(self) -> Self:
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def execute(self, args: list[Datatype]) -> DATATYPE_OR_ERROR:
        from ..components.runtime import RuntimeResult
        from ..components.interpreter import Interpreter
        from ..components.context import Context
        from ..components.symbol_table import SymbolTable
        
        rt_result = RuntimeResult()
        interpreter = Interpreter()
        
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        
        if len(args) > len(self.arg_names):
            return rt_result.failure(ErrorRuntime(
                f"{len(args) - len(self.arg_names)} too many arguments passed into '{self.name}'",
                self.pos_start, self.pos_end, self.context
            ))
            
        elif len(args) < len(self.arg_names):
            return rt_result.failure(ErrorRuntime(
                f"{len(self.arg_names) - len(args)} too few arguments passed into '{self.name}'",
                self.pos_start, self.pos_end, self.context
            ))
            
        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)
        
        value = rt_result.register(interpreter.visit(self.body_node, new_context))
        if rt_result.error: return rt_result
        
        return rt_result.success(value)
            