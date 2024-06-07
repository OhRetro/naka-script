from dataclasses import dataclass, field
from typing import Self
from ..datatype.datatypes import Datatype, makeout_datatype

@dataclass(slots=True)
class SymbolTable:
    symbols: dict[str, Datatype] = field(default_factory=dict, init=False)
    parent: Self = field(default=None, init=False)
    
    def get(self, name: str) -> Datatype:
        value = self.symbols.get(name, None)
        
        if not value and self.parent:
            value = self.parent.get(name)
            
        return value
    
    def set(self, name: str, value: Datatype):
        if not isinstance(value, Datatype):
            value = makeout_datatype(value)
        
        self.symbols[name] = value
        
    def remove(self, name: str):
        del self.symbols[name]
        