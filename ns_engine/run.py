from ns_engine.components.lexer import Lexer
from ns_engine.components.parser import Parser

def execute(src_filename: str, src_data: str):
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    
    # return tokens, error
    
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    return ast.node, ast.error