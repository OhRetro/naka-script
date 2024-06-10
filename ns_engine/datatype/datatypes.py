from typing import Any
from .datatype import Datatype
from .number import Number
from .function import Function
from .string import String

def makeout_datatype(value: Any) -> Datatype:
    if isinstance(value, int) or isinstance(value, float):
        return Number(value)
    elif isinstance(value, str):
        return String(value)
    else:
        raise TypeError(f"Could not convert {value} to a Datatype")
    