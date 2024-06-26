from dataclasses import dataclass
from typing import Callable
from types import MethodType, NoneType
from os import name as os_name, system as os_system
from os.path import abspath as osp_abspath
from random import random, randint
from ..base_function import BaseFunction
from ns_engine.components.datatypes import Datatype, Number, String, List, Module
from ns_engine.components.errors import NSRuntimeError
from ns_engine.components.runtime import RuntimeResult
from ns_engine.components.context import Context
from ns_engine.utils.misc import get_filedata

@dataclass(slots=True)
class BuiltInFunction(BaseFunction):
    arg_names: tuple[str]
    logic_function: Callable

    def __post_init__(self):
        self._values_to_copy = ("name", "arg_names", "logic_function")

    def __repr__(self) -> str:
        return f"<built-in function \"{self.name}\">"

    def _rt_result_success(self, datatype: Datatype) -> RuntimeResult:
        return RuntimeResult().success(datatype)

    def _rt_result_failure(self, details: str, context: Context) -> RuntimeResult:
        return RuntimeResult().failure(NSRuntimeError(
            details, self.pos_start, self.pos_end, context
        ))

    def execute(self, args: list[Datatype]) -> Datatype:
        rt_result = RuntimeResult()
        context = self.generate_new_context()

        if self.logic_function.__code__.co_argcount < 2:
            raise Exception(f"The logic function '{self.logic_function.__name__}' for '{self.name}' doesn't contain at least 2 arguments")
        
        method = MethodType(self.logic_function, self)
        
        arg_names = tuple([self.arg_names]) if not isinstance(self.arg_names, (list, tuple, NoneType)) else self.arg_names

        rt_result.register(self.check_populate_args(arg_names or tuple(), args, context))
        if rt_result.should_return():
            return rt_result

        value = rt_result.register(method(context) or self._rt_result_success(Number.null))
        if rt_result.should_return():
            return rt_result

        return rt_result.success(value)

def _print(_, context: Context):
    print(str(context.get_symbol("value")))

def _to_string(self: BuiltInFunction, context: Context):
    return self._rt_result_success(String(str(context.get_symbol("value"))))

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

def _clear(*_):
    os_system("cls" if os_name == "nt" else "clear")

def _is_number(self: BuiltInFunction, context: Context):
    is_number = isinstance(context.get_symbol("value"), Number)
    return self._rt_result_success(Number.true if is_number else Number.false)

def _is_string(self: BuiltInFunction, context: Context):
    is_string = isinstance(context.get_symbol("value"), String)
    return self._rt_result_success(Number.true if is_string else Number.false)

def _is_list(self: BuiltInFunction, context: Context):
    is_list = isinstance(context.get_symbol("value"), List)
    return self._rt_result_success(Number.true if is_list else Number.false)

def _is_function(self: BuiltInFunction, context: Context):
    is_function = isinstance(context.get_symbol("value"), BaseFunction)
    return self._rt_result_success(Number.true if is_function else Number.false)

def _random(self: BuiltInFunction, _):
    return self._rt_result_success(Number(random()))

def _random_int(self: BuiltInFunction, context: Context):
    min_ = context.get_symbol("min")
    max_ = context.get_symbol("max")

    if (not isinstance(min_, Number) or not isinstance(max_, Number)) or (
        not isinstance(min_.value, int) or not isinstance(max_.value, int)):
        return self._rt_result_failure(
            "Both arguments must be 'Number: int'",
            context
        )
        
    return self._rt_result_success(Number(randint(min_.value, max_.value)))

def _run(self: BuiltInFunction, context: Context):
    from ns_engine.wrapper import interpret 
    
    filename = context.get_symbol("filename")
    
    if not isinstance(filename, String):
        return self._rt_result_failure(
            "Argument must be string",
            context
        )
    
    filename = filename.value
    abspath_filename = osp_abspath(filename)
    
    if abspath_filename == context.get_symbol("__file__").value:
        return self._rt_result_failure(
            "Cannot run itself",
            context
        )
        
    try:
        script_code = get_filedata(filename)
            
    except FileNotFoundError as e:
        return self._rt_result_failure(
            f"Failed to load script \"{filename}\": {e}",
            context
        )
    
    _, error, _ = interpret(filename, script_code) # , ctx_name="__submain__")
    
    if error:
        return self._rt_result_failure(
            f"Failed to finish script \"{filename}\":\n{error.as_string()}",
            context
        )

def _import(self: BuiltInFunction, context: Context):
    from ns_engine.wrapper import interpret, imported_modules

    filename = context.get_symbol("filename")
    
    if not isinstance(filename, String):
        return self._rt_result_failure(
            "Argument must be string",
            context
        )
    
    filename = filename.value
    abspath_filename = osp_abspath(filename)
    
    if abspath_filename == context.get_symbol("__file__").value:
        return self._rt_result_failure(
            "Cannot import itself",
            context
        )
    
    already_imported_module = imported_modules.get(abspath_filename, False)
    
    if not already_imported_module:
        try:
            script_code = get_filedata(filename)
                
        except FileNotFoundError as e:
            return self._rt_result_failure(
                f"Failed to load module \"{filename}\": {e}",
                context
            )
            
        filenameext = abspath_filename.replace("\\", "/").split("/")[-1]
            
        _, error, context = interpret(filename, script_code, 
                                      ctx_name="__module__", ctx_name_post=filenameext)
        
        if error:
            return self._rt_result_failure(
                f"Failed to finish importing \"{filename}\":\n{error.as_string()}",
                context
            )
            
        imported_module = Module(context)
        imported_modules[abspath_filename] = imported_module
        
    return self._rt_result_success(already_imported_module or imported_module)

built_in_functions = {
    "print": ("value", _print),
    "clear": (None, _clear),
    "run": ("filename", _run),
    "import": ("filename", _import),

    "toString": ("value", _to_string),

    "input": (None, _input),
    "inputNumber": (None, _input_number),

    "isNumber": ("value", _is_number),
    "isString": ("value", _is_string),
    "isList": ("value", _is_list),
    "isFunction": ("value", _is_function),
    
    "random": (None, _random),
    "randomInt": (("min", "max"), _random_int)
}
