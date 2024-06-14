from dataclasses import dataclass
from typing import Callable
from types import MethodType
from os import name as os_name, system as os_system
from .datatype import Datatype, DATATYPE_OR_ERROR
from .function import BaseFunction
from .number import Number
from .string import String
from .list import List
from ..components.error import ErrorRuntime
from ..components.runtime import RuntimeResult
from ..components.context import Context

@dataclass(slots=True)
class BuiltInFunction(BaseFunction):
    arg_names: tuple[str]
    logic_function: Callable

    def __post_init__(self):
        self._values_to_copy = ("name", "arg_names", "logic_function")

    def __repr__(self) -> str:
        return f"<built-in function {self.name}>"

    def _rt_result_success(self, datatype: Datatype) -> RuntimeResult:
        return RuntimeResult().success(datatype)

    def _rt_result_failure(self, details: str, context: Context) -> RuntimeResult:
        return RuntimeResult().failure(ErrorRuntime(
            details, self.pos_start, self.pos_end, context
        ))

    def execute(self, args: list[Datatype]) -> DATATYPE_OR_ERROR:
        rt_result = RuntimeResult()
        context = self.generate_new_context()

        if self.logic_function.__code__.co_argcount < 2:
            raise Exception(f"The logic function '{self.logic_function.__name__}' for '{self.name}' doesn't contain at least 2 arguments")
        
        method = MethodType(self.logic_function, self)

        rt_result.register(self.check_populate_args(self.arg_names or tuple(), args, context))
        if rt_result.error:
            return rt_result

        value = rt_result.register(method(context) or self._rt_result_success(Number.null))
        if rt_result.error:
            return rt_result

        return rt_result.success(value)

def _print(_, context: Context) -> None:
    print(str(context.symbol_table.get("value")))

def _to_string(self: BuiltInFunction, context: Context):
    return self._rt_result_success(String(str(context.symbol_table.get("value"))))

def _input(self: BuiltInFunction, _):
    text = input()
    return self._rt_result_success(String(text))

def _input_number(self: BuiltInFunction, _):
    text = input()
    try:
        number = float(text) if "." in text else int(text)
        return self._rt_result_success(Number(number))
    except ValueError:
        return None

def _clear(_, __):
    os_system("cls" if os_name == "nt" else "clear")

def _is_number(self: BuiltInFunction, context: Context):
    is_number = isinstance(context.symbol_table.get("value"), Number)
    return self._rt_result_success(Number.true if is_number else Number.false)

def _is_string(self: BuiltInFunction, context: Context):
    is_string = isinstance(context.symbol_table.get("value"), String)
    return self._rt_result_success(Number.true if is_string else Number.false)

def _is_list(self: BuiltInFunction, context: Context):
    is_list = isinstance(context.symbol_table.get("value"), List)
    return self._rt_result_success(Number.true if is_list else Number.false)

def _is_function(self: BuiltInFunction, context: Context):
    is_function = isinstance(context.symbol_table.get("value"), BaseFunction)
    return self._rt_result_success(Number.true if is_function else Number.false)

def _append(self: BuiltInFunction, context: Context):
    list_ = context.symbol_table.get("list")
    value = context.symbol_table.get("value")

    if not isinstance(list_, List):
        return self._rt_result_failure("First argument must be list", context)

    list_.value.append(value)

def _pop(self: BuiltInFunction, context: Context):
    list_ = context.symbol_table.get("list")
    index = context.symbol_table.get("index")

    if not isinstance(list_, List):
        return self._rt_result_failure("First argument must be list", context)

    if not isinstance(index, Number):
        return self._rt_result_failure("Second argument must be number", context)

    try:
        element = list_.value.pop(int(index.value))
    except IndexError:
        return self._rt_result_failure("Element at index doesn't exist, Out of bounds", context)

    return self._rt_result_success(element)

def _extend(self: BuiltInFunction, context: Context):
    listA = context.symbol_table.get("listA")
    listB = context.symbol_table.get("listB")

    if not isinstance(listA, List):
        return self._rt_result_failure("First argument must be list", context)

    if not isinstance(listB, List):
        return self._rt_result_failure("Second argument must be list", context)

    listA.value.extend(listB.value)

built_in_functions = {
    "print": BuiltInFunction("print", ("value",), _print),
    "to_string": BuiltInFunction("to_string", ("value",), _to_string),
    "input": BuiltInFunction("input", None, _input),
    "input_number": BuiltInFunction("input_int", None, _input_number),
    "clear": BuiltInFunction("clear", None, _clear),
    "is_number": BuiltInFunction("is_number", ("value",), _is_number),
    "is_string": BuiltInFunction("is_string", ("value",), _is_string),
    "is_list": BuiltInFunction("is_list", ("value",), _is_list),
    "is_function": BuiltInFunction("is_function", ("value",), _is_function),
    "append": BuiltInFunction("append", ("list", "value"), _append),
    "pop": BuiltInFunction("pop", ("list", "index"), _pop),
    "extend": BuiltInFunction("extend", ("listA", "listB"), _extend),
}
