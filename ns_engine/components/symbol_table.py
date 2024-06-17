from dataclasses import dataclass, field
from typing import Self
from ..datatype import Datatype, convert_to_datatype

@dataclass(slots=True)
class SymbolTable:
    symbols: dict[str, Datatype] = field(default_factory=dict, init=False)
    local_symbols: dict[str, Datatype] = field(default_factory=dict, init=False)
    
    parent: Self = field(default=None)
    
    def __repr__(self) -> str:
        return f"SymbolTable({len(self.symbols)} symbols, {len(self.local_symbols)} local_symbols)"
    
    def get(self, name: str) -> Datatype:
        value = self.symbols.get(name, None)
        
        if not value and self.parent:
            value = self.parent.get(name)
            
        return value
    
    def set(self, name: str, value: Datatype):
        if not isinstance(value, Datatype):
            value = convert_to_datatype(value)
        
        self.symbols[name] = value
        
    def remove(self, name: str):
        del self.symbols[name]
        
    def exists(self, name: str) -> bool:
        return name in self.symbols
    
    def clear(self):
        self.symbols.clear()
