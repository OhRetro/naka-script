from ns_engine.components.lexer import Lexer
from ns_engine.components.parser import Parser
from ns_engine.components.interpreter import Interpreter

def execute(src_filename: str, src_data: str):
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    
    # return tokens, error
    
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    if ast.error: return None, ast.error
    
    interpreter = Interpreter()
    result = interpreter.visit(ast.node)
    
    #return ast.node, ast.error
    return result, None