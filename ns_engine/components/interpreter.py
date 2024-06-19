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
        datatype_elements: list[Datatype] = []
        
        for element_node in node.element_nodes:
            datatype = rt_result.register(self.visit(element_node, context))
            if rt_result.should_return(): return rt_result
            datatype_elements.append(datatype)
            
        return rt_result.success(
            List(datatype_elements).set_context(context).set_pos(node.pos_start, node.pos_end)
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

    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        rt_result = RuntimeResult()
        func_name: str = node.token.value if node.token else "<anon>"
        body_node = node.body_node
        arg_names: list[str] = [arg_name.value for arg_name in node.arg_name_tokens]
        func_datatype = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
        
        if node.token:
            context.symbol_table.set(func_name, func_datatype, "symbols")
            
        return rt_result.success(func_datatype)
        
    def visit_CallNode(self, node: CallNode, context: Context):
        rt_result = RuntimeResult()
        datatype_args: list[Datatype] = []
        
        datatype_to_call = rt_result.register(self.visit(node.node_to_call, context))
        if rt_result.should_return(): return rt_result
        
        datatype_to_call = datatype_to_call.copy().set_pos(node.pos_start, node.pos_end)
        
        for arg_node in node.arg_nodes:
            datatype_args.append(rt_result.register(self.visit(arg_node, context)))
            if rt_result.should_return(): return rt_result
            
        if not isinstance(datatype_to_call, BaseFunction):
            return rt_result.failure(ErrorRuntime(
                f"'{datatype_to_call.__class__.__name__}' datatypes are not callable.",
                node.pos_start, node.pos_end, context
            ))
            
        return_datatype = rt_result.register(datatype_to_call.execute(datatype_args))
        if rt_result.should_return(): return rt_result
        
        return_datatype = return_datatype.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(return_datatype)
    
    def visit_IndexNode(self, node: IndexNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        datatype_to_index: Union[String, List, Dict] = rt_result.register(self.visit(node.node_to_index, context))
        if rt_result.should_return(): return rt_result
        datatype_to_index = datatype_to_index.copy().set_pos(node.pos_start, node.pos_end)
        
        index_datatype: Union[Number, String] = rt_result.register(self.visit(node.index_node, context))
        if rt_result.should_return(): return rt_result
        index_datatype = index_datatype.copy().set_pos(node.pos_start, node.pos_end)

        if not isinstance(datatype_to_index, (String, List, Dict)):
            return rt_result.failure(ErrorRuntime(
                f"'{datatype_to_index.__class__.__name__}' datatypes are not indexable.",
                node.pos_start, node.pos_end, context
            ))
            
        indexed_datatype, error = datatype_to_index.index_at(index_datatype)
        
        if error: 
            return rt_result.failure(error)
        
        indexed_datatype = indexed_datatype.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(indexed_datatype)

    def visit_AccessNode(self, node: AccessNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        identifier_name: str = node.token.value
        
        if node.node_to_access:
            datatype_to_access = rt_result.register(self.visit(node.node_to_access, context))
            if rt_result.should_return(): return rt_result
            datatype_to_access = datatype_to_access.copy().set_pos(node.pos_start, node.pos_end)
            
            accessed_datatype, error = datatype_to_access.access_at(identifier_name)

            if error: 
                return rt_result.failure(error)
        else:
            accessed_datatype = context.get_symbol(identifier_name)
            
            if not accessed_datatype:
                return rt_result.failure(ErrorRuntime(
                    f"Variable '{identifier_name}' is not defined.",
                    node.pos_start, node.pos_end, context
                ))
        
        accessed_datatype = accessed_datatype.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
        return rt_result.success(accessed_datatype)
    
    def visit_UpdateNode(self, node: UpdateNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        node_or_identifier_to_update: Union[Union[IndexNode, AccessNode], Token] = node.node_or_identifier_to_update
        
        new_datatype = rt_result.register(self.visit(node.new_value_node, context))
        if rt_result.should_return(): return rt_result
        
        if isinstance(node_or_identifier_to_update, IndexNode):
            main_node = node_or_identifier_to_update.node_to_index

            if isinstance(main_node, StringNode):
                return rt_result.failure(ErrorRuntime(
                    f"'String' datatypes are immutable.",
                    node.pos_start, node.pos_end, context
                ))
                
            main_datatype = rt_result.register(self.visit(main_node, context))
            if rt_result.should_return(): return rt_result
            main_datatype = main_datatype.copy().set_pos(node.pos_start, node.pos_end)
            
            index_datatype: Union[Number, String] = rt_result.register(self.visit(node_or_identifier_to_update.index_node, context))
            if rt_result.should_return(): return rt_result
            index_datatype = index_datatype.copy().set_pos(node.pos_start, node.pos_end)
            
            if isinstance(main_datatype, String):
                return rt_result.failure(ErrorRuntime(
                    f"'String' datatypes are immutable.",
                    node.pos_start, node.pos_end, context
                ))
        
            _, error = main_datatype.update_index_at(index_datatype, new_datatype)

            if error:
                return rt_result.failure(error)
        
            return rt_result.success(Number.null)
        
        elif isinstance(node_or_identifier_to_update, AccessNode):
            main_node = node_or_identifier_to_update.node_to_access
            
            main_datatype = rt_result.register(self.visit(main_node, context))
            if rt_result.should_return(): return rt_result
            main_datatype = main_datatype.copy().set_pos(node.pos_start, node.pos_end)
            
            identifier_name: str = node_or_identifier_to_update.token.value
            
            _, error = main_datatype.update_access_at(identifier_name, new_datatype)

            if error:
                return rt_result.failure(error)
        
            return rt_result.success(Number.null)
        
        elif isinstance(node_or_identifier_to_update, Token):
            identifier_name: str = node_or_identifier_to_update.value
            
            symbol_table = context.symbol_table
            symbols_dict_type, _ = symbol_table.exists_where(identifier_name)
            
            if not symbol_table.exists(identifier_name):
                return rt_result.failure(ErrorRuntime(
                    f"Variable '{identifier_name}' was not defined.",
                    node.pos_start, node.pos_end, context
                ))
            else:
                if symbols_dict_type == "immutable_symbols":
                    return rt_result.failure(ErrorRuntime(
                        f"'{identifier_name}' is a constant variable.",
                        node.pos_start, node.pos_end, context
                    ))
                if symbols_dict_type == "persistent_symbols":
                    return rt_result.failure(ErrorRuntime(
                        f"'{identifier_name}' is a persistent and builtin variable.",
                        node.pos_start, node.pos_end, context
                    ))
                
            symbol_table.set(identifier_name, new_datatype, symbols_dict_type)
            return rt_result.success(new_datatype)
        else:
            raise Exception("Somewere went wrong")

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        identifier_name: str = node.token.value
        datatype = rt_result.register(self.visit(node.value_node, context))
        
        if rt_result.should_return(): return rt_result
        
        symbol_table = context.symbol_table
        
        if symbol_table.exists(identifier_name):
            return rt_result.failure(ErrorRuntime(
                f"Variable '{identifier_name}' is already defined.",
                node.pos_start, node.pos_end, context
            ))
            
        symbol_table.set(identifier_name, datatype, node.assign_type)
        return rt_result.success(datatype)
        
    def visit_VarDeleteNode(self, node: VarDeleteNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        identifier_name: str = node.token.value
        
        symbol_table = context.symbol_table
        symbols_dict_type, _ = symbol_table.exists_where(identifier_name)
        
        if not symbol_table.exists(identifier_name):
            return rt_result.failure(ErrorRuntime(
                f"Variable '{identifier_name}' is already not defined.",
                node.pos_start, node.pos_end, context
            ))
        else:
            if symbols_dict_type == "persistent_symbols":
                return rt_result.failure(ErrorRuntime(
                    f"'{identifier_name}' is a persistent and builtin variable and cannot be deleted.",
                    node.pos_start, node.pos_end, context
                ))
    
        symbol_table.remove(identifier_name)
        return rt_result.success(Number.null)
    
    def visit_BinOpNode(self, node: BinOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        left_datatype: Datatype = rt_result.register(self.visit(node.left_node, context))
        if rt_result.should_return(): return rt_result
        
        right_datatype: Datatype = rt_result.register(self.visit(node.right_node, context))
        if rt_result.should_return(): return rt_result
        
        match node.token.type:
            case TokenType.PLUS:
                result_datatype, error = left_datatype.added_to(right_datatype)
            case TokenType.MINUS:
                result_datatype, error = left_datatype.subtracted_by(right_datatype)
            case TokenType.MULT:
                result_datatype, error = left_datatype.multiplied_by(right_datatype)
            case TokenType.DIV:
                result_datatype, error = left_datatype.divided_by(right_datatype)
            case TokenType.POWER:
                result_datatype, error = left_datatype.powered_by(right_datatype)
            case TokenType.MOD:
                result_datatype, error = left_datatype.modulo_by(right_datatype)
                
            case TokenType.ISEQUALS:
                result_datatype, error = left_datatype.is_equal_to(right_datatype)
            case TokenType.NE:
                result_datatype, error = left_datatype.is_not_equal_to(right_datatype)
            case TokenType.LT:
                result_datatype, error = left_datatype.is_less_than(right_datatype)
            case TokenType.GT:
                result_datatype, error = left_datatype.is_greater_than(right_datatype)
            case TokenType.LTE:
                result_datatype, error = left_datatype.is_less_equal_than(right_datatype)
            case TokenType.GTE:
                result_datatype, error = left_datatype.is_greater_equal_than(right_datatype)
                    
            case TokenType.KEYWORD:
                if node.token.is_keyword_of(Keyword.AND):
                    result_datatype, error = left_datatype.and_with(right_datatype)
                elif node.token.is_keyword_of(Keyword.OR):
                    result_datatype, error = left_datatype.or_with(right_datatype)

        if error:
            return rt_result.failure(error)
        
        result_datatype = result_datatype or Number.null
        
        return rt_result.success(result_datatype.set_context(context).set_pos(node.pos_start, node.pos_end))
            
    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        number: Number = rt_result.register(self.visit(node.node, context))
        if rt_result.should_return(): return rt_result
        
        error = None
        operator_token = node.token
        
        if operator_token.is_type_of(TokenType.MINUS):
            number, error = number.multiplied_by(Number(-1))
            
        elif operator_token.is_keyword_of(Keyword.NOT):
            number, error = number.notted()

        if error:
            return rt_result.failure(error)
        
        return rt_result.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node: IfNode, context: Context) -> RuntimeResult:
        rt_result = RuntimeResult()
        
        for condition, expr, should_return_null in node.cases:
            condition_datatype = rt_result.register(self.visit(condition, context))
            if rt_result.should_return(): return rt_result
            
            if condition_datatype.is_true():
                expr_datatype = rt_result.register(self.visit(expr, context))
                if rt_result.should_return(): return rt_result
                return rt_result.success(Number.null if should_return_null else expr_datatype)
            
        if node.else_case:
            expr, should_return_null = node.else_case
            else_datatype = rt_result.register(self.visit(expr, context))
            if rt_result.should_return(): return rt_result
            return rt_result.success(Number.null if should_return_null else else_datatype)
        
        return rt_result.success(Number.null)
    
    def visit_ForNode(self, node: ForNode, context: Context):
        rt_result = RuntimeResult()
        datatype_elements: list[Datatype] = []

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
            
            datatype_elements.append(value)

        return rt_result.success(
            Number.null if node.should_return_null else
            List(datatype_elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        rt_result = RuntimeResult()
        datatype_elements: list[Datatype] = []

        while True:
            condition_datatype = rt_result.register(self.visit(node.condition_node, context))
            if rt_result.should_return(): return rt_result

            if not condition_datatype.is_true(): break

            value = rt_result.register(self.visit(node.body_node, context))
            if rt_result.an_error_occurred(): return rt_result
            
            if rt_result.loop_should_continue:
                continue
            elif rt_result.loop_should_break:
                break
            
            datatype_elements.append(value)

        return rt_result.success(
            Number.null if node.should_return_null else
            List(datatype_elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ReturnNode(self, node: ReturnNode, context: Context):
        rt_result = RuntimeResult()
        
        datatype = Number.null
        if node.node_to_return:
            datatype = rt_result.register(self.visit(node.node_to_return, context))
            
            if rt_result.should_return(): return rt_result

        # Fun Fact: While making it I forgot to return the runtime result in a function about returning, ironic
        return rt_result.success_return(datatype)

    def visit_ContinueNode(self, _, __):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, _, __):
        return RuntimeResult().success_break()
