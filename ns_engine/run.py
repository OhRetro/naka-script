from ns_engine.components.lexer import Lexer
from ns_engine.components.parser import Parser
from ns_engine.components.interpreter import Interpreter

from ns_engine.components.context import Context
from ns_engine.components.symbol_table import SymbolTable

global_symbol_table = SymbolTable()
global_symbol_table.set("null", -1)

def execute(src_filename: str, src_data: str):
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
