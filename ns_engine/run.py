from ns_engine.components.lexer import Lexer
from ns_engine.components.parser import Parser
from ns_engine.components.interpreter import Interpreter

from ns_engine.components.context import Context

def execute(src_filename: str, src_data: str):
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    
    interpreter = Interpreter()
    context = Context("__main__")
    result = interpreter.visit(ast.node, context)
    
    return result.value, result.error