from dataclasses import dataclass, field
from typing import Union
from .token import Token
from .position import Position

@dataclass(slots=True)
class Node:
    token: Token
    pos_start: Position = field(default=None, init=False)
    pos_end: Position = field(default=None, init=False)

    def __post_init__(self):
        self.pos_start = self.pos_start or self.token.pos_start
        self.pos_end = self.pos_end or self.token.pos_end
        
@dataclass(slots=True)
class NumberNode(Node):
    def __repr__(self) -> str:
        return f"NumberNode({self.token.value})"
    
@dataclass(slots=True)
class StringNode(Node):
    def __repr__(self) -> str:
        return f"StringNode(\"{self.token.value}\")"

@dataclass(slots=True)
class ListNode(Node):
    token: Token = field(default=None, init=False)
    element_nodes: list[Node]
    pos_start: Position
    pos_end: Position
        
    def __repr__(self) -> str:
        return f"ListNode({self.element_nodes})"

@dataclass(slots=True)
class DictNode(Node):
    token: Token = field(default=None, init=False)
    key_tokens: list[Token]
    value_nodes: list[Node]
    pos_start: Position
    pos_end: Position
        
    def __repr__(self) -> str:
        display = ""
        for i, key_token in enumerate(self.key_tokens):
            display += f"{key_token}={self.value_nodes[i]}"
        
        return f"DictNode({display})"
    
@dataclass(slots=True)
class VarAccessNode(Node):
    def __repr__(self) -> str:
        return f"VarAccessNode({self.token})"
    
@dataclass(slots=True)
class VarAssignNode(Node):
    value_node: Node
    assign_type: str

    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self) -> str:
        return f"VarAssignNode({self.token}, {self.value_node})"

@dataclass(slots=True)
class VarDeleteNode(Node):
    def __repr__(self) -> str:
        return f"VarDeleteNode({self.token})"

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
    else_case: tuple[Node, bool]
    should_return_null: bool
    
    def __post_init__(self):
        if self.else_case:
            case_for_pos_end = self.else_case[0]
        else:
            case_for_pos_end = self.cases[-1][0]
        
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = case_for_pos_end.pos_end
        
    def __repr__(self) -> str:
        return f"IfNode({self.cases}, {self.else_case})"

@dataclass(slots=True)
class ForNode(Node):
    start_value_node: Node
    end_value_node: Node
    step_value_node: Node
    body_node: Node
    should_return_null: bool

    def __post_init__(self):
        self.pos_start = self.token.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self) -> str:
        return f"ForNode({self.start_value_node.token.value}, {self.end_value_node.token.value}, {self.step_value_node.token.value}, {self.body_node})"

@dataclass(slots=True)
class WhileNode(Node):
    token: Token = field(default=None, init=False)
    condition_node: Node
    body_node: Node
    should_return_null: bool

    def __post_init__(self):
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self) -> str:
        return f"WhileNode({self.condition_node}, {self.body_node})"

@dataclass(slots=True)
class FuncDefNode(Node):
    arg_name_tokens: list[Token]
    body_node: Node
    should_auto_return: bool

    def __post_init__(self):
        if self.token:
            pos_start = self.token.pos_start
        elif len(self.arg_name_tokens) > 0:
            pos_start = self.arg_name_tokens[0].pos_start
        else:
            pos_start = self.body_node.pos_start
        
        self.pos_start = pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self) -> str:
        if self.token:
            return f"FuncDefNode({self.token.value}, {self.arg_name_tokens}, {self.body_node})"
        else:
            return f"FuncDefNode({self.arg_name_tokens}, {self.body_node})"

@dataclass(slots=True)
class CallNode(Node):
    token: Token = field(default=None, init=False)
    node_to_call: Node
    arg_nodes: list[Node]

    def __post_init__(self):
        if len(self.arg_nodes) > 0:
            pos_end = self.arg_nodes[-1].pos_end
        else:
            pos_end = self.node_to_call.pos_end
        
        self.pos_start = self.node_to_call.pos_start
        self.pos_end = pos_end

    def __repr__(self) -> str:
        return f"CallNode({self.node_to_call}, {self.arg_nodes})"

@dataclass(slots=True)
class IndexNode(Node):
    token: Token = field(default=None, init=False)
    node_to_index: Node
    index_node: Node

    def __post_init__(self):
        self.pos_start = self.node_to_index.pos_start
        self.pos_end = self.index_node.pos_end

    def __repr__(self) -> str:
        return f"IndexNode({self.node_to_index}, {self.index_node})"

@dataclass(slots=True)
class AccessNode(Node):
    node_to_access: Node

    def __post_init__(self):
        self.pos_start = self.node_to_access.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self) -> str:
        return f"AccessNode({self.node_to_access}, {self.token})"

@dataclass(slots=True)
class UpdateNode(Node):
    token: Token = field(default=None, init=False)
    node_or_identifier_to_update: Union[Node, Token]
    new_value_node: Node

    def __post_init__(self):
        self.pos_start = self.node_or_identifier_to_update.pos_start
        self.pos_end = self.new_value_node.pos_end

    def __repr__(self) -> str:
        return f"UpdateNode({self.node_or_identifier_to_update}, {self.new_value_node})"
    
@dataclass(slots=True)
class ReturnNode(Node):
    token: Token = field(default=None, init=False)
    node_to_return: Node
    pos_start: Position
    pos_end: Position

    def __repr__(self) -> str:
        return f"ReturnNode({self.node_to_return})"

@dataclass(slots=True)
class ContinueNode(Node):
    token: Token = field(default=None, init=False)
    pos_start: Position
    pos_end: Position

    def __repr__(self) -> str:
        return f"ContinueNode()"

@dataclass(slots=True)
class BreakNode(Node):
    token: Token = field(default=None, init=False)
    pos_start: Position
    pos_end: Position

    def __repr__(self) -> str:
        return f"BreakNode()"
