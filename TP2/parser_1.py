import ply.yacc as yacc
from lexer import tokens
from eval import eval_expression, eval_statement
import re 
import random 

# Parsing rules
precedence = (
    ('left', 'CONCAT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# Dictionary of names (for storing variables)
names = {}

# Dictionary of functions (for storing function definitions)
functions = {}

# Function to handle string interpolation
def interpolate_string(s):
    def replace_var(match):
        var_name = match.group(1)
        return str(names.get(var_name, f'#{var_name}'))
    
    return re.sub(r'#\{(\w+)\}', replace_var, s)

# Program structure
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
    names[p[1]] = p[3]
    p[0] = ('assign', p[1], p[3])

def p_write_statement(p):
    'write_statement : WRITE LPAREN expression RPAREN'
    p[0] = ('write', p[3])
    print(p[3])

def p_read_statement(p):
    'read_statement : IDENTIFIER ASSIGN READ LPAREN RPAREN'
    value = input("Enter a value: ")
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
        functions[p[2]] = (p[4], p[8])
        p[0] = ('function_def', p[2], p[4], p[8])
    else:
        functions[p[2]] = (p[4], p[7])
        p[0] = ('function_def', p[2], p[4], p[7])

def p_function_call(p):
    'function_call : IDENTIFIER LPAREN arguments RPAREN'
    func_name = p[1]
    args = p[3]

    if func_name not in functions:
        print(f"Function '{func_name}' not defined")
        p[0] = None
        return

    param_names, body = functions[func_name]

    if len(param_names) != len(args):
        print(f"Function '{func_name}' called with incorrect number of arguments")
        p[0] = None
        return

    # Save current variable context
    saved_context = names.copy()

    # Assign arguments to parameters
    local_context = {}
    for param, arg in zip(param_names, args):
        local_context[param] = eval_expression(arg, local_context)

    print(f"Function call '{func_name}' with local context: {local_context}")

    # Execute function body
    result = None
    if isinstance(body, list):
        for stmt in body:
            result = eval_statement(stmt, local_context)
    else:
        result = eval_expression(body, local_context)

    print(f"Function '{func_name}' result: {result}")

    # Restore variable context
    names.clear()
    names.update(saved_context)

    p[0] = result

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
                  | expression CONCAT expression'''
    print(f"Evaluating binary operation: {p[1]} {p[2]} {p[3]}")
    if isinstance(p[1], int) and isinstance(p[3], int):
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] // p[3]
    elif p[2] == '<>':
        p[0] = str(p[1]) + str(p[3])
    else:
        raise TypeError(f"Invalid operation: {p[2]} between {p[1]} and {p[3]}")

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    try:
        p[0] = names[p[1]]
    except LookupError:
        print(f"Undefined name '{p[1]}'")
        p[0] = ''

def p_expression_string(p):
    'expression : STRING'
    p[0] = interpolate_string(p[1])  # Apply string interpolation

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

def parse(data):
    return parser.parse(data)



