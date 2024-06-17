from .number import Number
from .builtinfunction import BuiltInFunction, built_in_functions
from . import convert_to_datatype
from ..components.symbol_table import SymbolTable

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
