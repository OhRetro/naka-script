from .number import Number
from .builtinfunction import built_in_functions
from . import convert_to_datatype
from ..components.symbol_table import SymbolTable

def setup_global_symbols_symbols() -> SymbolTable:
    symbol_table = SymbolTable()
    symbol_table.set("null", Number.null)
    symbol_table.set("true", Number.true)
    symbol_table.set("false", Number.false)
    
    for k, v in built_in_functions.items():
        symbol_table.set(k, v)
    
    return symbol_table