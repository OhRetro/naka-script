from typing import Any
from .datatype import Datatype
from .number import Number

def makeout_datatype(value: Any) -> Datatype:
    if isinstance(value, int) or isinstance(value, float):
        return Number(value)
    else:
        raise TypeError(f"Cannot convert {value} to a datatype")