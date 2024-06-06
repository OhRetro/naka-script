from dataclasses import dataclass
from typing import List, Optional, Tuple
from .token import Token

@dataclass
class NumberNode:
    token: Token

@dataclass
class StringNode:
    token: Token

@dataclass
class ListNode:
    element_nodes: List[NumberNode]

@dataclass
class VarAccessNode:
    name_token: Token

@dataclass
class VarAssignNode:
    name_token: Token
    value_node: NumberNode

@dataclass
class BinOpNode:
    left_node: NumberNode
    operation_token: Token
    right_node: NumberNode

@dataclass
class UnaryOpNode:
    operation_token: Token
    node: NumberNode

@dataclass
class IfNode:
    cases: List[Tuple[Token, NumberNode]]
    else_case: Optional[Tuple[Token, NumberNode]]

@dataclass
class ForNode:
    name_token: Token
    start_value_node: NumberNode
    end_value_node: NumberNode
    step_value_node: NumberNode
    body_node: NumberNode
    should_return_null: bool

@dataclass
class WhileNode:
    condition_node: NumberNode
    body_node: NumberNode
    should_return_null: bool

@dataclass
class FuncDefNode:
    name_token: Optional[Token]
    arg_name_tokens: List[Token]
    body_node: NumberNode
    should_auto_return: bool

@dataclass
class CallNode:
    node_to_call: NumberNode
    arg_nodes: List[NumberNode]

@dataclass
class ReturnNode:
    node_to_return: NumberNode

@dataclass
class ContinueNode:
    pass

@dataclass
class BreakNode:
    pass
