from typing import Any
from .datatype import Datatype
from .number import Number
from .function import Function
from .builtinfunction import built_in_functions
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
    
    for k, v in built_in_functions.items():
        symbol_table.set(k, v)
    
    return symbol_table
