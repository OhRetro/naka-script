from dataclasses import dataclass, field
from .token import Token
from .position import Position

@dataclass(slots=True)
class Node:
    token: Token
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)
    
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
    
@dataclass(slots=True)
class IfNode(Node):
    token: Token = field(default=None, init=False)
    cases: list[tuple[Node, Node]]
    else_case: Node
    
    def __post_init__(self):
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end
        
    def __repr__(self) -> str:
        return f"IfNode({self.cases}, {self.else_case})"
    