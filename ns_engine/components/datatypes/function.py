from dataclasses import dataclass, field
from typing import Never
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from ..errors import NSRuntimeError
from ..node import Node
from ..runtime import RuntimeResult
from ..context import Context

@dataclass(slots=True)
class BaseFunction(Datatype):
    value: Never = field(default=None, init=False)
    name: str

    def __post_init__(self):
        self._values_to_copy = ("name", )

    def generate_new_context(self) -> Context:
        from ..symbol_table import SymbolTable

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

@dataclass(slots=True)
class Function(BaseFunction):
    value: Never = field(default=None, init=False)
    body_node: Node
    arg_names: list[str]
    should_auto_return: bool

    def __post_init__(self):
        self._values_to_copy = ("name", "body_node", "arg_names", "should_auto_return")

    def __repr__(self) -> str:
        return f"<function \"{self.name}\">"
    
    def execute(self, args: list[Datatype]) -> DATATYPE_OR_ERROR:
        from ..interpreter import Interpreter

        rt_result = RuntimeResult()
        interpreter = Interpreter()
        
        context = self.generate_new_context()
        
        rt_result.register(self.check_populate_args(self.arg_names, args, context))
        if rt_result.should_return(): return rt_result
        
        value = rt_result.register(interpreter.visit(self.body_node, context))
        if rt_result.should_return() and rt_result.func_return_value is None: return rt_result
        
        return_value = (value if self.should_auto_return else None) or rt_result.func_return_value or Number.null
        return rt_result.success(return_value)
