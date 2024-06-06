from dataclasses import dataclass
from .token import Token

@dataclass(frozen=True, slots=True)
class Node:
    token: Token

@dataclass(frozen=True, slots=True)
class NumberNode(Node):
    def __repr__(self) -> str:
        return f"NumberNode({self.token.value})"

@dataclass(frozen=True, slots=True)
class BinOpNode(Node):
    left_node: Node
    right_node: Node
    
    def __repr__(self) -> str:
        return f"BinOpNode({self.left_node}, {self.token}, {self.right_node})"
        
@dataclass(frozen=True, slots=True)
class UnaryOpNode(Node):
    node: Node
    
    def __repr__(self) -> str:
        return f"UnaryOpNode({self.token}, {self.node})"