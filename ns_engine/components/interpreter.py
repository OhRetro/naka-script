from typing import Callable
from .node import (Node, 
                   NumberNode, StringNode, ListNode,
                   BinOpNode, UnaryOpNode,
                   IfNode, ForNode, WhileNode,
                   FuncDefNode, CallNode,
                   VarAccessNode, VarAssignNode, VarDeleteNode)
from .token import TokenType
from .keyword import Keyword
from .runtime import RuntimeResult
from .context import Context
from .error import ErrorRuntime
from ..datatype import Datatype, Number, String, List, Function

class Interpreter:
    def visit(self, node: Node, context: Context) -> RuntimeResult:
        method_name = f"visit_{type(node).__name__}"
        method: Callable = getattr(self, method_name, self.no_visit_method)
        
        return method(node, context)
    
    def no_visit_method(self, node: Node, _):
        raise Exception(f"No visit method defined for {type(node).__name__}.")
    
    def visit_NumberNode(self, node: NumberNode, context: Context) -> RuntimeResult:
        return RuntimeResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node: StringNode, context: Context) -> RuntimeResult:
        return RuntimeResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_ListNode(self, node: ListNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        elements: list[Datatype] = []
        
        for element_node in node.element_nodes:
            elements.append(rt_result.register(self.visit(element_node, context)))
            if rt_result.error: return rt_result
            
        return rt_result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
           
    def visit_VarAccessNode(self, node: VarAccessNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        var_value: Datatype = context.symbol_table.get(var_name)
        
        if not var_value:
            return rt_result.failure(ErrorRuntime(
                f"Variable '{var_name}' is not defined.",
                node.pos_start, node.pos_end, context
            ))
        
        var_value = var_value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(var_value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        value = rt_result.register(self.visit(node.value_node, context))
        
        if rt_result.error: return rt_result
        
        context.symbol_table.set(var_name, value)
        
        return rt_result.success(value)
    
    def visit_VarDeleteNode(self, node: VarDeleteNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        
        symbol_table = context.symbol_table
        
        if symbol_table.exists(var_name):
            symbol_table.remove(var_name)
            return rt_result.success(Number.null)
        else:
            return rt_result.failure(ErrorRuntime(
                f"Variable '{var_name}' is not defined.",
                node.pos_start, node.pos_end, context
            ))
    
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
                
            case TokenType.ISEQUALS:
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

            case TokenType.COLON:
                result, error = left.indexing_on(right)
                    
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
        
        for condition, expr, should_return_null in node.cases:
            condition_value = rt_result.register(self.visit(condition, context))
            if rt_result.error: return rt_result
            
            if condition_value.is_true():
                expr_value = rt_result.register(self.visit(expr, context))
                if rt_result.error: return rt_result
                return rt_result.success(Number.null if should_return_null else expr_value)
            
        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = rt_result.register(self.visit(expr, context))
            if rt_result.error: return rt_result
            return rt_result.success(Number.null if should_return_null else else_value)
        
        return rt_result.success(Number.null)
    
    def visit_ForNode(self, node: ForNode, context: Context):
        rt_result = RuntimeResult()
        elements: list[Datatype] = []

        start_value_number: Number = rt_result.register(self.visit(node.start_value_node, context))
        if rt_result.error: return rt_result

        end_value_number: Number = rt_result.register(self.visit(node.end_value_node, context))
        if rt_result.error: return rt_result

        if node.step_value_node:
            step_value_number: Number = rt_result.register(self.visit(node.step_value_node, context))
            if rt_result.error: return rt_result
        else:
            step_value_number = Number(1)

        i: int = start_value_number.value

        if step_value_number.value >= 0:
            condition = lambda: i < end_value_number.value
        else:
            condition = lambda: i > end_value_number.value
        
        while condition():
            context.symbol_table.set(node.token.value, Number(i))
            i += step_value_number.value

            elements.append(rt_result.register(self.visit(node.body_node, context)))
            if rt_result.error: return rt_result

        return rt_result.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        rt_result = RuntimeResult()
        elements: list[Datatype] = []

        while True:
            condition: Datatype = rt_result.register(self.visit(node.condition_node, context))
            if rt_result.error: return rt_result

            if not condition.is_true(): break

            elements.append(rt_result.register(self.visit(node.body_node, context)))
            if rt_result.error: return rt_result

        return rt_result.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        rt_result = RuntimeResult()
        
        func_name: str = node.token.value if node.token else "<anon>"
        body_node = node.body_node
        arg_names: list[str] = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, node.should_return_null).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.token:
            context.symbol_table.set(func_name, func_value)
            
        return rt_result.success(func_value)
        
    def visit_CallNode(self, node: CallNode, context: Context):
        rt_result = RuntimeResult()
        args: list[Datatype] = []
        
        value_to_call = rt_result.register(self.visit(node.node_to_call, context))
        if rt_result.error: return rt_result
        
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        
        for arg_node in node.arg_nodes:
            args.append(rt_result.register(self.visit(arg_node, context)))
            if rt_result.error: return rt_result
            
        return_value: Datatype = rt_result.register(value_to_call.execute(args))
        if rt_result.error: return rt_result
        
        return_value = return_value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(return_value)
    