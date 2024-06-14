from dataclasses import dataclass, field
from typing import Self, TypeVar, TYPE_CHECKING
from .position import Position

if TYPE_CHECKING:
    from .symbol_table import SymbolTable
else:
    SymbolTable = TypeVar("SymbolTable")

@dataclass(slots=True)
class Context:
    name: str
    parent: Self = field(default=None)
    parent_entry_pos: Position = field(default=None)
    symbol_table: SymbolTable = field(default=None, init=False)
    