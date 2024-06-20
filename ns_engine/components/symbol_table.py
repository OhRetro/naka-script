from dataclasses import dataclass, field
from typing import Self, Tuple, Optional
from gc import collect as gc_collect
from .datatypes import Datatype, Number, convert_to_datatype 
from .datatypes.functions import BuiltInFunction, built_in_functions

SYMBOLS_DICT = dict[str, Datatype]

@dataclass(slots=True)
class SymbolTable:
    symbols: SYMBOLS_DICT = field(default_factory=dict, init=False)
    immutable_symbols: SYMBOLS_DICT = field(default_factory=dict, init=False)
    persistent_symbols: SYMBOLS_DICT = field(default_factory=dict, init=False)
    
    parent: Self = field(default=None)
    
    def __repr__(self) -> str:
        return f"SymbolTable({len(self.symbols)} symbols, {len(self.immutable_symbols)} immutable_symbols, {len(self.persistent_symbols)} persistent_symbols)"
    
    def _get_symbols_dict(self, type: str) -> SYMBOLS_DICT:
        if type != "symbols" and not type.endswith("_symbols"):
            raise ValueError(f"'{type}' is not a valid symbols type")
            
        symbols_dict: SYMBOLS_DICT = getattr(self, type)
        return symbols_dict
    
    def get(self, name: str) -> Optional[Datatype]:
        _, symbols_dict = self.exists_where(name)
        
        value = symbols_dict.get(name) if symbols_dict else None
        
        if not value and self.parent:
            value = self.parent.get(name)
            
        return value
    
    def set(self, name: str, value: Datatype, type: str):
        if not isinstance(value, Datatype):
            value = convert_to_datatype(value)
        self._get_symbols_dict(type)[name] = value
        
    def remove(self, name: str):
        _, symbols_dict = self.exists_where(name)
        del symbols_dict[name]
        gc_collect()
        
    def exists(self, name: str) -> bool:
        symbols_dict_name, _ = self.exists_where(name)
        return symbols_dict_name != None
    
    def exists_where(self, name: str) -> Tuple[Optional[str], Optional[SYMBOLS_DICT]]:
        symbols_dict_check_order = {
            "immutable_symbols": self.immutable_symbols,
            "symbols": self.symbols,
            "persistent_symbols": self.persistent_symbols,
        }
        
        for k, v in symbols_dict_check_order.items():
            if name in v: return k, v
            
        return None, None
    
    def clear(self, type: str):
        self._get_symbols_dict(type).clear()

def setup_starter_symbol_table(**extras) -> SymbolTable:
    symbol_table = SymbolTable()
    
    for args in [
        ("null", Number.null),
        ("true", Number.true),
        ("false", Number.false)
    ]:
        symbol_table.set(*args, "symbols")
    
    for k, v in built_in_functions.items():
        symbol_table.set(k, BuiltInFunction(k, *v), "symbols")
    
    for k, v in extras.items():
        symbol_table.set(k, convert_to_datatype(v), "symbols")
    
    return symbol_table