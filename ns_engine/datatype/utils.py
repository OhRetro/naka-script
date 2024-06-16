from .number import Number
from .builtinfunction import built_in_functions
from ..components.symbol_table import SymbolTable

def setup_global_symbols() -> SymbolTable:
    symbol_table = SymbolTable()
    symbol_table.set("null", Number.null)
    symbol_table.set("true", Number.true)
    symbol_table.set("false", Number.false)
    
    for k, v in built_in_functions.items():
        symbol_table.set(k, v)
    
    return symbol_table

def clear_global_symbols(symbol_table: SymbolTable) -> SymbolTable:
    symbol_table.remove("null")
    symbol_table.remove("true")
    symbol_table.remove("false")
    
    for k in built_in_functions.keys():
        symbol_table.remove(k)
    
    return symbol_table
