from dataclasses import dataclass, field
from typing import Callable, Self
from .token import Token, TokenType
from .keyword import Keyword
from .node import (Node, 
                   NumberNode, StringNode,
                   BinOpNode, UnaryOpNode, 
                   IfNode, ForNode, WhileNode,
                   FuncDefNode, CallNode,
                   VarAssignNode, VarAccessNode)
from .error import Error, ErrorInvalidSyntax
from ..utils.expected import expected
from ..utils.debug import DebugMessage

debug_message = DebugMessage()

@dataclass(slots=True)
class ParseResult:
    error: Error = field(default=None, init=False)
    node: Node = field(default=None, init=False)
    
    last_registered_advance_count: int = field(default=0, init=False)
    advance_count: int = field(default=0, init=False)
    
    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1
    
    def register(self, result: Self) -> Node:
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node
    
    def success(self, node: Node) -> Self:
        self.node = node
        return self

    def failure(self, error: Error) -> Self:
        if not self.error or self.last_registered_advance_count == 0:
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
    
    def parse(self) -> ParseResult:
        response = self.expr()
        
        if not response.error and self.current_token.type != TokenType.EOF:
            return response.failure(ErrorInvalidSyntax(
                expected(TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return response

    #!================================================================

    def atom(self) -> ParseResult:
        p_result = ParseResult()
        token = self.current_token

        if token.type == TokenType.NUMBER:
            p_result.register_advancement()
            self.advance()
            return p_result.success(NumberNode(token))
 
        elif token.type == TokenType.STRING:
            p_result.register_advancement()
            self.advance()
            return p_result.success(StringNode(token))
               
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
                
        elif token.is_keyword_of(Keyword.IF):
            if_expr = p_result.register(self.if_expr())
            if p_result.error: return p_result
            return p_result.success(if_expr)

        elif token.is_keyword_of(Keyword.FOR):
            for_expr = p_result.register(self.for_expr())
            if p_result.error: return p_result
            return p_result.success(for_expr)
        
        elif token.is_keyword_of(Keyword.WHILE):
            while_expr = p_result.register(self.while_expr())
            if p_result.error: return p_result
            return p_result.success(while_expr)

        elif token.is_keyword_of(Keyword.SETFUNCTION):
            func_def = p_result.register(self.func_def())
            if p_result.error: return p_result
            return p_result.success(func_def)
        
        return p_result.failure(ErrorInvalidSyntax(
            expected(TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN,
                     Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION),
            token.pos_start, token.pos_end
        ))

    def call(self) -> ParseResult:
        p_result = ParseResult()
        atom: Node = p_result.register(self.atom())
        if p_result.error: return p_result
        
        if self.current_token.type == TokenType.LPAREN:
            p_result.register_advancement()
            self.advance()
            
            arg_nodes: list[Node] = []
            
            if self.current_token.type == TokenType.RPAREN:
                p_result.register_advancement()
                self.advance()
            
            else:
                arg_nodes.append(p_result.register(self.expr()))
                
                if p_result.error: 
                    return p_result.failure(ErrorInvalidSyntax(
                        expected(TokenType.RPAREN, Keyword.SETVAR, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, Keyword.NOT),
                        self.current_token.pos_start, self.current_token.pos_end
                    ))
                    
                while self.current_token.type == TokenType.COMMA:
                    p_result.register_advancement()
                    self.advance()
                    
                    arg_nodes.append(p_result.register(self.expr()))
                    if p_result.error: return p_result
                    
                if self.current_token.type != TokenType.RPAREN:
                    return p_result.failure(ErrorInvalidSyntax(
                        expected(TokenType.COMMA, TokenType.RPAREN),
                        self.current_token.pos_start, self.current_token.pos_end
                    ))
                    
                p_result.register_advancement()
                self.advance()
                
            return p_result.success(CallNode(atom, arg_nodes))
        
        return p_result.success(atom)

    def power(self) -> ParseResult:
        return self.bin_op((TokenType.POWER, ), self.call, self.factor)
    
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
        return self.bin_op((TokenType.MULT, TokenType.DIV, TokenType.MOD), self.factor)

    def arith_expr(self) -> ParseResult:
        return self.bin_op((TokenType.PLUS, TokenType.MINUS), self.term)
        
    def comp_expr(self) -> ParseResult:
        p_result = ParseResult()
        
        if self.current_token.is_keyword_of(Keyword.NOT):
            operation_token = self.current_token
            p_result.register_advancement()
            self.advance()
            
            node = p_result.register(self.comp_expr())
            if p_result.error: return p_result
            return p_result.success(UnaryOpNode(operation_token, node))
        
        node = p_result.register(self.bin_op(
            (TokenType.EE, TokenType.NE,
             TokenType.LT, TokenType.GT, 
             TokenType.LTE, TokenType.GTE), 
            self.arith_expr))
        
        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, Keyword.NOT),
                self.current_token.pos_start, self.current_token.pos_end
            ))
            
        return p_result.success(node)

    def if_expr(self) -> ParseResult:
        p_result = ParseResult()
        cases: list[tuple[Node, Node]] = []
        else_case = None

        if not self.current_token.is_keyword_of(Keyword.IF):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.IF),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()

        condition = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()

        expr = p_result.register(self.expr())
        if p_result.error: return p_result
        cases.append((condition, expr))

        while self.current_token.is_keyword_of(Keyword.ELSEIF):
            p_result.register_advancement()
            self.advance()

            condition = p_result.register(self.expr())
            if p_result.error: return p_result

            if not self.current_token.is_keyword_of(Keyword.THEN):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(Keyword.THEN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))

            p_result.register_advancement()
            self.advance()

            expr = p_result.register(self.expr())
            if p_result.error: return p_result
            cases.append((condition, expr))

        if self.current_token.is_keyword_of(Keyword.ELSE):
            p_result.register_advancement()
            self.advance()

            else_case: Node = p_result.register(self.expr())
            if p_result.error: return p_result

        return p_result.success(IfNode(cases, else_case))

    def for_expr(self) -> ParseResult:
        p_result = ParseResult()

        if not self.current_token.is_keyword_of(Keyword.FOR):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.FOR),
                self.current_token.pos_start, self.current_token.pos_end
            ))

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

        start_value_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.TO):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.TO),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        p_result.register_advancement()
        self.advance()

        end_value_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if self.current_token.is_keyword_of(Keyword.STEP):
            p_result.register_advancement()
            self.advance()

            step_value_node: Node = p_result.register(self.expr())
            if p_result.error: return p_result
        else:
            step_value_node = None

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()

        body_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        return p_result.success(ForNode(var_name_token, start_value_node, end_value_node, step_value_node, body_node))

    def while_expr(self) -> ParseResult:
        p_result = ParseResult()

        if not self.current_token.is_keyword_of(Keyword.WHILE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.WHILE),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()

        condition_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()

        body_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        return p_result.success(WhileNode(condition_node, body_node))

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
        
        node = p_result.register(self.bin_op((Keyword.AND, Keyword.OR), self.comp_expr))
        
        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.SETVAR, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, Keyword.NOT,
                         Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return p_result.success(node)

    def func_def(self) -> ParseResult:
        p_result = ParseResult()
        
        if not self.current_token.is_keyword_of(Keyword.SETFUNCTION):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.SETFUNCTION),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        p_result.register_advancement()
        self.advance()
        
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name_token = self.current_token
            
            p_result.register_advancement()
            self.advance()
            
            if self.current_token.type != TokenType.LPAREN:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.LPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        else:
            var_name_token = None
            if self.current_token.type != TokenType.LPAREN:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER, TokenType.LPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        p_result.register_advancement()
        self.advance()
        
        arg_name_tokens: list[Token] = []
        
        if self.current_token.type == TokenType.IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            
            p_result.register_advancement()
            self.advance()
            
            while self.current_token.type == TokenType.COMMA:
                p_result.register_advancement()
                self.advance()
                
                if self.current_token.type != TokenType.IDENTIFIER:
                    return p_result.failure(ErrorInvalidSyntax(
                        expected(TokenType.IDENTIFIER),
                        self.current_token.pos_start, self.current_token.pos_end
                    ))
                    
                arg_name_tokens.append(self.current_token)
                
                p_result.register_advancement()
                self.advance()
                
            if self.current_token.type != TokenType.RPAREN:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.COMMA, TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        else:
            if self.current_token.type != TokenType.RPAREN:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER, TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        p_result.register_advancement()
        self.advance()
        
        if self.current_token.type != TokenType.ARROW:
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.ARROW),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        p_result.register_advancement()
        self.advance()
        
        node_to_return: Node = p_result.register(self.expr())
        
        if p_result.error: return p_result
        
        return p_result.success(FuncDefNode(var_name_token, arg_name_tokens, node_to_return))
    
    #!================================================================
    
    def bin_op(self, operations: tuple, function_a: Callable, function_b: Callable = None) -> ParseResult:
        function_b = function_b or function_a

        p_result = ParseResult()
        left = p_result.register(function_a())
        
        if p_result.error: return p_result

        while self.current_token.type in operations or (self.current_token.type == TokenType.KEYWORD and self.current_token.value in operations):
            operation_token = self.current_token
            p_result.register_advancement()
            self.advance()
            right = p_result.register(function_b())
            if p_result.error: return p_result
            left = BinOpNode(operation_token, left, right)
            
        return p_result.success(left)
    