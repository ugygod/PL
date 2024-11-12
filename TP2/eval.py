import random
from parser_1 import names, functions

def eval_statement(stmt, local_context=None):
    if local_context is None:
        local_context = names

    if stmt[0] == 'assign':
        local_context[stmt[1]] = eval_expression(stmt[2], local_context)
    elif stmt[0] == 'write':
        print(eval_expression(stmt[1], local_context))
    elif stmt[0] == 'read':
        local_context[stmt[1]] = input("Enter a value: ")
    elif stmt[0] == 'random':
        local_context[stmt[1]] = random.randint(0, stmt[2])
    elif stmt[0] == 'function_def':
        functions[stmt[1]] = (stmt[2], stmt[3])
    elif stmt[0] == 'function_call':
        func_name = stmt[1]
        args = [eval_expression(arg, local_context) for arg in stmt[2]]
        param_names, body = functions[func_name]

        # Save current variable context
        saved_context = local_context.copy()

        # Assign arguments to parameters
        for param, arg in zip(param_names, args):
            local_context[param] = arg

        print(f"Executing function '{func_name}' with local context: {local_context}")

        # Execute function body
        result = None
        if isinstance(body, list):
            for sub_stmt in body:
                result = eval_statement(sub_stmt, local_context)
        else:
            result = eval_expression(body, local_context)

        print(f"Function '{func_name}' result: {result}")

        # Restore variable context
        local_context.clear()
        local_context.update(saved_context)

        return result

def eval_expression(expr, local_context=None):
    if local_context is None:
        local_context = names

    if isinstance(expr, tuple):
        if expr[0] == 'assign':
            local_context[expr[1]] = eval_expression(expr[2], local_context)
        elif expr[0] == 'write':
            print(eval_expression(expr[1], local_context))
        elif expr[0] == 'read':
            local_context[expr[1]] = input("Enter a value: ")
        elif expr[0] == 'random':
            local_context[expr[1]] = random.randint(0, expr[2])
        elif expr[0] == 'function_call':
            func_name = expr[1]
            args = [eval_expression(arg, local_context) for arg in expr[2]]
            param_names, body = functions[func_name]

            # Save current variable context
            saved_context = local_context.copy()

            # Assign arguments to parameters
            for param, arg in zip(param_names, args):
                local_context[param] = arg

            print(f"Calling function '{func_name}' with local context: {local_context}")

            # Execute function body
            result = None
            if isinstance(body, list):
                for sub_stmt in body:
                    result = eval_statement(sub_stmt, local_context)
            else:
                result = eval_statement(body, local_context)

            print(f"Function '{func_name}' result: {result}")

            # Restore variable context
            local_context.clear()
            local_context.update(saved_context)

            return result
    elif isinstance(expr, int):
        return expr
    elif isinstance(expr, str):
        return local_context.get(expr, names.get(expr, expr))
    elif isinstance(expr, list):
        return [eval_expression(e, local_context) for e in expr]
    else:
        return expr


