from dataclasses import dataclass
from typing import TypeVar, TYPE_CHECKING
from .datatype import Datatype, DATATYPE_OR_ERROR
from .number import Number
from ..error import ErrorRuntime

if TYPE_CHECKING:
    from ..context import Context
else:
    Context = TypeVar("Context")

@dataclass(slots=True)
class Module(Datatype):
    value: Context

    def __repr__(self) -> str:
        return f"<module {self.value.name}>"
    
    def access_at(self, attribute_name: str) -> DATATYPE_OR_ERROR:
        datatype_attribute = self.value.get_symbol(attribute_name)
        
        if not datatype_attribute:
            return None, ErrorRuntime(
                f"Attribute '{attribute_name}' doesn't exist",
                self.pos_start, self.pos_end, self.context
            )
        
        return datatype_attribute, None

    def update_access_at(self, attribute_name: str, new: Datatype) -> DATATYPE_OR_ERROR:
        symbol_table = self.value.symbol_table
        symbols_dict_type, _ = symbol_table.exists_where(attribute_name)
        
        if not symbol_table.exists(attribute_name):
            return None, ErrorRuntime(
                f"Variable '{attribute_name}' was not defined.",
                self.pos_start, self.pos_end, self.context
            )
        else:
            if symbols_dict_type == "immutable_symbols":
                return None, ErrorRuntime(
                    f"'{attribute_name}' is a constant variable.",
                    self.pos_start, self.pos_end, self.context
                )
            if symbols_dict_type == "persistent_symbols":
                return None, ErrorRuntime(
                    f"'{attribute_name}' is a persistent and builtin variable.",
                    self.pos_start, self.pos_end, self.context
                )

        symbol_table.set(attribute_name, new, symbols_dict_type)
        return Number.null, None
        