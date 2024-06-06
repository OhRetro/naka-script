from typing import Callable
from .error import NSInvalidSyntaxError
from .token import Token, TokenType
from .keyword import Keyword
from .node import (Node, NumberNode, StringNode, BinOpNode, ClassNode,
                   UnaryOpNode, VarAccessNode, VarAssignNode, VarReassignNode,
                   CallNode, ForNode, FuncDefNode, IfNode,
                   WhileNode, ListNode, ReturnNode, ContinueNode, BreakNode)

from ..utils.expected import expected
from ..utils.debug import DebugMessage

debug_message = DebugMessage("", True)

class Parser:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self

    def __repr__(self) -> str:
        return f"<ParseResult:({self.node}, {self.error})>"

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount: int = 1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def register_advance(self, res: Parser):
        res.register_advancement()
        return self.advance()

    def parse(self):
        res = self.statements()
        
        if not res.error and self.current_tok.type != TokenType.EOF:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Token cannot appear after previous tokens"
            ))
        return res
    
    def get_full_identifier(self, res: Parser):
        identifier_name = self.current_tok
        debug_message.set_message(f"IDENTIFIER: {identifier_name}")
        self.register_advance(res)
        
        extra_identifiers = []
        
        # while self.current_tok.type == TokenType.DOT:
        #     self.register_advance(res)

        #     if self.current_tok.type != TokenType.IDENTIFIER:
        #         return None, None, res.failure(NSInvalidSyntaxError(
        #             self.current_tok.pos_start, self.current_tok.pos_end,
        #             expected(TokenType.IDENTIFIER)
        #         ))
            
        #     extra_identifiers.append(self.current_tok)
        #     self.register_advance(res)
        
        debug_message.set_message(f"IDENTIFIER: EXTRAS: {extra_identifiers}")
        return identifier_name, extra_identifiers, None
            
    ###################################

    def statements(self):
        debug_message.set_message("")
        res = Parser()
        statements = []
        pos_start = self.current_tok.pos_start.copy()
        
        while self.current_tok.type in (TokenType.NEWLINE, TokenType.SEMICOLON):
            self.register_advance(res)

        statement = res.register(self.statement())
        
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            
            while self.current_tok.type in (TokenType.NEWLINE, TokenType.SEMICOLON):
                self.register_advance(res)
                newline_count += 1
                
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = res.try_register(self.statement())
            
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        
        return res.success(ListNode(
            statements,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def statement(self):
        debug_message.set_message("")
        res = Parser()
        pos_start = self.current_tok.pos_start.copy()
        
        if self.current_tok.matches(TokenType.KEYWORD, Keyword.RETURN):
            self.register_advance(res)
            
            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(TokenType.KEYWORD, Keyword.CONTINUE):
            self.register_advance(res)
            
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(TokenType.KEYWORD, Keyword.BREAK):
            self.register_advance(res)
            
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
        
        expr = res.register(self.expr())
        
        if res.error:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.RETURN, Keyword.CONTINUE, Keyword.BREAK,
                         Keyword.SETVAR, Keyword.SETIMMUTABLEVAR, Keyword.SETTEMPVAR, Keyword.SETSCOPEDVAR,
                         Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION,
                         TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                         TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE, TokenType.LBRACE, Keyword.NOT)
            ))
            
        return res.success(expr)

    def expr(self):
        debug_message.set_message("")
        res = Parser()

        if (self.current_tok.matches(TokenType.KEYWORD, Keyword.SETVAR) or
            self.current_tok.matches(TokenType.KEYWORD, Keyword.SETIMMUTABLEVAR) or
            self.current_tok.matches(TokenType.KEYWORD, Keyword.SETTEMPVAR) or
            self.current_tok.matches(TokenType.KEYWORD, Keyword.SETSCOPEDVAR)):
            
            var_keyword_tok = self.current_tok
            var_value_type_tok = None
            var_value_type_specified = False

            self.register_advance(res)

            if self.current_tok.type != TokenType.IDENTIFIER:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.IDENTIFIER)
                ))
                
            var_name_tok, var_extra_names_toks, error = self.get_full_identifier(res)
            
            if error:
                return res.failure(error)
        
            if self.current_tok.type == TokenType.COLON:
                self.register_advance(res)

                if self.current_tok.type != TokenType.IDENTIFIER:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(TokenType.IDENTIFIER)
                    ))
                    
                var_value_type_tok = self.current_tok
                
                var_value_type_specified = True
                
                if var_keyword_tok.value == Keyword.SETTEMPVAR:
                    self.register_advance(res)
            else:
                var_value_type_tok = Token(TokenType.IDENTIFIER, "Any")
            
            var_lifetime = None
            if var_keyword_tok.value == Keyword.SETTEMPVAR:
                if self.current_tok.type != TokenType.INT:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(TokenType.INT)
                    ))

                var_lifetime = self.current_tok.value

            if var_value_type_specified or var_keyword_tok.value == Keyword.SETTEMPVAR:
                self.register_advance(res)

            if self.current_tok.type not in (TokenType.EQUALS, TokenType.PLUSE, TokenType.MINUSE, TokenType.MULE, TokenType.DIVE, TokenType.POWERE, TokenType.DIVRESTE):
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.EQUALS, TokenType.PLUSE, TokenType.MINUSE, TokenType.MULE, TokenType.DIVE, TokenType.POWERE, TokenType.DIVRESTE)
                ))
                
            var_assign_type_tok = self.current_tok

            self.register_advance(res)
            
            expr = res.register(self.expr())
            if res.error:
                return res

            if var_keyword_tok.value == Keyword.SETVAR:
                var_method = "set"
            elif var_keyword_tok.value == Keyword.SETIMMUTABLEVAR:
                var_method = "set_as_immutable"
            elif var_keyword_tok.value == Keyword.SETTEMPVAR:
                var_method = "set_as_temporary"
            elif var_keyword_tok.value == Keyword.SETSCOPEDVAR:
                var_method = "set_as_scoped"

            return res.success(VarAssignNode(var_name_tok, var_extra_names_toks, expr, var_value_type_tok, var_assign_type_tok, var_method, var_lifetime))

        elif self.current_tok.type == TokenType.IDENTIFIER:                
            var_name_tok, var_extra_names_toks, error = self.get_full_identifier(res)

            if error:
                return res.failure(error)
            
            if self.current_tok.type in (TokenType.EQUALS, TokenType.PLUSE, TokenType.MINUSE, TokenType.MULE, TokenType.DIVE, TokenType.POWERE, TokenType.DIVRESTE):
                var_assign_type_tok = self.current_tok

                self.register_advance(res)
                
                expr = res.register(self.expr())
                if res.error:
                    return res

                return res.success(VarReassignNode(var_name_tok, var_extra_names_toks, expr, var_assign_type_tok))
            
            elif self.current_tok.type == TokenType.COLON:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    CANNOT_DECLARE_TYPE_AFTER_DECLARED_ERROR
                ))
            
            # PART 1 OF ACCESSING VARIABLES THE OTHER PART IS ON ATOM
            # elif var_extra_names_toks != []:
            #     return res.success(VarAccessNode(var_name_tok, var_extra_names_toks))
                #__1 = 1

            # elif var_extra_names_toks == []:
            #     self.reverse()
            else:
                self.reverse()
        
        node = res.register(self.bin_op(
            self.comp_expr, ((TokenType.KEYWORD, Keyword.AND), (TokenType.KEYWORD, Keyword.OR))))

        if res.error:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.SETVAR, Keyword.SETIMMUTABLEVAR, Keyword.SETTEMPVAR, Keyword.SETSCOPEDVAR,
                         Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION,
                         TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                         TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE, TokenType.LBRACE, Keyword.NOT)
            ))

        return res.success(node)

    def comp_expr(self):
        debug_message.set_message("")
        res = Parser()

        if self.current_tok.matches(TokenType.KEYWORD, Keyword.NOT):
            op_tok = self.current_tok
            self.register_advance(res)

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(
            self.arith_expr, (TokenType.EE, TokenType.NE, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE)))

        if res.error:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                         TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE, Keyword.NOT)
            ))

        return res.success(node)

    def arith_expr(self):
        debug_message.set_message("")
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    def term(self):
        debug_message.set_message("")
        return self.bin_op(self.factor, (TokenType.MUL, TokenType.DIV, TokenType.DIVREST))

    def factor(self):
        debug_message.set_message("")
        res = Parser()
        tok = self.current_tok

        if tok.type in (TokenType.PLUS, TokenType.MINUS):
            self.register_advance(res)
            
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        debug_message.set_message("")
        #return self.bin_op(self.call, (TokenType.POWER, ), self.factor)
        return self.bin_op(self.dot, (TokenType.POWER, ), self.factor)

    def dot(self):
        debug_message.set_message("")
        return self.bin_op(self.call, (TokenType.DOT, ), self.power)
    
    def call(self):
        debug_message.set_message("")
        
        res = Parser()
        
        atom = res.register(self.atom())
        
        if res.error:
            return res
        
        # while self.current_tok.type == TokenType.DOT:
        #     child: Node = atom
        #     self.register_advance(res)

        #     child_ = res.register(self.call())
        #     if res.error:
        #         return res

        #     child.child = child_
        #     child = child_

        if self.current_tok.type == TokenType.LPAREN:
            self.register_advance(res)
            
            arg_nodes = []

            if self.current_tok.type == TokenType.RPAREN:
                self.register_advance(res)
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(TokenType.RPAREN, Keyword.SETVAR, Keyword.SETIMMUTABLEVAR, Keyword.SETTEMPVAR, Keyword.SETSCOPEDVAR,
                                 Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION,
                                 TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                                 TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE, Keyword.NOT)
                    ))

                while self.current_tok.type == TokenType.COMMA:
                    self.register_advance(res)

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TokenType.RPAREN:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(TokenType.COMMA, TokenType.RPAREN)
                    ))

                self.register_advance(res)

            return res.success(CallNode(atom, arg_nodes))
        
        return res.success(atom)

    def atom(self):
        debug_message.set_message("CHECKING TOKEN")
        res = Parser()
        tok = self.current_tok
        
        if tok.type in (TokenType.INT, TokenType.FLOAT):
            debug_message.set_message("NUMBER")
            self.register_advance(res)
            return res.success(NumberNode(tok))

        elif tok.type == TokenType.STRING:
            debug_message.set_message("STRING")
            self.register_advance(res)
            return res.success(StringNode(tok))

        # PART 2 OF ACCESSING VARIABLES THE PART 1 IS ON EXPR
        elif tok.type == TokenType.IDENTIFIER:
            tok, var_extra_names_toks, error = self.get_full_identifier(res)
            
            if error:
                return res.failure(error)
            
            return res.success(VarAccessNode(tok, var_extra_names_toks))
            # self.register_advance(res)
            # return res.success(VarAccessNode(tok))

        elif tok.type == TokenType.LPAREN:
            debug_message.set_message("PARENTHESES")
            self.register_advance(res)
            
            expr = res.register(self.expr())
            
            if res.error:
                return res
            if self.current_tok.type == TokenType.RPAREN:
                self.register_advance(res)
                
                return res.success(expr)
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RPAREN)
                ))

        elif tok.type == TokenType.LSQUARE:
            debug_message.set_message("SQUARE PARENTHESES")
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        elif tok.matches(TokenType.KEYWORD, Keyword.IF):
            debug_message.set_message("IF")
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TokenType.KEYWORD, Keyword.FOR):
            debug_message.set_message("FOR")
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TokenType.KEYWORD, Keyword.WHILE):
            debug_message.set_message("WHILE")
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TokenType.KEYWORD, Keyword.SETFUNCTION):
            debug_message.set_message("SET FUNCTION")
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        elif tok.matches(TokenType.KEYWORD, Keyword.SETCLASS):
            debug_message.set_message("SET CLASS")
            class_set = res.register(self.class_set())
            if res.error:
                return res
            return res.success(class_set)
        
        debug_message.set_message("INVALID TOKEN")
        
        return res.failure(NSInvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            expected(TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                     TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE,
                     Keyword.IF, Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION)
        ))

    def list_expr(self):
        debug_message.set_message("")
        res = Parser()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TokenType.LSQUARE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.LSQUARE)
            ))

        self.register_advance(res)

        if self.current_tok.type == TokenType.RSQUARE:
            self.register_advance(res)
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RSQUARE, Keyword.SETVAR, Keyword.SETIMMUTABLEVAR, Keyword.SETTEMPVAR, Keyword.SETSCOPEDVAR,
                             Keyword.FOR, Keyword.WHILE, Keyword.SETFUNCTION,
                             TokenType.INT, TokenType.FLOAT, TokenType.IDENTIFIER,
                             TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.LSQUARE, Keyword.NOT)
                ))

            while self.current_tok.type == TokenType.COMMA:
                self.register_advance(res)

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TokenType.RSQUARE:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.COMMA, TokenType.RSQUARE)
                ))

            self.register_advance(res)

        return res.success(ListNode(
            element_nodes,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def if_expr(self):
        debug_message.set_message("")
        
        res = Parser()
        all_cases = res.register(self.if_expr_cases(Keyword.IF))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def elseif_expr(self):
        debug_message.set_message("")
        return self.if_expr_cases(Keyword.ELSEIF)

    def else_expr(self):
        debug_message.set_message("")
        
        res = Parser()
        else_case = None

        self.register_advance(res)
            
        if self.current_tok.type == TokenType.LBRACE:
            self.register_advance(res)
            
            if self.current_tok.type == TokenType.NEWLINE:
                self.register_advance(res)
                
            statements = res.register(self.statements())
            if res.error:
                return res
            else_case = (statements, True)

            if self.current_tok.matches(TokenType.RBRACE):
                self.register_advance(res)
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RBRACE)
                ))
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            else_case = (expr, False)

        return res.success(else_case)

    def if_expr_elseif_or_else(self):
        debug_message.set_message("")
        
        res = Parser()
        cases, else_case = [], None

        if self.current_tok.matches(TokenType.KEYWORD, Keyword.ELSEIF):
            all_cases = res.register(self.elseif_expr())
            
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.else_expr())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        debug_message.set_message("")
        
        res = Parser()
        cases = []
        else_case = None

        if not self.current_tok.matches(TokenType.KEYWORD, case_keyword):
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))
        
        keyword_tok = self.current_tok
        
        self.register_advance(res)
        
        condition = res.register(self.expr())
        
        if res.error:
            return res

        if self.current_tok.matches(TokenType.LBRACE):
            self.register_advance(res)

            if self.current_tok.type == TokenType.NEWLINE:
                self.register_advance(res)

            statements = res.register(self.statements())
            if res.error:
                return res
            
            cases.append((condition, statements, True))
            
            if self.current_tok.matches(TokenType.RBRACE):
                if keyword_tok.matches(TokenType.KEYWORD, Keyword.IF) or keyword_tok.matches(TokenType.KEYWORD, Keyword.ELSEIF):
                    self.register_advance(res)
                    
                    if self.current_tok.matches(TokenType.KEYWORD, Keyword.ELSEIF) or self.current_tok.matches(TokenType.KEYWORD, Keyword.ELSE):
                        all_cases = res.register(self.if_expr_elseif_or_else())
                        if res.error:
                            return res
                        
                        new_cases, else_case = all_cases
                        cases.extend(new_cases)
                    
                elif keyword_tok.matches(TokenType.KEYWORD, Keyword.ELSE):                
                    self.register_advance(res)
                
                else:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(Keyword.IF, Keyword.ELSEIF, Keyword.ELSE)
                    ))
                    
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RBRACE)
                ))
        
        # Inline statements
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_elseif_or_else())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
            
        return res.success((cases, else_case))

    def for_expr(self):
        debug_message.set_message("")
        
        res = Parser()

        if not self.current_tok.matches(TokenType.KEYWORD, Keyword.FOR):
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.FOR)
            ))

        self.register_advance(res)

        if self.current_tok.type != TokenType.IDENTIFIER:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.IDENTIFIER)
            ))

        var_name = self.current_tok
        
        self.register_advance(res)

        if self.current_tok.type != TokenType.EQUALS:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.EQUALS)
            ))

        self.register_advance(res)

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.type == TokenType.SEMICOLON:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.SEMICOLON)
            ))

        self.register_advance(res)

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type == TokenType.SEMICOLON:
            self.register_advance(res)

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if self.current_tok.type != TokenType.LBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.LBRACE)
            ))

        self.register_advance(res)

        if self.current_tok.type in (TokenType.NEWLINE, TokenType.SEMICOLON):
            self.register_advance(res)

            body = res.register(self.statements())
            if res.error:
                return res

            if self.current_tok.type != TokenType.RBRACE:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RBRACE)
                ))

            self.register_advance(res)

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error:
            return res
    
        if self.current_tok.type != TokenType.RBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.RBRACE)
            ))

        self.register_advance(res)

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        debug_message.set_message("")
        
        res = Parser()

        if not self.current_tok.matches(TokenType.KEYWORD, Keyword.WHILE):
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.WHILE)
            ))

        self.register_advance(res)

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TokenType.LBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.LBRACE)
            ))

        self.register_advance(res)

        if self.current_tok.type in (TokenType.NEWLINE, TokenType.SEMICOLON):
            self.register_advance(res)

            body = res.register(self.statements())
            if res.error:
                return res

            if self.current_tok.type != TokenType.RBRACE:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.RBRACE)
                ))

            self.register_advance(res)

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        if self.current_tok.type != TokenType.RBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.RBRACE)
            ))

        self.register_advance(res)
            
        return res.success(WhileNode(condition, body, False))

    def class_set(self):
        debug_message.set_message("")
        
        res = Parser()
        
        pos_start = self.current_tok.pos_start
        
        if not self.current_tok.matches(TokenType.KEYWORD, Keyword.SETCLASS):
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.SETCLASS)
            ))

        self.register_advance(res)

        if self.current_tok.type != TokenType.IDENTIFIER:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.IDENTIFIER)
            ))

        class_name_tok = self.current_tok
        self.register_advance(res)

        if self.current_tok.type != TokenType.LBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.LBRACE)
            ))

        self.register_advance(res)

        body = res.register(self.statements())

        if res.error:
            return res

        if self.current_tok.type != TokenType.RBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.RBRACE)
            ))

        self.register_advance(res)
        
        return res.success(ClassNode(class_name_tok, body, pos_start, self.current_tok.pos_end))

    def func_def(self):
        debug_message.set_message("")
        
        res = Parser()

        if not self.current_tok.matches(TokenType.KEYWORD, Keyword.SETFUNCTION):
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(Keyword.SETFUNCTION)
            ))

        self.register_advance(res)

        if self.current_tok.type == TokenType.IDENTIFIER:
            func_name_tok = self.current_tok
            self.register_advance(res)
            
            if self.current_tok.type != TokenType.LPAREN:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.LPAREN)
                ))
        else:
            func_name_tok = None
            if self.current_tok.type != TokenType.LPAREN:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.IDENTIFIER, TokenType.LPAREN)
                ))

        self.register_advance(res)
        
        arg_name_toks = []
        arg_type_toks = []
        arg_default_value_toks = []
        
        failsafe = -1
        
        while True:
            failsafe += 1
            if failsafe > 5 or self.current_tok.type == TokenType.RPAREN: break
            
            arg_name_set = False

            if self.current_tok.type == TokenType.IDENTIFIER:
                arg_name_toks.append(self.current_tok)
                self.register_advance(res)
                
                failsafe = -1
                arg_name_set = True
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.IDENTIFIER)
                ))             
                
            if self.current_tok.type == TokenType.COLON and arg_name_set:
                self.register_advance(res)

                if self.current_tok.type != TokenType.IDENTIFIER:
                    return res.failure(NSInvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        expected(TokenType.IDENTIFIER)
                    ))

                arg_type_toks.append(self.current_tok)
                self.register_advance(res)
                
                failsafe = -1
                
            elif arg_name_set:
                arg_type_toks.append(Token(TokenType.IDENTIFIER, "Value"))
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.IDENTIFIER)
                ))
            
            if self.current_tok.type == TokenType.EQUALS and arg_name_set:
                self.register_advance(res)

                arg_default_value_toks.append(self.current_tok)
                
                self.register_advance(res)
                
                failsafe = -1
            elif arg_name_set:
                arg_default_value_toks.append(Token(TokenType.GENERIC, None))
            else:
                return res.failure(NSInvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    expected(TokenType.IDENTIFIER)
                ))

            if self.current_tok.type == TokenType.COMMA and arg_name_set:
                self.register_advance(res)
                
                failsafe = -1

        if self.current_tok.type != TokenType.RPAREN:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.IDENTIFIER, TokenType.COLON, TokenType.EQUALS, TokenType.COMMA, TokenType.RPAREN)
            ))
                
        self.register_advance(res)

        if self.current_tok.type == TokenType.ARROW:
            self.register_advance(res)

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(FuncDefNode(
                func_name_tok,
                arg_name_toks,
                arg_type_toks,
                arg_default_value_toks,
                body,
                True
            ))

        if self.current_tok.type != TokenType.LBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.ARROW, TokenType.LBRACE)
            ))

        self.register_advance(res)

        body = res.register(self.statements())
        if res.error:
            return res
        
        if self.current_tok.type != TokenType.RBRACE:
            return res.failure(NSInvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                expected(TokenType.RBRACE)
            ))

        self.register_advance(res)

        return res.success(FuncDefNode(
            func_name_tok,
            arg_name_toks,
            arg_type_toks,
            arg_default_value_toks,
            body,
            False
        ))

    ###################################

    def bin_op(self, func_a: Callable, ops: tuple[TokenType | Keyword], func_b: Callable = None):
        if func_b is None:
            func_b = func_a
            
        debug_message.set_message(f"{func_a.__name__}, {ops}, {func_b.__name__}")

        res = Parser()
        left = res.register(func_a())
        if res.error:
            debug_message.set_message("Error")
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            
            self.register_advance(res)
            
            right = res.register(func_b())
            if res.error:
                debug_message.set_message("Error")
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)