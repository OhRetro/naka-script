from dataclasses import dataclass
from typing import Self
# from copy import deepcopy
from ..datatype.value import Value

#TODO: still need to refactor this

@dataclass
class SymbolTable:
    symbols: dict[str, Value] = {}
    immutable_symbols: dict[str, Value] = {}
    scoped_symbols: dict[str, Value] = {}
    
    builtin_symbols: dict[str, Value] = {}
    
    parent: Self = None
        
    def _exists(self, name: str, symbols_name: str, extra_condition: bool = True):
        return name in getattr(self, symbols_name) and extra_condition

    def exists_in(self, name: str, get_from_parent: bool = False):
        symbol_type_name = None
        found_in_parent = False
        
        if name in self.scoped_symbols and not get_from_parent:
            symbol_type_name = "scoped_symbols"
            
        elif name in self.immutable_symbols:
            symbol_type_name = "immutable_symbols"
            
        elif name in self.symbols:
            symbol_type_name = "symbols"
            
        elif name in self.builtin_symbols:
            symbol_type_name = "builtin_symbols"
            
        if symbol_type_name is None and self.parent:
            symbol_type_name, _ = self.parent.exists_in(name, True)
            if symbol_type_name: found_in_parent = True
            
        return symbol_type_name, found_in_parent
            
    def exists(self, name: str, get_from_parent: bool = False) -> bool:
        exists = False

        symbols_list = [
            ("scoped_symbols", not get_from_parent),
            ("immutable_symbols", 1),
            ("symbols", 1),
            ("builtin_symbols", 1)
        ]
        
        for symbols in symbols_list:
            exists = self._exists(name, symbols[0], symbols[1])
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
        symbol_type_name, found_in_parent = self.exists_in(name)
        
        value = getattr(self, symbol_type_name).get(name)

        if value is None and self.parent and found_in_parent:
            value = self.parent._get(name, True)[0]
            type = self.parent._get(name, True)[1]
                
        return value, type

    def get(self, name: str, calling_from_parent: bool = False) -> Value:
        return self._get(name, calling_from_parent)[0]
    
    def get_type(self, name: str, calling_from_parent: bool = False) -> Value:
        return self._get(name, calling_from_parent)[1]
    
    def _set_symbol(self, name: str, value: Value, type: Value, symbols_name: str, **kwargs):
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
            