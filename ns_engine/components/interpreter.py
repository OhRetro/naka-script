from typing import Callable
from .node import (Node, NumberNode,
                   BinOpNode, UnaryOpNode,
                   IfNode,
                   VarAccessNode, VarAssignNode)
from .token import TokenType
from .keyword import Keyword
from .runtime import RuntimeResult
from .context import Context
from .error import ErrorRuntime
from ..datatype.datatypes import Datatype, Number

class Interpreter:
    def visit(self, node: Node, context: Context) -> RuntimeResult:
        method_name = f"visit_{type(node).__name__}"
        method: Callable = getattr(self, method_name, self.no_visit_method)
        
        return method(node, context)
    
    def no_visit_method(self, node: Node, context: Context):
        raise Exception(f"No visit method defined for {type(node).__name__}.")
    
    def visit_NumberNode(self, node: NumberNode, context: Context) -> RuntimeResult:
        return RuntimeResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_VarAccessNode(self, node: VarAccessNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name = node.token.value
        var_value = context.symbol_table.get(var_name)
        
        if not var_value:
            return rt_result.failure(ErrorRuntime(
                f"Variable '{var_name}' is not defined.",
                node.pos_start, node.pos_end, context
            ))
        
        var_value = var_value.copy().set_pos(node.pos_start, node.pos_end)
        return rt_result.success(var_value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        value = rt_result.register(self.visit(node.value_node, context))
        
        if rt_result.error: return rt_result
        
        context.symbol_table.set(var_name, value)
        
        return rt_result.success(value)
    
    def visit_BinOpNode(self, node: BinOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        left: Datatype = rt_result.register(self.visit(node.left_node, context))
        if rt_result.error: return rt_result
        
        right: Datatype = rt_result.register(self.visit(node.right_node, context))
        if rt_result.error: return rt_result
        
        match node.token.type:
            case TokenType.PLUS:
                result, error = left.added_to(right)
            case TokenType.MINUS:
                result, error = left.subtracted_by(right)
            case TokenType.MULT:
                result, error = left.multiplied_by(right)
            case TokenType.DIV:
                result, error = left.divided_by(right)
            case TokenType.POWER:
                result, error = left.powered_by(right)
            case TokenType.MOD:
                result, error = left.modulo_by(right)
                
            case TokenType.EE:
                result, error = left.is_equal_to(right)
            case TokenType.NE:
                result, error = left.is_not_equal_to(right)
            case TokenType.LT:
                result, error = left.is_less_than(right)
            case TokenType.GT:
                result, error = left.is_greater_than(right)
            case TokenType.LTE:
                result, error = left.is_less_equal_than(right)
            case TokenType.GTE:
                result, error = left.is_greater_equal_than(right)
                
            case TokenType.KEYWORD:
                if node.token.is_keyword_of(Keyword.AND):
                    result, error = left.and_with(right)
                elif node.token.is_keyword_of(Keyword.OR):
                    result, error = left.or_with(right)

        if error:
            return rt_result.failure(error)
            
        return rt_result.success(result.set_pos(node.pos_start, node.pos_end))
            
    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        number: Number = rt_result.register(self.visit(node.node, context))
        if rt_result.error: return rt_result
        
        error = None
        
        if node.token.type == TokenType.MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.token.is_keyword_of(Keyword.NOT):
            number, error = number.notted()

        if error:
            return rt_result.failure(error)
        
        return rt_result.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_IfNode(self, node: IfNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        for condition, expr in node.cases:
            condition_value = rt_result.register(self.visit(condition, context))
            if rt_result.error: return rt_result
            
            if condition_value.is_true():
                expr_value = rt_result.register(self.visit(expr, context))
                if rt_result.error: return rt_result
                return rt_result.success(expr_value)
            
        if node.else_case:
            else_value = rt_result.register(self.visit(node.else_case, context))
            if rt_result.error: return rt_result
            return rt_result.success(else_value)
        
        return rt_result.success(None)