from ns_engine.components.lexer import Lexer

def execute(src_filename: str, src_data: str):
    lexer = Lexer(src_filename, src_data)
    tokens, error = lexer.make_tokens()
    
    return tokens, error
