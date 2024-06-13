from typing import Any
from .datatype import Datatype
from .number import Number
from .function import Function
from .string import String
from .list import List

def convert_to_datatype(value: Any) -> Datatype:
    if isinstance(value, (int, float)):
        return Number(value)
    elif isinstance(value, bool):
        return Number.true if value else Number.false
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, list):
        return List(value)
    else:
        raise TypeError(f"Could not convert {value} to a Datatype")

#! NOT A FINISHED FUNCTION
def new_datatype(value: Any, context):
    return convert_to_datatype(value).set_context(context), None

__all__ = [
    "Datatype",
    "Number",
    "Function",
    "String",
    "List",
    
    "convert_to_datatype"
]
