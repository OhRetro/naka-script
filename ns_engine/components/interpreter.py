from typing import Callable
from .node import (Node, NumberNode,
                   BinOpNode, UnaryOpNode)
from .token import TokenType
from .runtime import RuntimeResult
from .context import Context
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

        if error:
            return rt_result.failure(error)
            
        return rt_result.success(result.set_pos(node.pos_start, node.pos_end))
            
    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        number: Number = rt_result.register(self.visit(node.node, context))
        if rt_result.error: return rt_result
        
        if node.token.type == TokenType.MINUS:
            number, error = number.multiplied_by(Number(-1))

        if error:
            return rt_result.failure(error)
        
        return rt_result.success(number.set_pos(node.pos_start, node.pos_end))
    