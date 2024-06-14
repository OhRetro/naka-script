from typing import Tuple, List, Optional
from string import ascii_letters as LETTERS
from .token import TokenType, Token
from .keyword import Keyword
from .error import Error, ErrorIllegalCharacter, ErrorExpectedCharacter
from .position import Position

DIGITS = "0123456789"
LETTERS_DIGITS = LETTERS + DIGITS

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
            "/": TokenType.DIV,
            "%": TokenType.MOD,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LSQUARE,
            "]": TokenType.RSQUARE,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            "\n": TokenType.NEWLINE
        }
        
        # Advanced Tokens are tokens that require more complex handling in comparison to Simple Tokens
        ADVANCED_TOKENS = {
            # Check if it's a Mult or Power Token, the rest follow the same rules
            "*": lambda: self._make_token_advanced(TokenType.MULT, ( {"char": "*", "token_type": TokenType.POWER}, )), 
            "-": lambda: self._make_token_advanced(TokenType.MINUS, ( {"char": ">", "token_type": TokenType.RIGHTARROW}, )), 
            
            "=": lambda: self._make_token_advanced(TokenType.EQUALS, ( {"char": "=", "token_type": TokenType.ISEQUALS}, )), 
            "<": lambda: self._make_token_advanced(TokenType.LT, ( {"char": "=", "token_type": TokenType.LTE}, )), 
            ">": lambda: self._make_token_advanced(TokenType.GT, ( {"char": "=", "token_type": TokenType.GTE}, )),
            "!": lambda: self._make_token_advanced(None, ( {"char": "=", "token_type": TokenType.NE, "enforced": True}, )),
            
            '"': lambda: self._make_token_string()
            # "#": lambda: self._make_token_comment()
        }
        
        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
                
            elif self.current_char in DIGITS:
                tokens.append(self._make_token_number())
                
            elif self.current_char in LETTERS:
                tokens.append(self._make_token_identifier())
            
            elif self.current_char in ADVANCED_TOKENS:
                token, error = ADVANCED_TOKENS[self.current_char]()
                
                if error: return None, error
                
                tokens.append(token)
                
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
    
    #! THE ORDER OF THE ITEMS IN THE CONDITIONS TUPLE MATTERS
    def _make_token_advanced(self, start_token_type: TokenType, conditions: tuple[dict]) -> Tuple[Token, None]:
        full_char = self.current_char
        token_type = start_token_type
        pos_start = self.pos.copy()
        self.advance()
        
        for condition in conditions:
            char = condition.get("char")
            
            if self.current_char == char:
                full_char += char
                token_type = condition.get("token_type")
                self.advance()
                
                if condition.get("break", False): break
            
            elif self.current_char != char and condition.get("enforced", False):
                self.advance()
                return None, ErrorExpectedCharacter(
                    f"'{char}' (after '{full_char}')",
                    pos_start, self.pos
                )
        
        if not token_type:
            return None, ErrorExpectedCharacter(
                f"'{conditions[0].get('char')}'",
                pos_start, self.pos
            )
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos), None
    
    def _make_token_number(self) -> Token:
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
                
        number_value = float(number_string) if dot_count else int(number_string)
        return Token(TokenType.NUMBER, number_value, pos_start, self.pos)

    def _make_token_string(self) -> Tuple[Optional[Token], Optional[Error]]:
        string = ""
        pos_start = self.pos.copy()
        escape_character = False
        escape_characters = {
            "n": "\n",
            "t": "\t",
            "\\": "\\",
            '"': '"'
        }
        
        self.advance()
        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:       
                if self.current_char == "\\":
                    escape_character = True
                else:
                    string += self.current_char
                    
            self.advance()
        
        if self.current_char != '"':
            self.advance()
            return None, ErrorExpectedCharacter(
                "'\"'",
                pos_start, self.pos
            )
        
        self.advance()
        
        return Token(TokenType.STRING, string, pos_start, self.pos), None

    def _make_token_identifier(self) -> Token:
        identifier_string = ""
        pos_start = self.pos.copy()
        
        reversed_keyword_map = Keyword._value2member_map_
        
        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            identifier_string += self.current_char
            self.advance()
        
        token_type = TokenType.KEYWORD if identifier_string in reversed_keyword_map else TokenType.IDENTIFIER
        token_value = reversed_keyword_map[identifier_string] if token_type == TokenType.KEYWORD else identifier_string
        
        return Token(token_type, token_value, pos_start, self.pos)
    
    def _make_token_comment(self) -> Tuple[Optional[Token], Optional[Error]]:
        pass