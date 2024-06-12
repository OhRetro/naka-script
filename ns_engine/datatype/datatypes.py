from typing import Any
from .datatype import Datatype
from .number import Number
from .function import Function
from .builtinfunction import BuiltInFunction
from .string import String
from .list import List

def makeout_datatype(value: Any) -> Datatype:
    if isinstance(value, (int, float)):
        return Number(value)
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, list):
        return List(value)
    else:
        raise TypeError(f"Could not convert {value} to a Datatype")
    
def set_builtin_symbols(symbol_table):
    symbol_table.set("null", Number.null)
    symbol_table.set("true", Number.true)
    symbol_table.set("false", Number.false)
    symbol_table.set("print", BuiltInFunction.print)
    symbol_table.set("print_ret", BuiltInFunction.print_ret)
    symbol_table.set("input", BuiltInFunction.input)
    symbol_table.set("input_int", BuiltInFunction.input_int)
    symbol_table.set("clear", BuiltInFunction.clear)
    symbol_table.set("cls", BuiltInFunction.clear)
    symbol_table.set("is_num", BuiltInFunction.is_number)
    symbol_table.set("is_str", BuiltInFunction.is_string)
    symbol_table.set("is_list", BuiltInFunction.is_list)
    symbol_table.set("is_fun", BuiltInFunction.is_function)
    symbol_table.set("append", BuiltInFunction.append)
    symbol_table.set("pop", BuiltInFunction.pop)
    symbol_table.set("extend", BuiltInFunction.extend)
    
    return symbol_table