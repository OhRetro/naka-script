from typing import Tuple, Optional
from os.path import abspath as osp_abspath, dirname as osp_dirname
from .components.lexer import Lexer
from .components.parser import Parser
from .components.interpreter import Interpreter
from .components.context import Context
from .components.error import Error
from .components.node import Node
from .datatype import List
from .datatype.utils import setup_starter_symbol_table
from .utils.misc import temp_cwd

shell_symbol_table = setup_starter_symbol_table()

def generate_ast(src_filename: str, src_data: str)-> Tuple[Optional[Node], Optional[Error]]:
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error

def interpret(src_filename: str, src_data: str) -> Tuple[Optional[List], Optional[Error], Context]:
    with temp_cwd(osp_dirname(osp_abspath(src_filename))):
        node, error = generate_ast(src_filename, src_data)
        if error: return None, error, None
        
        interpreter = Interpreter()
        context = Context("__main__")
        context.symbol_table = setup_starter_symbol_table() if src_filename != "<shell>" else shell_symbol_table
        result = interpreter.visit(node, context)
        
        return result.value, result.error, context

__all__ = [
    "interpret"
]
    