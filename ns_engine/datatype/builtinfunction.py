from dataclasses import dataclass, field
from os import name as os_name, system as os_system

from .datatype import Datatype, DATATYPE_OR_ERROR
from .function import BaseFunction
from .number import Number
from .string import String
from .list import List

from ..components.error import ErrorRuntime
from ..components.node import Node
from ..components.runtime import RuntimeResult
from ..components.context import Context

@dataclass(slots=True)
class BuiltInFunction(BaseFunction):
    arg_names: tuple = field(default_factory=tuple, init=False)
    
    def __repr__(self) -> str:
        return f"<built-in function {self.name}>"

    def no_visit_method(self, node: Node, context: Context):
        raise Exception(f"No execute_{self.name} method defined")

    def execute(self, args: list[Datatype]) -> DATATYPE_OR_ERROR:
        rt_result = RuntimeResult()
        context = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)
        
        rt_result.register(self.check_populate_args(method.arg_names, args, context))
        if rt_result.error: return rt_result
        
        value = rt_result.register(method(context))
        if rt_result.error: return rt_result
        
        return rt_result.success(value)
    

    def execute_print(self, context: Context):
        print(str(context.symbol_table.get("value")))
        return RuntimeResult().success(Number.null)
    execute_print.arg_names = ["value"]

    def execute_print_ret(self, context: Context):
        return RuntimeResult().success(String(str(context.symbol_table.get("value"))))
    execute_print_ret.arg_names = ["value"]

    def execute_input(self, context: Context):
        text = input()
        return RuntimeResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, context: Context):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RuntimeResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, context: Context):
        os_system("cls" if os_name == "nt" else "cls") 
        return RuntimeResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, context: Context):
        is_number = isinstance(context.symbol_table.get("value"), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, context: Context):
        is_number = isinstance(context.symbol_table.get("value"), String)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, context: Context):
        is_number = isinstance(context.symbol_table.get("value"), List)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, context: Context):
        is_number = isinstance(context.symbol_table.get("value"), BaseFunction)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, context: Context):
        list_ = context.symbol_table.get("list")
        value = context.symbol_table.get("value")

        if not isinstance(list_, List):
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "First argument must be list",
                context
            ))

        list_.elements.append(value)
        return RuntimeResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, context: Context):
        list_ = context.symbol_table.get("list")
        index = context.symbol_table.get("index")

        if not isinstance(list_, List):
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "First argument must be list",
                context
            ))

        if not isinstance(index, Number):
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                context
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of bounds",
                context
            ))
        return RuntimeResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, context: Context):
        listA = context.symbol_table.get("listA")
        listB = context.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "First argument must be list",
                context
            ))

        if not isinstance(listB, List):
            return RuntimeResult().failure(ErrorRuntime(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                context
            ))

        listA.elements.extend(listB.elements)
        return RuntimeResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
