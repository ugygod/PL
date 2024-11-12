import ply.yacc as yacc
import random
import re
from lexer import tokens  # Importa os tokens do lexer
from lexer import lexer  # Importa o lexer

# Regras de precedência
precedence = (
    ('left', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'MAIOR', 'MENOR'),
)

# Dicionário de nomes (para armazenar variáveis)
names = {}

# Dicionário de funções (para armazenar definições de funções)
functions = {}

# Função para manipular a interpolação de strings
def interpolate_string(s):
    def replace_var(match):
        var_name = match.group(1)
        return str(names.get(var_name, f'#{var_name}'))
    return re.sub(r'#\{(\w+)\}', replace_var, s)

# Estrutura do programa
def p_program(p):
    'program : statement_list'
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : assignment SEMICOLON
                 | write_statement SEMICOLON
                 | read_statement SEMICOLON
                 | random_statement SEMICOLON
                 | function_definition
                 | function_call SEMICOLON'''
    p[0] = p[1]

def p_assignment(p):
    'assignment : IDENTIFIER ASSIGN expression'
    names[p[1]] = eval_expression(p[3])
    p[0] = ('assign', p[1], p[3])

def p_write_statement(p):
    'write_statement : WRITE LPAREN expression RPAREN'
    p[0] = ('write', p[3])

def p_read_statement(p):
    'read_statement : IDENTIFIER ASSIGN READ LPAREN RPAREN'
    value = input("Introduza um valor: ")
    names[p[1]] = value
    p[0] = ('read', p[1], value)

def p_random_statement(p):
    'random_statement : IDENTIFIER ASSIGN RANDOM LPAREN NUMBER RPAREN'
    value = random.randint(0, p[5])
    names[p[1]] = value
    p[0] = ('random', p[1], value)

def p_function_definition(p):
    '''function_definition : FUNCTION IDENTIFIER LPAREN parameters RPAREN COMMA COLON expression SEMICOLON
                           | FUNCTION IDENTIFIER LPAREN parameters RPAREN COLON statement_list END'''
    if len(p) == 10:
        functions[p[2]] = (p[4], [p[8]])
        p[0] = ('function_def', p[2], p[4], p[8])
    else:
        functions[p[2]] = (p[4], p[7])
        p[0] = ('function_def', p[2], p[4], p[7])

def p_function_call(p):
    'function_call : IDENTIFIER LPAREN arguments RPAREN'
    p[0] = ('function_call', p[1], p[3])

def eval_statement(stmt, local_context=None):
    if local_context is None:
        local_context = names

    if stmt[0] == 'assign':
        rhs = eval_expression(stmt[2], local_context)
        local_context[stmt[1]] = rhs
    elif stmt[0] == 'write':
        result = eval_expression(stmt[1], local_context)
        print(result)
    elif stmt[0] == 'read':
        local_context[stmt[1]] = stmt[2]
    elif stmt[0] == 'random':
        local_context[stmt[1]] = stmt[2]
    elif stmt[0] == 'function_def':
        functions[stmt[1]] = (stmt[2], stmt[3])
    elif stmt[0] == 'function_call':
        func_name = stmt[1]
        args = [eval_expression(arg, local_context) for arg in stmt[2]]
        param_names, body = functions[func_name]
        saved_context = local_context.copy()
        local_context = {}
        for param, arg in zip(param_names, args):
            local_context[param] = arg
        result = None
        if isinstance(body, list):
            for sub_stmt in body:
                result = eval_statement(sub_stmt, local_context)
        else:
            result = eval_statement(body, local_context)
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
            return eval_expression(expr[1], local_context)
        elif expr[0] == 'read':
            return local_context[expr[1]]
        elif expr[0] == 'random':
            return local_context[expr[1]]
        elif expr[0] == 'function_def':
            functions[expr[1]] = (expr[2], expr[3])
        elif expr[0] == 'greater_than':
            left = eval_expression(expr[1], local_context)
            right = eval_expression(expr[2], local_context)
            return left > right
        elif expr[0] == 'less_than':
            left = eval_expression(expr[1], local_context)
            right = eval_expression(expr[2], local_context)
            return left < right
        elif expr[0] == 'function_call':
            func_name = expr[1]
            args = [eval_expression(arg, local_context) for arg in expr[2]]
            param_names, body = functions[func_name]
            saved_context = local_context.copy()
            local_context = {}
            for param, arg in zip(param_names, args):
                local_context[param] = arg
            result = None
            if isinstance(body, list):
                for sub_stmt in body:
                    result = eval_statement(sub_stmt, local_context)
            else:
                result = eval_statement(body, local_context)
            local_context.clear()
            local_context.update(saved_context)
            return result
    elif isinstance(expr, int):
        return expr
    elif isinstance(expr, str):
        return local_context.get(expr, expr)
    elif isinstance(expr, list):
        return [eval_expression(e, local_context) for e in expr]
    elif isinstance(expr, str):
        return interpolate_string(expr)

def p_parameters(p):
    '''parameters : parameters COMMA IDENTIFIER
                  | IDENTIFIER
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_arguments(p):
    '''arguments : arguments COMMA expression
                 | expression
                 | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression CONCAT expression
                  | expression MAIOR expression
                  | expression MENOR expression'''
    if p[2] == '+':
        p[0] = eval_expression(p[1]) + eval_expression(p[3])
    elif p[2] == '-':
        p[0] = eval_expression(p[1]) - eval_expression(p[3])
    elif p[2] == '*':
        p[0] = eval_expression(p[1]) * eval_expression(p[3])
    elif p[2] == '/':
        p[0] = eval_expression(p[1]) // eval_expression(p[3])
    elif p[2] == '<>':
        p[0] = str(eval_expression(p[1])) + str(eval_expression(p[3]))
    elif p[2] == '/\\':
        p[0] = ('greater_than', p[1], p[3])
    elif p[2] == '\\/':
        p[0] = ('less_than', p[1], p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = names.get(p[1], p[1])

def p_expression_string(p):
    'expression : STRING'
    p[0] = interpolate_string(p[1])

def p_expression_list(p):
    'expression : LBRACKET elements RBRACKET'
    if not p[2]:
        p[0] = []
    else:
        p[0] = p[2]

def p_elements(p):
    '''elements : elements COMMA expression
                | expression
                | empty'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

def p_empty(p):
    'empty :'

def p_error(p):
    if p:
        print(f"Erro de sintaxe em '{p.value}'")
    else:
        print("Erro de sintaxe no EOF")

# Constrói o parser
parser = yacc.yacc()

def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        result = parser.parse(data)
        if result:
            for stmt in result:
                eval_statement(stmt)

