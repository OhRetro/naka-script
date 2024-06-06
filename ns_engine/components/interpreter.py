from .node import (Node, NumberNode,
                   BinOpNode, UnaryOpNode)
from .token import TokenType
from ..datatype.datatypes import Datatype, Number

class Interpreter:
    def visit(self, node: Node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        
        return method(node)
    
    def no_visit_method(self, node: Node):
        raise Exception(f"No visit method defined for {type(node).__name__}.")
    
    def visit_NumberNode(self, node: NumberNode):
        return Number(node.token.value).set_pos(node.pos_start, node.pos_end)
    
    def visit_BinOpNode(self, node: BinOpNode):
        left: Datatype = self.visit(node.left_node)
        right: Datatype = self.visit(node.right_node)
        result: Datatype = None
        
        if node.token.type == TokenType.PLUS: 
            result = left.added_to(right)
        elif node.token.type == TokenType.MINUS: 
            result = left.subtracted_by(right)
        elif node.token.type == TokenType.MULT: 
            result = left.multiplied_by(right)
        elif node.token.type == TokenType.DIV: 
            result = left.divided_by(right)
            
        return result.set_pos(node.pos_start, node.pos_end)
            
    def visit_UnaryOpNode(self, node: UnaryOpNode):
        number: Number = self.visit(node.node)
        
        if node.token.type == TokenType.MINUS:
            number = number.multiplied_by(Number(-1))
            
        return number.set_pos(node.pos_start, node.pos_end)
    