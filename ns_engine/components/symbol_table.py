from dataclasses import dataclass, field
from typing import Self, Dict
from ..datatype.value import Value

#TODO: still need to refactor this

@dataclass
class SymbolTable:
    symbols: Dict[str, Value] = field(default_factory=dict)
    immutable_symbols: Dict[str, Value] = field(default_factory=dict)
    scoped_symbols: Dict[str, Value] = field(default_factory=dict)
    
    builtin_symbols: Dict[str, Value] = field(default_factory=dict)
    
    parent: Self = None

    def _exists(self, name: str, symbols_name: str):
        return name in getattr(self, symbols_name)
    
    def exists_in(self, name: str, get_from_parent: bool = False):
        symbol_type_name = None
        
        if name in self.scoped_symbols and not get_from_parent:
            symbol_type_name = "scoped_symbols"
            
        elif name in self.immutable_symbols:
            symbol_type_name = "immutable_symbols"
            
        elif name in self.symbols:
            symbol_type_name = "symbols"
            
        elif name in self.builtin_symbols:
            symbol_type_name = "builtin_symbols"
            
        if symbol_type_name is None and self.parent:
            symbol_type_name = self.parent.exists_in(name, True)
            
        return symbol_type_name
            
    def exists(self, name: str, get_from_parent: bool = False) -> bool:
        exists = False

        symbols_name_list = [
            "scoped_symbols",
            "immutable_symbols",
            "symbols",
            "builtin_symbols"
        ]
        
        if get_from_parent:
            symbols_name_list.remove("scoped_symbols")
        
        for symbols in symbols_name_list:
            exists = self._exists(name, symbols)
            if exists: break
            
        if not exists and self.parent:
            exists = self.parent.exists(name, True)
            
        return exists

    def _is_immutable_or_builtin_check(self, name: str):
        exists = self._exists(name, "immutable_symbols") or self._exists(name, "builtin_symbols")
        
        if not exists and self.parent:
            exists = self.parent._is_immutable_or_builtin_check(name)
        
        return exists
    
    def _get(self, name: str, get_from_parent: bool = False):
        symbol_type_name = self.exists_in(name)
        
        if symbol_type_name == "scoped_symbols" and get_from_parent:
            value = None
        else:
            value = getattr(self, symbol_type_name).get(name)

        if value is None and self.parent:
            value = self.parent._get(name, True)
                
        return value

    def get(self, name: str) -> Value:
        return self._get(name)
    
    def _set_symbol(self, name: str, value: Value, symbols_name: str):
        success = False
        fail_type = "const"
        
        if self._exists(name, symbols_name):
            current_type = getattr(self, symbols_name)[name][1]
            if type != current_type:
                fail_type = "type"
        
        if not self._is_immutable_or_builtin_check(name) and fail_type == "const":
            getattr(self, symbols_name)[name] = (value, type)
            success = True
                
        return success, fail_type
   
    def set(self, name: str, value: Value, type: Value):
        return self._set_symbol(name, value, type, "symbols")

    def set_as_immutable(self, name: str, value: Value, type: Value):
        return self._set_symbol(name, value, type, "immutable_symbols")
        
    def set_as_scoped(self, name: str, value: Value, type: Value):
        return self._set_symbol(name, value, type, "scoped_symbols")

    def set_as_builtin(self, name: str, value: Value, type: Value):
        return self._set_symbol(name, value, type, "builtin_symbols")
        
    def remove(self, name: str):
        if name in self.symbols:
            del self.symbols[name]
        elif name in self.immutable_symbols:
            del self.immutable_symbols[name]
        elif name in self.scoped_symbols:
            del self.scoped_symbols[name]
            
    def copy(self):
        copy = SymbolTable(self)
        copy.symbols = self.symbols
        copy.immutable_symbols = self.immutable_symbols
        return copy
            