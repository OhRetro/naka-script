from dataclasses import dataclass, field
from typing import Callable, Self
from .token import Token, TokenType
from .keyword import Keyword
from .node import (Node, NumberNode, 
                   BinOpNode, UnaryOpNode, 
                   VarAssignNode, VarAccessNode)
from .error import Error, ErrorInvalidSyntax
from ..utils.expected import expected

@dataclass(slots=True)
class ParseResult:
    error: Error = field(default=None, init=False)
    node: Node = field(default=None, init=False)
    
    advance_count: int = field(default=0, init=False)
    
    def register_advancement(self):
        self.advance_count += 1
    
    def register(self, result: Self | Node):
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node
    
    def success(self, node: Node):
        self.node = node
        return self

    def failure(self, error: Error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

@dataclass(slots=True)
class Parser:
    tokens: list[Token]
    token_index: int = field(default=-1, init=False)
    current_token: Token = field(default=None, init=False)
    
    def __post_init__(self):
        self.advance()
        
    def advance(self) -> Token:
        self.token_index += 1
        
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            
        return self.current_token
    
    def parse(self):
        response = self.expr()
        
        if not response.error and self.current_token.type != TokenType.EOF:
            return response.failure(ErrorInvalidSyntax(
                expected(TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return response
    
    def atom(self) -> ParseResult:
        p_result = ParseResult()
        token = self.current_token

        if token.type == TokenType.NUMBER:
            p_result.register_advancement()
            self.advance()
            return p_result.success(NumberNode(token))
        
        elif token.type == TokenType.IDENTIFIER:
            p_result.register_advancement()
            self.advance()
            return p_result.success(VarAccessNode(token))
        
        elif token.type == TokenType.LPAREN:
            p_result.register_advancement()
            self.advance()
            expr = p_result.register(self.expr())
            
            if p_result.error: return p_result
            
            if self.current_token.type == TokenType.RPAREN:
                p_result.register_advancement()
                self.advance()
                return p_result.success(expr)
            else:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        return p_result.failure(ErrorInvalidSyntax(
            expected(TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN),
            token.pos_start, token.pos_end
        ))
    
    def power(self) -> ParseResult:
        return self.bin_op((TokenType.POWER, ), self.atom, self.factor)
    
    def factor(self) -> ParseResult:
        p_result = ParseResult()
        token = self.current_token
        
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            p_result.register_advancement()
            self.advance()
            factor = p_result.register(self.factor())
            
            if p_result.error: return p_result
            
            return p_result.success(UnaryOpNode(token, factor))
        
        return self.power()
    
    def term(self) -> ParseResult:
        return self.bin_op((TokenType.MULT, TokenType.DIV), self.factor)
    
    def expr(self) -> ParseResult:
        p_result = ParseResult()
        if self.current_token.is_keyword_of(Keyword.SETVAR):
            p_result.register_advancement()
            self.advance()
            
            if self.current_token.type != TokenType.IDENTIFIER:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
            var_name_token = self.current_token
            p_result.register_advancement()
            self.advance()

            if self.current_token.type != TokenType.EQUALS:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.EQUALS),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
            p_result.register_advancement()
            self.advance()
            expr = p_result.register(self.expr())
            
            if p_result.error: return p_result
                
            return p_result.success(VarAssignNode(var_name_token, expr))
        
        node = p_result.register(self.bin_op((TokenType.PLUS, TokenType.MINUS), self.term))
        
        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.SETVAR, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return p_result.success(node)

    def bin_op(self, operations: tuple, function_a: Callable, function_b: Callable = None) -> ParseResult:
        function_b = function_b or function_a
        
        p_result = ParseResult()
        left = p_result.register(function_a())
        
        if p_result.error: return p_result
    
        while self.current_token.type in operations:
            operation_token = self.current_token
            p_result.register_advancement()
            self.advance()
            right = p_result.register(function_b())
            if p_result.error: return p_result
            left = BinOpNode(operation_token, left, right)
            
        return p_result.success(left)
    