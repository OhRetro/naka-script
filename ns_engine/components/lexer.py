from typing import Tuple, List, Optional
from .token import TokenType, Token
from .error import Error, ErrorIllegalCharacter
from .position import Position

DIGITS = "0123456789"

class Lexer:
    def __init__(self, source_name: str, source_code: str):
        self.src_name = source_name
        self.src_code = source_code
        self.pos = Position(-1, 0, -1, source_name, source_code)
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.src_code[self.pos.index] if self.pos.index < len(self.src_code) else None
        
    def make_tokens(self) -> Tuple[Optional[List[Token]], Optional[Error]]:
        tokens: list[Token] = []
        
        SIMPLE_TOKENS = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "/": TokenType.DIV,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LSQUARE,
            "]": TokenType.RSQUARE,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
        }
        
        ADVANCED_TOKENS = {
            # Check if it's a Mult or Power Token
            "*": lambda: self._make_token_advanced(TokenType.MULT, ( ("*", TokenType.POWER), )), 
        }
        
        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_token_number())
            elif self.current_char in ADVANCED_TOKENS:
                tokens.append(ADVANCED_TOKENS[self.current_char]())
            elif self.current_char in SIMPLE_TOKENS:
                tokens.append(Token(SIMPLE_TOKENS[self.current_char], pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                illegal_char = self.current_char
                self.advance()
                return None, ErrorIllegalCharacter(f"'{illegal_char}'", pos_start, self.pos)
        
        tokens.append(Token(TokenType.EOF, pos_start=self.pos))
        return tokens, None
    
    def make_token_number(self) -> Token:
        number_string = ""
        dot_count = 0
        pos_start = self.pos.copy()
        
        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1: break
                dot_count += 1
                number_string += "."
            else:
                number_string += self.current_char
            
            self.advance()
                
        if dot_count:
            return Token(TokenType.NUMBER, float(number_string), pos_start, self.pos)
        else:
            return Token(TokenType.NUMBER, int(number_string), pos_start, self.pos)
    
    #! THE ORDER OF THE ITEMS IN THE CONDITIONS TUPLE MATTERS
    def _make_token_advanced(self, start_token_type: TokenType, conditions: tuple) -> Token:
        token_type = start_token_type
        pos_start = self.pos.copy()
        
        self.advance()
        
        for condition in conditions:
            condition_char = condition[0]
            condition_token_type = condition[1]
            
            if self.current_char == condition_char:
                token_type = condition_token_type
                self.advance()
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    