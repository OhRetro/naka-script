from typing import Any, TypeVar, TYPE_CHECKING, List as type_List, Dict as type_Dict
from types import NoneType
from .datatype import Datatype
from .number import Number
from .function import Function, BaseFunction
from .string import String
from .list import List
from .dict import Dict
from .module import Module

if TYPE_CHECKING:
    from ..context import Context
else:
    Context = TypeVar("Context")

def convert_to_datatype(value: Any) -> Datatype:
    if isinstance(value, (int, float)):
        return Number(value)
    elif isinstance(value, bool):
        return Number.true if value else Number.false
    elif isinstance(value, NoneType):
        return Number.null
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, type_List):
        new_value: list[Datatype] = [
            convert_to_datatype(v) if not isinstance(v, Datatype) else v for v in value
        ]
        return List(new_value)
    elif isinstance(value, type_Dict):
        new_value: dict[str, Datatype] = {}
        
        for k, v in value.items():
            new_value[str(k)] = convert_to_datatype(v) if not isinstance(v, Datatype) else v
        
        return Dict(new_value)
    else:
        raise TypeError(f"Could not convert '{value}' to a Datatype")

__all__ = [
    "Datatype",
    "Number",
    "Function", "BaseFunction",
    "String",
    "List",
    "Dict",
    "Module",
    
    "convert_to_datatype"
]
