from dataclasses import dataclass, field
from typing import Never
from .base_function import BaseFunction
from ..datatype import Datatype
from ..number import Number
from ns_engine.components.node import Node
from ns_engine.components.runtime import RuntimeResult

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
    
    def execute(self, args: list[Datatype]) -> Datatype:
        from ns_engine.components.interpreter import Interpreter

        rt_result = RuntimeResult()
        interpreter = Interpreter()
        
        context = self.generate_new_context()
        
        rt_result.register(self.check_populate_args(self.arg_names, args, context))
        if rt_result.should_return(): return rt_result
        
        value = rt_result.register(interpreter.visit(self.body_node, context))
        if rt_result.should_return() and rt_result.func_return_value is None: return rt_result
        
        return_value = (value if self.should_auto_return else None) or rt_result.func_return_value or Number.null
        return rt_result.success(return_value)
