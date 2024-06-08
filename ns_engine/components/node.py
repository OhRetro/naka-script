from dataclasses import dataclass, field
from .token import Token
from .position import Position

@dataclass(slots=True,)
class Node:
    token: Token
    pos_start: Position = field(default=None, init=False, repr=False)
    pos_end: Position = field(default=None, init=False, repr=False)
    
@dataclass(slots=True)
class NumberNode(Node):
    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self) -> str:
        return f"NumberNode({self.token.value})"

@dataclass(slots=True)
class VarAccessNode(Node):
    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self) -> str:
        return f"VarAccessNode({self.token})"
    
@dataclass(slots=True)
class VarAssignNode(Node):
    value_node: Node

    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self) -> str:
        return f"VarAssignNode({self.token}, {self.value_node})"
    
@dataclass(slots=True)
class BinOpNode(Node):
    left_node: Node
    right_node: Node

    def __post_init__(self):
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self) -> str:
        return f"BinOpNode({self.left_node}, {self.token}, {self.right_node})"
        
@dataclass(slots=True)
class UnaryOpNode(Node):
    node: Node

    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self) -> str:
        return f"UnaryOpNode({self.token}, {self.node})"
    