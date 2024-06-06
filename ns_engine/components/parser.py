from dataclasses import dataclass, field
from typing import Callable, Self
from .token import Token, TokenType
from .node import (Node, NumberNode, 
                   BinOpNode, UnaryOpNode)
from .error import Error, ErrorInvalidSyntax
from ..utils.expected import expected

@dataclass(slots=True)
class ParseResult:
    error: Error = field(default=None, init=False)
    node: Node = field(default=None, init=False)
    
    def register(self, result: Self | Node):
        if isinstance(result, ParseResult):
            if result.error: self.error = result.error
            return result.node
        
        return result
    
    def success(self, node: Node):
        self.node = node
        return self

    def failure(self, error: Error):
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
    
    def factor(self) -> ParseResult:
        response = ParseResult()
        token = self.current_token
        
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            response.register(self.advance())
            factor = response.register(self.factor())
            
            if response.error: return response
            
            return response.success(UnaryOpNode(token, factor))
        
        elif token.type == TokenType.NUMBER:
            response.register(self.advance())
            return response.success(NumberNode(token))
        
        elif token.type == TokenType.LPAREN:
            response.register(self.advance())
            expr = response.register(self.expr())
            
            if response.error: return response
            
            if self.current_token.type == TokenType.RPAREN:
                response.register(self.advance())
                return response.success(expr)
            else:
                return response.failure(ErrorInvalidSyntax(
                    expected(TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        return response.failure(ErrorInvalidSyntax(
            expected(TokenType.NUMBER),
            token.pos_start, token.pos_end
        ))
    
    def term(self) -> ParseResult:
        return self.bin_op((TokenType.MULT, TokenType.DIV), self.factor)
    
    def expr(self) -> ParseResult:
        return self.bin_op((TokenType.PLUS, TokenType.MINUS), self.term)

    def bin_op(self, operations: tuple, function_a: Callable, function_b: Callable = None) -> ParseResult:
        function_b = function_b or function_a
        
        response = ParseResult()
        left = response.register(function_a())
        
        if response.error: return response
    
        while self.current_token.type in operations:
            operation_token = self.current_token
            response.register(self.advance())
            right = response.register(function_b())
            if response.error: return response
            left = BinOpNode(operation_token, left, right)
            
        return response.success(left)