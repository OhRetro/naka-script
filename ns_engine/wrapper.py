from typing import Tuple, Optional
from os.path import abspath as osp_abspath, dirname as osp_dirname
from .components.lexer import Lexer
from .components.parser import Parser
from .components.interpreter import Interpreter
from .components.token import Token, TokenType
from .components.context import Context
from .components.errors import Error
from .components.node import Node
from .components.datatypes import List
from .components.symbol_table import setup_starter_symbol_table
from .utils.misc import temp_cwd

shell_symbol_table = setup_starter_symbol_table()
imported_modules = {}

def is_valid_tokens(tokens: list[Token]) -> bool:
    for token in tokens:
        if token.is_type_of(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.EOF):
            continue
        elif not token.is_type_of(TokenType.SEMICOLON, TokenType.NEWLINE):
            return True
        
    return False
        
def generate_ast(src_filename: str, src_data: str)-> Tuple[Optional[Node], Optional[Error]]:
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    if error: 
        return None, error
    elif not is_valid_tokens(tokens): 
        return None, None
    
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error

def interpret(src_filename: str, src_data: str, **kwargs) -> Tuple[Optional[List], Optional[Error], Optional[Context]]:
    abs_filepath = osp_abspath(src_filename)
    dir_filepath = osp_dirname(abs_filepath)
    
    with temp_cwd(kwargs.get("cwd", dir_filepath)):
        node, error = generate_ast(src_filename, src_data)
        if error: 
            return None, error, None
        elif not node: 
            return None, None, None
        
        interpreter = Interpreter()
        context = Context(kwargs.get("ctx_name", "__main__"))
        context.symbol_table = setup_starter_symbol_table(__file__=abs_filepath) if src_filename != "<shell>" else shell_symbol_table
        result = interpreter.visit(node, context)
        
        # hey look, it's the walrus operator
        if cnp := kwargs.get("ctx_name_post", False):
            context.name = cnp
        
        return result.value, result.error, context

__all__ = [
    "interpret"
]
