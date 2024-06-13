from typing import Tuple, Optional
from .components.lexer import Lexer
from .components.parser import Parser
from .components.interpreter import Interpreter
from .components.context import Context
from .components.symbol_table import SymbolTable
from .components.error import Error
from .datatype import List
from .datatype.utils import set_builtin_symbols

global_symbol_table = SymbolTable()
set_builtin_symbols(global_symbol_table)

def execute(src_filename: str, src_data: str) -> Tuple[Optional[List], Optional[Error]]:
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    
    interpreter = Interpreter()
    context = Context("__main__")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

def make_executable():
    from . import __version__ as ns_version
    from .tools.make_executable import make_executable
    make_executable(ns_version.split("."))
    