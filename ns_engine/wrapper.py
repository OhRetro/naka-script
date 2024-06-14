from typing import Tuple, Optional
from .components.lexer import Lexer
from .components.parser import Parser
from .components.interpreter import Interpreter
from .components.context import Context
from .components.symbol_table import SymbolTable
from .components.error import Error
from .components.node import Node
from .datatype import List
from .datatype.utils import set_builtin_symbols

global_symbol_table = SymbolTable()
set_builtin_symbols(global_symbol_table)

def generate_ast(src_filename: str, src_data: str)-> Tuple[Optional[Node], Optional[Error]]:
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error

def interpret(src_filename: str, src_data: str) -> Tuple[Optional[List], Optional[Error]]:
    node, error = generate_ast(src_filename, src_data)
    if error: return None, error
    
    interpreter = Interpreter()
    context = Context("__main__")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(node, context)

    return result.value, result.error

__all__ = [
    "interpret"
]
    