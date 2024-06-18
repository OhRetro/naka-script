from dataclasses import dataclass, field
from typing import Callable, Self, Optional
from .token import Token, TokenType
from .keyword import Keyword
from .node import (Node, 
                   NumberNode, StringNode, ListNode, DictNode,
                   BinOpNode, UnaryOpNode, 
                   IfNode, ForNode, WhileNode,
                   FuncDefNode, CallNode,
                   VarAssignNode, VarAccessNode, VarDeleteNode, VarUpdateNode,
                   ReturnNode, ContinueNode, BreakNode, IndexNode, AccessNode)
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
    to_reverse_count: int = field(default=0, init=False)
    
    def __repr__(self) -> str:
        if self.error:
            return f"ParseResult({self.error})"
        elif self.node:
            return f"ParseResult({self.node})"
        else:
            return f"ParseResult()"
    
    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1
    
    def register(self, result: Self) -> Node:
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node
    
    def try_register(self, result: Self) -> Optional[Node]:
        if result.error:
            self.to_reverse_count = result.advance_count
            return None
        return self.register(result)
    
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
        self.update_current_token()
        return self.current_token
    
    def reverse(self, amount: int = 1) -> Token:
        self.token_index -= amount
        self.update_current_token()
        return self.current_token
    
    def update_current_token(self):
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
               
    def parse(self) -> ParseResult:
        p_result = self.statements()
        
        if not p_result.error and not self.current_token.is_type_of(TokenType.EOF):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV, TokenType.POWER, TokenType.MOD,
                         TokenType.ISEQUALS, TokenType.NE, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE,
                         Keyword.AND, Keyword.OR),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return p_result
    
    def current_token_is_semicolon_or_newline(self) -> bool:
        return self.current_token.is_type_of(TokenType.SEMICOLON, TokenType.NEWLINE)

    # def next_token_is_type_of(self, type: TokenType) -> bool:
    #     try:
    #         return self.tokens[self.token_index + 1].is_type_of(type)
    #     except IndexError:
    #         return False
    
    def advance_if_token_is_semicolon_or_newline(self, parse_result: ParseResult) -> int:
        semicolon_newline_count = 0
        while self.current_token_is_semicolon_or_newline():
            parse_result.register_advancement()
            self.advance()
            semicolon_newline_count += 1
            
        return semicolon_newline_count
    
    def advance_register_advancement(self, parse_result: ParseResult, skip_semicolon_newline: bool):
        parse_result.register_advancement()
        self.advance()
        advance_count = 1
        
        if skip_semicolon_newline: 
            advance_count += self.advance_if_token_is_semicolon_or_newline(parse_result)
            
        return advance_count

    #!================================================================

    def atom(self) -> ParseResult:
        p_result = ParseResult()
        token = self.current_token

        if token.is_type_of(TokenType.NUMBER):
            self.advance_register_advancement(p_result, False)
            return p_result.success(NumberNode(token))
 
        elif token.is_type_of(TokenType.STRING):
            self.advance_register_advancement(p_result, False)
            return p_result.success(StringNode(token))
               
        elif token.is_type_of(TokenType.IDENTIFIER):
            self.advance_register_advancement(p_result, False)
            
            if self.current_token.is_type_of(TokenType.EQUALS):
                var_name_token = token
            
                self.advance_register_advancement(p_result, False)
                
                expr = p_result.register(self.expr())
                
                if p_result.error: return p_result
                    
                return p_result.success(VarUpdateNode(var_name_token, expr))
            else:
                return p_result.success(VarAccessNode(token))
        
        elif token.is_type_of(TokenType.LPAREN):
            self.advance_register_advancement(p_result, False)
            
            expr = p_result.register(self.expr())
            
            if p_result.error: return p_result
            
            if self.current_token.is_type_of(TokenType.RPAREN):
                self.advance_register_advancement(p_result, False)
                
                return p_result.success(expr)
            else:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
        elif token.is_type_of(TokenType.LSQUARE):
            list_expr = p_result.register(self.list_expr())
            if p_result.error: return p_result
            return p_result.success(list_expr)

        elif token.is_type_of(TokenType.LBRACE):
            dict_expr = p_result.register(self.dict_expr())
            if p_result.error: return p_result
            return p_result.success(dict_expr)
                              
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
            expected(TokenType.STRING, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, 
                     TokenType.LPAREN, TokenType.LSQUARE,
                     Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION),
            token.pos_start, token.pos_end
        ))

    def call(self) -> ParseResult:
        p_result = ParseResult()
        
        atom: Node = p_result.register(self.atom())
        if p_result.error: return p_result

        while True:
            if self.current_token.is_type_of(TokenType.LPAREN):
                self.advance_register_advancement(p_result, True)
                
                arg_nodes: list[Node] = []

                if self.current_token.is_type_of(TokenType.RPAREN):
                    self.advance_register_advancement(p_result, False)
                    
                else:
                    def get_arguments():
                        arg_nodes.append(p_result.register(self.expr()))
                        if p_result.error:
                            return p_result.failure(
                                ErrorInvalidSyntax(
                                    expected(TokenType.RPAREN, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, 
                                             TokenType.LPAREN, TokenType.LSQUARE,
                                             Keyword.SETVAR, Keyword.NOT, Keyword.IF,
                                             Keyword.WHILE, Keyword.FOR, Keyword.SETFUNCTION),
                                    self.current_token.pos_start, self.current_token.pos_end
                                )
                            )
                            
                        self.advance_if_token_is_semicolon_or_newline(p_result)
                    
                    if get_arguments(): return p_result
                    while self.current_token.is_type_of(TokenType.COMMA):
                        self.advance_register_advancement(p_result, True)
                        if get_arguments(): return p_result

                    if not self.current_token.is_type_of(TokenType.RPAREN):
                        return p_result.failure(
                            ErrorInvalidSyntax(
                                expected(TokenType.COMMA, TokenType.RPAREN),
                                self.current_token.pos_start, self.current_token.pos_end
                            )
                        )

                    self.advance_register_advancement(p_result, False)

                atom = CallNode(atom, arg_nodes)

            elif self.current_token.is_type_of(TokenType.LSQUARE):
                self.advance_register_advancement(p_result, False)
                
                index_node: Node = p_result.register(self.expr())
                if p_result.error: return p_result

                if not self.current_token.is_type_of(TokenType.RSQUARE):
                    return p_result.failure(
                        ErrorInvalidSyntax(
                            expected(TokenType.RSQUARE),
                            self.current_token.pos_start, self.current_token.pos_end
                        )
                    )

                self.advance_register_advancement(p_result, False)
                atom = IndexNode(atom, index_node)

            elif self.current_token.is_type_of(TokenType.DOT):
                self.advance_register_advancement(p_result, False)
                
                if not self.current_token.is_type_of(TokenType.IDENTIFIER):
                    return p_result.failure(
                        ErrorInvalidSyntax(
                            expected(TokenType.IDENTIFIER),
                            self.current_token.pos_start, self.current_token.pos_end
                        )
                    )
                    
                attribute_name_token = self.current_token

                self.advance_register_advancement(p_result, False)
                atom = AccessNode(attribute_name_token, atom)
                
            else:
                break

        return p_result.success(atom)

    def power(self) -> ParseResult:
        return self.bin_op((TokenType.POWER, ), self.call, self.factor)
    
    def factor(self) -> ParseResult:
        p_result = ParseResult()
        token = self.current_token
        
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self.advance_register_advancement(p_result, False)
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
            self.advance_register_advancement(p_result, False)
            
            node = p_result.register(self.comp_expr())
            if p_result.error: return p_result
            return p_result.success(UnaryOpNode(operation_token, node))
        
        node = p_result.register(self.bin_op(
            (TokenType.ISEQUALS, TokenType.NE,
             TokenType.LT, TokenType.GT, 
             TokenType.LTE, TokenType.GTE), 
            self.arith_expr))

        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LSQUARE,
                         Keyword.NOT),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return p_result.success(node)

    def list_expr(self) -> ParseResult:
        p_result = ParseResult()
        element_nodes: list[Node] = []
        pos_start = self.current_token.pos_start.copy()
        
        if not self.current_token.is_type_of(TokenType.LSQUARE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.LSQUARE),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, True)
        
        if self.current_token.is_type_of(TokenType.RSQUARE):
            self.advance_register_advancement(p_result, False)
            return p_result.success(ListNode(pos_start, self.current_token.pos_end.copy(), element_nodes))
        
        def get_elements():
            element_nodes.append(p_result.register(self.expr()))
            
            if p_result.error:
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, 
                                TokenType.LPAREN, TokenType.LSQUARE,
                            Keyword.SETVAR, Keyword.NOT, Keyword.IF,
                            Keyword.WHILE, Keyword.FOR, Keyword.SETFUNCTION),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
            
            self.advance_if_token_is_semicolon_or_newline(p_result)
        
        if get_elements(): return p_result
        while self.current_token.is_type_of(TokenType.COMMA):
            self.advance_register_advancement(p_result, True)
            if get_elements(): return p_result
            
        if not self.current_token.is_type_of(TokenType.RSQUARE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.COMMA, TokenType.RSQUARE),
                self.current_token.pos_start, self.current_token.pos_end
            ))
            
        self.advance_register_advancement(p_result, False)

        return p_result.success(ListNode(pos_start, self.current_token.pos_end.copy(), element_nodes))
    
    def dict_expr(self) -> ParseResult:
        p_result = ParseResult()
        key_tokens: list[Token] = []
        value_nodes: list[Node] = []
        pos_start = self.current_token.pos_start.copy()
        
        if not self.current_token.is_type_of(TokenType.LBRACE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.LBRACE),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, True)
        
        if self.current_token.is_type_of(TokenType.RBRACE):
            self.advance_register_advancement(p_result, False)
            return p_result.success(DictNode(pos_start, self.current_token.pos_end.copy(), key_tokens, value_nodes))
        
        def get_key_value():
            if not self.current_token.is_type_of(TokenType.IDENTIFIER):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
            
            key_tokens.append(self.current_token)
            
            self.advance_register_advancement(p_result, True)
            
            if not self.current_token.is_type_of(TokenType.COLON):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.COLON),
                    self.current_token.pos_start, self.current_token.pos_end
                ))

            self.advance_register_advancement(p_result, True)
            
            value_nodes.append(p_result.register(self.expr()))
            
            if p_result.error: 
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.RBRACE, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER,
                            TokenType.LBRACE, TokenType.LPAREN,
                            Keyword.SETVAR, Keyword.NOT, Keyword.IF,
                            Keyword.WHILE, Keyword.FOR, Keyword.SETFUNCTION),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
            
            self.advance_if_token_is_semicolon_or_newline(p_result)
        
        if get_key_value(): return p_result
        while self.current_token.is_type_of(TokenType.COMMA):
            self.advance_register_advancement(p_result, True)
            if get_key_value(): return p_result
        
        if not self.current_token.is_type_of(TokenType.RBRACE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.COMMA, TokenType.RBRACE),
                self.current_token.pos_start, self.current_token.pos_end
            ))
            
        self.advance_register_advancement(p_result, False)

        return p_result.success(DictNode(pos_start, self.current_token.pos_end.copy(), key_tokens, value_nodes))

    def if_expr(self) -> ParseResult:
        p_result = ParseResult()
        all_cases = p_result.register(self.if_expr_cases(Keyword.IF))
        if p_result.error: return p_result
        cases, else_case = all_cases
        return p_result.success(IfNode(cases, else_case, True))

    def if_expr_elseif(self) -> ParseResult:
        return self.if_expr_cases(Keyword.ELSEIF)
        
    def if_expr_else(self) -> ParseResult:
        p_result = ParseResult()
        else_case = None

        if self.current_token.is_keyword_of(Keyword.ELSE):
            self.advance_register_advancement(p_result, False)

            if self.current_token_is_semicolon_or_newline():
                self.advance_register_advancement(p_result, False)

                statements = p_result.register(self.statements())
                if p_result.error: return p_result
                else_case = (statements, True)

                if self.current_token.is_keyword_of(Keyword.END):
                    self.advance_register_advancement(p_result, False)
                else:
                    return p_result.failure(ErrorInvalidSyntax(
                        expected(Keyword.END),
                        self.current_token.pos_start, self.current_token.pos_end
                    ))
            else:
                expr = p_result.register(self.statement())
                if p_result.error: return p_result
                else_case = (expr, False)

        return p_result.success(else_case)

    def if_expr_elseif_or_else(self) -> ParseResult:
        p_result = ParseResult()
        cases, else_case = [], None

        if self.current_token.is_keyword_of(Keyword.ELSEIF):
            all_cases = p_result.register(self.if_expr_elseif())
            if p_result.error: return p_result
            cases, else_case = all_cases
        else:
            else_case = p_result.register(self.if_expr_else())
            if p_result.error: return p_result
        
        return p_result.success((cases, else_case))

    def if_expr_cases(self, case_keyword: Keyword) -> ParseResult:
        p_result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.is_keyword_of(case_keyword):
            return p_result.failure(ErrorInvalidSyntax(
                expected(case_keyword),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        condition = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        if self.current_token_is_semicolon_or_newline():
            self.advance_register_advancement(p_result, False)

            statements = p_result.register(self.statements())
            if p_result.error: return p_result
            cases.append((condition, statements, True))

            if self.current_token.is_keyword_of(Keyword.END):
                self.advance_register_advancement(p_result, False)
            else:
                all_cases = p_result.register(self.if_expr_elseif_or_else())
                if p_result.error: return p_result
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = p_result.register(self.statement())
            if p_result.error: return p_result
            cases.append((condition, expr, False))

            all_cases = p_result.register(self.if_expr_elseif_or_else())
            if p_result.error: return p_result
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return p_result.success((cases, else_case))

    def for_expr(self) -> ParseResult:
        p_result = ParseResult()

        if not self.current_token.is_keyword_of(Keyword.FOR):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.FOR),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        if not self.current_token.is_type_of(TokenType.IDENTIFIER):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.IDENTIFIER),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        var_name_token = self.current_token
        self.advance_register_advancement(p_result, False)

        if not self.current_token.is_type_of(TokenType.EQUALS):
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.EQUALS),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        self.advance_register_advancement(p_result, False)

        start_value_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.TO):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.TO),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        self.advance_register_advancement(p_result, False)

        end_value_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if self.current_token.is_keyword_of(Keyword.STEP):
            self.advance_register_advancement(p_result, False)

            step_value_node: Node = p_result.register(self.expr())
            if p_result.error: return p_result
        else:
            step_value_node = None

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)
        
        if self.current_token_is_semicolon_or_newline():
            self.advance_register_advancement(p_result, False)

            body_node = p_result.register(self.statements())
            if p_result.error:
                return p_result

            if not self.current_token.is_keyword_of(Keyword.END):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(Keyword.END),
                    self.current_token.pos_start, self.current_token.pos_end
                ))

            self.advance_register_advancement(p_result, False)

            return p_result.success(ForNode(var_name_token, start_value_node, end_value_node, step_value_node, body_node, True))

        body_node: Node = p_result.register(self.statement())
        if p_result.error: return p_result

        return p_result.success(ForNode(var_name_token, start_value_node, end_value_node, step_value_node, body_node, False))

    def while_expr(self) -> ParseResult:
        p_result = ParseResult()

        if not self.current_token.is_keyword_of(Keyword.WHILE):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.WHILE),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        condition_node: Node = p_result.register(self.expr())
        if p_result.error: return p_result

        if not self.current_token.is_keyword_of(Keyword.THEN):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.THEN),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        if self.current_token_is_semicolon_or_newline():
            self.advance_register_advancement(p_result, False)

            body_node = p_result.register(self.statements())
            if p_result.error: return p_result

            if not self.current_token.is_keyword_of(Keyword.END):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(Keyword.END),
                    self.current_token.pos_start, self.current_token.pos_end
                ))

            self.advance_register_advancement(p_result, False)

            return p_result.success(WhileNode(condition_node, body_node, True))

        body_node: Node = p_result.register(self.statement())
        if p_result.error: return p_result

        return p_result.success(WhileNode(condition_node, body_node, False))

    def expr(self) -> ParseResult:
        p_result = ParseResult()
        
        if self.current_token.is_keyword_of(Keyword.SETVAR, Keyword.SETIMMUTABLEVAR):
            set_var_keyword = self.current_token.value
            self.advance_register_advancement(p_result, False)
            
            if not self.current_token.is_type_of(TokenType.IDENTIFIER):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
            var_name_token = self.current_token
            self.advance_register_advancement(p_result, False)

            if not self.current_token.is_type_of(TokenType.EQUALS):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.EQUALS),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
            self.advance_register_advancement(p_result, False)
            expr = p_result.register(self.expr())
            
            if p_result.error: return p_result
            
            symbols_dict_type = {
                Keyword.SETVAR: "symbols",
                Keyword.SETIMMUTABLEVAR: "immutable_symbols",
                #Keyword.SETLOCALVAR: "local_symbols"
            }
                
            return p_result.success(VarAssignNode(var_name_token, expr, symbols_dict_type.get(set_var_keyword)))
        
        elif self.current_token.is_keyword_of(Keyword.DELETEVAR):
            self.advance_register_advancement(p_result, False)
            
            if not self.current_token.is_type_of(TokenType.IDENTIFIER):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
                
            var_name_token = self.current_token
            self.advance_register_advancement(p_result, False)
            
            return p_result.success(VarDeleteNode(var_name_token))
        
        node = p_result.register(self.bin_op((Keyword.AND, Keyword.OR), self.comp_expr))
        
        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.SETVAR, Keyword.DELETEVAR, TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LSQUARE, Keyword.NOT,
                         Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION),
                self.current_token.pos_start, self.current_token.pos_end
            ))
        
        return p_result.success(node)
    
    def statement(self) -> ParseResult:
        p_result = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        
        if self.current_token.is_keyword_of(Keyword.RETURN):
            self.advance_register_advancement(p_result, False)
            
            expr = p_result.try_register(self.expr())
            
            if not expr:
                self.reverse(p_result.to_reverse_count)
                
            return p_result.success(ReturnNode(
                pos_start, self.current_token.pos_end.copy(),
                expr
            ))

        elif self.current_token.is_keyword_of(Keyword.CONTINUE):
            self.advance_register_advancement(p_result, False)
            return p_result.success(ContinueNode(
                pos_start, self.current_token.pos_end.copy()
            ))
            
        elif self.current_token.is_keyword_of(Keyword.BREAK):
            self.advance_register_advancement(p_result, False)
            return p_result.success(BreakNode(
                pos_start, self.current_token.pos_end.copy()
            ))
            
        expr = p_result.register(self.expr())
        if p_result.error:
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.RETURN, Keyword.CONTINUE, Keyword.BREAK, Keyword.SETVAR, Keyword.DELETEVAR,
                         Keyword.NOT, Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION,
                         TokenType.NUMBER, TokenType.PLUS, TokenType.MINUS, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.LSQUARE
                         ),
                self.current_token.pos_start, self.current_token.pos_end
            ))
            
        return p_result.success(expr)

    def statements(self):
        p_result = ParseResult()
        statements: list[Node] = []
        pos_start = self.current_token.pos_start.copy()
        
        self.advance_if_token_is_semicolon_or_newline(p_result)
            
        statement: Node = p_result.register(self.statement())
        if p_result.error: return p_result
        statements.append(statement)
        
        more_statements = True
        
        while True:
            newline_count = self.advance_if_token_is_semicolon_or_newline(p_result)
                
            if not newline_count:
                more_statements = False
                
            if not more_statements: break
            
            statement: Node = p_result.try_register(self.statement())

            if not statement:
                self.reverse(p_result.to_reverse_count)
                more_statements = False
                continue
            
            statements.append(statement)
            
        return p_result.success(ListNode(
            pos_start, self.current_token.pos_end.copy(),
            statements
        ))
                
    def func_def(self) -> ParseResult:
        p_result = ParseResult()
        
        if not self.current_token.is_keyword_of(Keyword.SETFUNCTION):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.SETFUNCTION),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)
        
        if self.current_token.is_type_of(TokenType.IDENTIFIER):
            var_name_token = self.current_token
            
            self.advance_register_advancement(p_result, False)
            
            if not self.current_token.is_type_of(TokenType.LPAREN):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.LPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        else:
            var_name_token = None
            if not self.current_token.is_type_of(TokenType.LPAREN):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER, TokenType.LPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        self.advance_register_advancement(p_result, False)
        
        arg_name_tokens: list[Token] = []
        
        if self.current_token.is_type_of(TokenType.IDENTIFIER):
            arg_name_tokens.append(self.current_token)
            
            self.advance_register_advancement(p_result, False)
            
            while self.current_token.is_type_of(TokenType.COMMA):
                self.advance_register_advancement(p_result, False)
                
                if not self.current_token.is_type_of(TokenType.IDENTIFIER):
                    return p_result.failure(ErrorInvalidSyntax(
                        expected(TokenType.IDENTIFIER),
                        self.current_token.pos_start, self.current_token.pos_end
                    ))
                    
                arg_name_tokens.append(self.current_token)
                
                self.advance_register_advancement(p_result, False)
                
            if not self.current_token.is_type_of(TokenType.RPAREN):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.COMMA, TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        else:
            if not self.current_token.is_type_of(TokenType.RPAREN):
                return p_result.failure(ErrorInvalidSyntax(
                    expected(TokenType.IDENTIFIER, TokenType.RPAREN),
                    self.current_token.pos_start, self.current_token.pos_end
                ))
        
        self.advance_register_advancement(p_result, False)
        
        if self.current_token.is_type_of(TokenType.RIGHTARROW):
            self.advance_register_advancement(p_result, False)
            
            body_node: Node = p_result.register(self.expr())
            
            if p_result.error: return p_result
            
            return p_result.success(FuncDefNode(var_name_token, tuple(arg_name_tokens), body_node, True))
    
        if not self.current_token_is_semicolon_or_newline():
            return p_result.failure(ErrorInvalidSyntax(
                expected(TokenType.RIGHTARROW, TokenType.SEMICOLON, TokenType.NEWLINE),
                self.current_token.pos_start, self.current_token.pos_end,
            ))

        self.advance_register_advancement(p_result, False)

        body_node = p_result.register(self.statements())
        if p_result.error:
            return p_result

        if not self.current_token.is_keyword_of(Keyword.END):
            return p_result.failure(ErrorInvalidSyntax(
                expected(Keyword.END),
                self.current_token.pos_start, self.current_token.pos_end
            ))

        self.advance_register_advancement(p_result, False)

        return p_result.success(FuncDefNode(var_name_token, tuple(arg_name_tokens), body_node, False))
    
    #!================================================================
    
    def bin_op(self, operations: tuple, function_a: Callable, function_b: Callable = None) -> ParseResult:
        function_b = function_b or function_a

        p_result = ParseResult()
        left = p_result.register(function_a())
        
        if p_result.error: return p_result

        while self.current_token.type in operations or (self.current_token.is_type_of(TokenType.KEYWORD) and self.current_token.value in operations):
            operation_token = self.current_token
            self.advance_register_advancement(p_result, False)
            right = p_result.register(function_b())
            if p_result.error: return p_result
            left = BinOpNode(operation_token, left, right)
            
        return p_result.success(left)
    