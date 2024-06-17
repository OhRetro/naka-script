from dataclasses import dataclass, field
from typing import Self, TypeVar, TYPE_CHECKING
from .position import Position

if TYPE_CHECKING:
    from .symbol_table import SymbolTable
    from ..datatype import Datatype
else:
    SymbolTable = TypeVar("SymbolTable")
    Datatype = TypeVar("Datatype")

@dataclass(slots=True)
class Context:
    name: str
    parent: Self = field(default=None)
    parent_entry_pos: Position = field(default=None)
    symbol_table: SymbolTable = field(default=None, init=False)
    
    def __repr__(self) -> str:
        return f"Context(\"{self.name}\", {self.symbol_table}, {self.parent})"
    
    def get_symbol(self, name: str) -> Datatype:
        return self.symbol_table.get(name)
    