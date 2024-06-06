from dataclasses import dataclass
from typing import Self
from .symbol_table import SymbolTable

@dataclass
class Context:
    name: str
    symbol_table: SymbolTable = None
    parent: Self = None
        