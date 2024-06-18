from typing import Callable, Union
from .node import (Node, 
                   NumberNode, StringNode, ListNode, DictNode,
                   BinOpNode, UnaryOpNode,
                   IfNode, ForNode, WhileNode,
                   FuncDefNode, CallNode, IndexNode, AccessNode, UpdateNode,
                   VarAssignNode, VarDeleteNode,
                   ReturnNode)
from .token import Token, TokenType
from .keyword import Keyword
from .runtime import RuntimeResult
from .context import Context
from .error import ErrorRuntime
from ..datatype import Datatype, Number, String, List, Dict, BaseFunction, Function

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
            value = rt_result.register(self.visit(element_node, context))
            if rt_result.should_return(): return rt_result
            elements.append(value)
            
        return rt_result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_DictNode(self, node: DictNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        values: dict[str, Datatype] = {}
        
        key_tokens = node.key_tokens
        value_nodes = node.value_nodes
        
        for i, key_tokens in enumerate(key_tokens):
            value = rt_result.register(self.visit(value_nodes[i], context))
            if rt_result.should_return(): return rt_result
            
            values[str(key_tokens.value)] = value
            
        return rt_result.success(
            Dict(values).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_IndexNode(self, node: IndexNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        value_to_index: Union[String, List, Dict] = rt_result.register(self.visit(node.node_to_index, context))
        if rt_result.should_return(): return rt_result
        value_to_index = value_to_index.copy().set_pos(node.pos_start, node.pos_end)
        
        index_value: Union[Number, String] = rt_result.register(self.visit(node.index_node, context))
        if rt_result.should_return(): return rt_result
        index_value = index_value.copy().set_pos(node.pos_start, node.pos_end)

        if not isinstance(value_to_index, (String, List, Dict)):
            return rt_result.failure(ErrorRuntime(
                f"'{value_to_index.__class__.__name__}' datatypes are not indexable.",
                node.pos_start, node.pos_end, context
            ))
            
        indexed_value, error = value_to_index.index_at(index_value)
        
        if error: 
            return rt_result.failure(error)
        
        indexed_value = indexed_value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(indexed_value)

    def visit_AccessNode(self, node: AccessNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        identifier_name = node.token.value
        
        if node.node_to_access:
            value_to_access = rt_result.register(self.visit(node.node_to_access, context))
            if rt_result.should_return(): return rt_result
            value_to_access = value_to_access.copy().set_pos(node.pos_start, node.pos_end)
            
            accessed_value, error = value_to_access.access_at(identifier_name)

            if error: 
                return rt_result.failure(error)
        else:
            accessed_value = context.get_symbol(identifier_name)
            
            if not accessed_value:
                return rt_result.failure(ErrorRuntime(
                    f"Variable '{identifier_name}' is not defined.",
                    node.pos_start, node.pos_end, context
                ))
        
        accessed_value = accessed_value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(accessed_value)
    
    def visit_UpdateNode(self, node: UpdateNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        node_or_identifier_to_update: Union[Union[IndexNode, AccessNode], Token] = node.node_or_identifier_to_update
        
        new_value = rt_result.register(self.visit(node.new_value_node, context))
        if rt_result.should_return(): return rt_result
        
        if isinstance(node_or_identifier_to_update, IndexNode):
            main_node = node_or_identifier_to_update.node_to_index

            if isinstance(main_node, StringNode):
                return rt_result.failure(ErrorRuntime(
                    f"'String' datatypes are immutable.",
                    node.pos_start, node.pos_end, context
                ))
                
            main_value = rt_result.register(self.visit(main_node, context))
            if rt_result.should_return(): return rt_result
            main_value = main_value.copy().set_pos(node.pos_start, node.pos_end)
            
            index_value: Union[Number, String] = rt_result.register(self.visit(node_or_identifier_to_update.index_node, context))
            if rt_result.should_return(): return rt_result
            index_value = index_value.copy().set_pos(node.pos_start, node.pos_end)
            
            if isinstance(main_value, String):
                return rt_result.failure(ErrorRuntime(
                    f"'String' datatypes are immutable.",
                    node.pos_start, node.pos_end, context
                ))
        
            _, error = main_value.update_index_at(index_value, new_value)

            if error:
                return rt_result.failure(error)
        
            return rt_result.success(Number.null)
            
        elif isinstance(node_or_identifier_to_update, Token):
            var_name = node_or_identifier_to_update.value
            
            symbol_table = context.symbol_table
            symbols_dict_type, _ = symbol_table.exists_where(var_name)
            
            if not symbol_table.exists(var_name):
                return rt_result.failure(ErrorRuntime(
                    f"Variable '{var_name}' was not defined.",
                    node.pos_start, node.pos_end, context
                ))
            else:
                if symbols_dict_type == "immutable_symbols":
                    return rt_result.failure(ErrorRuntime(
                        f"'{var_name}' is a constant variable.",
                        node.pos_start, node.pos_end, context
                    ))
                if symbols_dict_type == "persistent_symbols":
                    return rt_result.failure(ErrorRuntime(
                        f"'{var_name}' is a persistent and builtin variable.",
                        node.pos_start, node.pos_end, context
                    ))
                
            symbol_table.set(var_name, new_value, symbols_dict_type)
            return rt_result.success(new_value)
        else:
            raise Exception("Somewere went wrong")

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        value = rt_result.register(self.visit(node.value_node, context))
        
        if rt_result.should_return(): return rt_result
        
        symbol_table = context.symbol_table
        
        if symbol_table.exists(var_name):
            return rt_result.failure(ErrorRuntime(
                f"Variable '{var_name}' is already defined.",
                node.pos_start, node.pos_end, context
            ))
            
        symbol_table.set(var_name, value, node.assign_type)
        return rt_result.success(value)
        
    def visit_VarDeleteNode(self, node: VarDeleteNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        var_name: str = node.token.value
        
        symbol_table = context.symbol_table
        symbols_dict_type, _ = symbol_table.exists_where(var_name)
        
        if not symbol_table.exists(var_name):
            return rt_result.failure(ErrorRuntime(
                f"Variable '{var_name}' is already not defined.",
                node.pos_start, node.pos_end, context
            ))
        else:
            if symbols_dict_type == "persistent_symbols":
                return rt_result.failure(ErrorRuntime(
                    f"'{var_name}' is a persistent and builtin variable and cannot be deleted.",
                    node.pos_start, node.pos_end, context
                ))
    
        symbol_table.remove(var_name)
        return rt_result.success(Number.null)
    
    def visit_BinOpNode(self, node: BinOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        left: Datatype = rt_result.register(self.visit(node.left_node, context))
        if rt_result.should_return(): return rt_result
        
        right: Datatype = rt_result.register(self.visit(node.right_node, context))
        if rt_result.should_return(): return rt_result
        
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
                    
            case TokenType.KEYWORD:
                if node.token.is_keyword_of(Keyword.AND):
                    result, error = left.and_with(right)
                elif node.token.is_keyword_of(Keyword.OR):
                    result, error = left.or_with(right)

        if error:
            return rt_result.failure(error)
        
        result = result or Number.null
        
        return rt_result.success(result.set_context(context).set_pos(node.pos_start, node.pos_end))
            
    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        number: Number = rt_result.register(self.visit(node.node, context))
        if rt_result.should_return(): return rt_result
        
        error = None
        
        if node.token.is_type_of(TokenType.MINUS):
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
            if rt_result.should_return(): return rt_result
            
            if condition_value.is_true():
                expr_value = rt_result.register(self.visit(expr, context))
                if rt_result.should_return(): return rt_result
                return rt_result.success(Number.null if should_return_null else expr_value)
            
        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = rt_result.register(self.visit(expr, context))
            if rt_result.should_return(): return rt_result
            return rt_result.success(Number.null if should_return_null else else_value)
        
        return rt_result.success(Number.null)
    
    def visit_ForNode(self, node: ForNode, context: Context):
        rt_result = RuntimeResult()
        elements: list[Datatype] = []

        start_value_number: Number = rt_result.register(self.visit(node.start_value_node, context))
        if rt_result.should_return(): return rt_result

        end_value_number: Number = rt_result.register(self.visit(node.end_value_node, context))
        if rt_result.should_return(): return rt_result

        if node.step_value_node:
            step_value_number: Number = rt_result.register(self.visit(node.step_value_node, context))
            if rt_result.should_return(): return rt_result
        else:
            step_value_number = Number(1)

        i: int = start_value_number.value

        if step_value_number.value >= 0:
            condition = lambda: i < end_value_number.value
        else:
            condition = lambda: i > end_value_number.value
        
        while condition():
            context.symbol_table.set(node.token.value, Number(i), "symbols")
            i += step_value_number.value
            
            value = rt_result.register(self.visit(node.body_node, context))
            if rt_result.an_error_occurred(): return rt_result
            
            if rt_result.loop_should_continue:
                continue
            elif rt_result.loop_should_break:
                break
            
            elements.append(value)

        return rt_result.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        rt_result = RuntimeResult()
        elements: list[Datatype] = []

        while True:
            condition: Datatype = rt_result.register(self.visit(node.condition_node, context))
            if rt_result.should_return(): return rt_result

            if not condition.is_true(): break

            value = rt_result.register(self.visit(node.body_node, context))
            if rt_result.an_error_occurred(): return rt_result
            
            if rt_result.loop_should_continue:
                continue
            elif rt_result.loop_should_break:
                break
            
            elements.append(value)

        return rt_result.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        rt_result = RuntimeResult()
        func_name: str = node.token.value if node.token else "<anon>"
        body_node = node.body_node
        arg_names: list[str] = [arg_name.value for arg_name in node.arg_name_tokens]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.token:
            context.symbol_table.set(func_name, func_value, "symbols")
            
        return rt_result.success(func_value)
        
    def visit_CallNode(self, node: CallNode, context: Context):
        rt_result = RuntimeResult()
        args: list[Datatype] = []
        
        value_to_call = rt_result.register(self.visit(node.node_to_call, context))
        if rt_result.should_return(): return rt_result
        
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        
        for arg_node in node.arg_nodes:
            args.append(rt_result.register(self.visit(arg_node, context)))
            if rt_result.should_return(): return rt_result
            
        if not isinstance(value_to_call, BaseFunction):
            return rt_result.failure(ErrorRuntime(
                f"'{value_to_call.__class__.__name__}' datatypes are not callable.",
                node.pos_start, node.pos_end, context
            ))
            
        return_value: Datatype = rt_result.register(value_to_call.execute(args))
        if rt_result.should_return(): return rt_result
        
        return_value = return_value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(return_value)

    def visit_ReturnNode(self, node: ReturnNode, context: Context):
        rt_result = RuntimeResult()
        
        value = Number.null
        if node.node_to_return:
            value = rt_result.register(self.visit(node.node_to_return, context))
            
            if rt_result.should_return(): return rt_result

        # Fun Fact: While making it I forgot to return the runtime result in a function about returning, ironic
        return rt_result.success_return(value)

    def visit_ContinueNode(self, _, __):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, _, __):
        return RuntimeResult().success_break()
