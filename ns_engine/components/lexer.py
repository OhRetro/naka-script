from ..settings import SCRIPT_FILE_EXTENSION
from .error import NSIllegalCharacterError, NSExpectedCharacterError, NSLoadingError, NSInvalidSyntaxError
from .token import TokenType, Token
from .keyword import Keyword
from string import ascii_letters

DIGITS = "0123456789"
LETTERS = ascii_letters
SPECIAL_CHARACTERS = "&|_"
LETTERS_DIGITS = LETTERS + DIGITS

class Lexer:
    def __init__(self, filename: str, text: str):
        self.filename = filename
        self.text = text
        
        self.current_char: str = None
        
        self.index: int = 0
        self.column: int = 0
        self.line: int = 0
        
        self.advance()

    def advance(self):
        self.index += 1
        self.column += 1
        
        self.current_char = self.text[self.index] if self.index < len(self.text) else None
        
        if self.current_char == "\n":
            self.line += 1
            self.column = 0
    
    def make_tokens(self):
        tokens = []
        
        if not self.filename.endswith(f".{SCRIPT_FILE_EXTENSION}"):
            return None, NSLoadingError(f"Script file extension must be .{SCRIPT_FILE_EXTENSION}", self.filename, self.line)
        
        basic_tokens = {
            TokenType.LPAREN.value: TokenType.LPAREN,
            TokenType.RPAREN.value: TokenType.RPAREN,
            TokenType.LSQUARE.value: TokenType.LSQUARE,
            TokenType.RSQUARE.value: TokenType.RSQUARE,
            TokenType.LBRACE.value: TokenType.LBRACE,
            TokenType.RBRACE.value: TokenType.RBRACE,
            TokenType.COMMA.value: TokenType.COMMA,
            TokenType.NEWLINE.value: TokenType.NEWLINE,
            TokenType.SEMICOLON.value: TokenType.SEMICOLON,
            TokenType.COLON.value: TokenType.COLON,
            TokenType.DOT.value: TokenType.DOT,
        }
        
        advanced_tokens = {
            TokenType.PLUS.value: self.make_plus, # Also checks for '+='
            TokenType.MINUS.value: self.make_minus, # Also checks for '->', '-='
            TokenType.MULT.value: self.make_multiplier, # Also checks for '*=', '**', '**='
            TokenType.DIV.value: self.make_div, # Also checks for '/='
            TokenType.DIVREST.value: self.make_divrest, # Also checks for '%='
            TokenType.EQUALS.value: self.make_equals, # Also checks for '=='
            TokenType.LT.value: self.make_less_than, # Also checks for '<='
            TokenType.GT.value: self.make_greater_than, # Also checks for '>='
            "!": self.make_not_equals,
            TokenType.STRING.value: self.make_string
        }
        
        no_return_tokens = {
            TokenType.COMMENT.value: self.skip_comment # Also checks for comment blocks
        }
        
        while self.current_char != None:
            if self.current_char in [" ", "\t"]:
                self.advance()
                
            elif self.current_char in LETTERS or self.current_char in SPECIAL_CHARACTERS:
                token, error = self.make_identifier()
                if error: return None, error
                tokens.append(token)
                
            elif self.current_char in DIGITS:
                token, error = self.make_number()
                if error: return None, error
                tokens.append(token)
                
            elif self.current_char in basic_tokens:
                tokens.append(Token(basic_tokens[self.current_char]))
                self.advance()

            elif self.current_char in advanced_tokens:
                token, error = advanced_tokens[self.current_char]()
                if error: return None, error
                tokens.append(token)

            elif self.current_char in no_return_tokens:
                no_return_tokens[self.current_char]()
                
            else:
                return None, NSIllegalCharacterError(f"'{self.current_char}'", self.filename, self.line)

        tokens.append(Token(TokenType.EOF))
        return tokens, None

    def make_plus(self):
        token_type = TokenType.PLUS
        self.advance()
        
        # if self.current_char == TokenType.EQUALS.value:
        #         token_type = TokenType.PLUSE
        #         self.advance()
            
        return Token(token_type), None
    
    def make_minus(self):
        token_type = TokenType.MINUS
        self.advance()
        
        if self.current_char == TokenType.ARROW.value[-1]:
            token_type = TokenType.ARROW
            self.advance()
            
        # elif self.current_char == TokenType.EQUALS.value:
        #     token_type = TokenType.MINUSE
        #     self.advance()
            
        return Token(token_type), None
    
    def make_multiplier(self):
        token_type = TokenType.MULT
        self.advance()
        
        if self.current_char == TokenType.MULT.value:
            token_type = TokenType.POWER
            self.advance()
            
        #     if self.current_char == TokenType.EQUALS.value:
        #         token_type = TokenType.POWERE
        #         self.advance()
                
        # elif self.current_char == TokenType.EQUALS.value:
        #     token_type = TokenType.MULE
        #     self.advance()
            
        return Token(token_type), None
    
    def make_div(self):
        token_type = TokenType.DIV
        self.advance()
        
        # if self.current_char == TokenType.EQUALS.value:
        #     token_type = TokenType.DIVE
        #     self.advance()
            
        return Token(token_type), None
    
    def make_divrest(self):
        token_type = TokenType.DIVREST
        self.advance()
        
        # if self.current_char == TokenType.EQUALS.value:
        #     token_type = TokenType.DIVRESTE
        #     self.advance()
            
        return Token(token_type), None
    
    def make_number(self):
        num_str = ""
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
                
            else: # if self.current_char in DIGITS:
                num_str += self.current_char
                
            self.advance()

        if dot_count == 0:
            return Token(TokenType.NUMBER, int(num_str)), None
        else:
            return Token(TokenType.NUMBER, float(num_str)), None

    def make_string(self):
        string = ""
        escape_char = False
        self.advance()

        escape_chars = {
            "n": "\n",   # Newline
            "t": "\t",   # Tab
            "\\": "\\",  # Backslash
            "\"": "\"",  # Double quote
        }

        while self.current_char != None and (self.current_char != TokenType.STRING.value or escape_char):
            if escape_char:
                string += escape_chars.get(self.current_char, "")
                escape_char = False
                
            else:
                if self.current_char == "\\":
                    escape_char = True
                    
                else:
                    string += self.current_char
                    
            self.advance()
            
        #self.advance()
        return Token(TokenType.STRING, string), None

    def make_identifier(self):
        identifier_string = ""
        
        reversed_keyword_dict = Keyword._value2member_map_
        
        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_" + SPECIAL_CHARACTERS:
            identifier_string += self.current_char
            
            if identifier_string[0] in DIGITS:
                return None, NSInvalidSyntaxError("Identifiers must not begin with a digit", self.filename, self.line)
            
            self.advance()
            
        token_type = TokenType.KEYWORD if identifier_string in reversed_keyword_dict else TokenType.IDENTIFIER
        token_value = reversed_keyword_dict.get(identifier_string, identifier_string)
        
        return Token(token_type,token_value), None

    def make_equals(self):
        token_type = TokenType.EQUALS
        self.advance()
        
        if self.current_char == TokenType.EQUALS.value:
            token_type = TokenType.EE
            self.advance()
            
        return Token(token_type), None
            
    def make_not_equals(self):
        self.advance()
        
        if self.current_char != TokenType.EQUALS.value:
            # self.advance()
            return None, NSExpectedCharacterError("'=' (after '!')", self.filename, self.line)
        
        self.advance()
        return Token(TokenType.NE), None
    
    def make_less_than(self):
        token_type = TokenType.LT
        self.advance()
        
        if self.current_char == TokenType.EQUALS.value:
            token_type = TokenType.LTE
            self.advance()
            
        return Token(token_type), None

    def make_greater_than(self):
        token_type = TokenType.GT
        self.advance()
        
        if self.current_char == TokenType.EQUALS.value:
            token_type = TokenType.GTE
            self.advance()
            
        return Token(token_type), None
            
    def skip_comment(self):
        sign_count = 0
        for _ in range(3):
            if self.current_char == TokenType.COMMENT.value:
                sign_count += 1
            self.advance()
            if self.current_char != TokenType.COMMENT.value: break
        
        block_mode = sign_count == 3
        check_pass = 0
        
        while True:
            self.advance()
            
            if not block_mode:
                if self.current_char is None or self.current_char == TokenType.NEWLINE.value: break
                
            else:
                if self.current_char == TokenType.COMMENT.value:
                    check_pass += 1
                elif check_pass >= 3: break
                else: check_pass = 0
            
                if self.current_char is None: break

        self.advance()
        