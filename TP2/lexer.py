import ply.lex as lex
import re

# Lista de nomes dos tokens
tokens = (
    'NUMBER',        # Número
    'PLUS',          # +
    'MINUS',         # -
    'TIMES',         # *
    'DIVIDE',        # /
    'LPAREN',        # (
    'RPAREN',        # )
    'SEMICOLON',     # ;
    'ASSIGN',        # =
    'IDENTIFIER',    # Identificador
    'STRING',        # Cadeia de caracteres
    'CONCAT',        # <>
    'WRITE',         # Palavra reservada ESCREVER
    'READ',          # Palavra reservada ENTRADA
    'RANDOM',        # Palavra reservada ALEATORIO
    'FUNCTION',      # Palavra reservada FUNCAO
    'END',           # Palavra reservada FIM
    'COMMA',         # ,
    'LBRACKET',      # [
    'RBRACKET',      # ]
    'COMMENT',       # Comentário
    'COLON',         # :
    'MAIOR',         # /\
    'MENOR',         # \/
)

# Regras de expressão regular para tokens simples
t_PLUS = r'\+'              # +
t_MINUS = r'-'              # -
t_TIMES = r'\*'             # *
t_DIVIDE = r'/'             # /
t_LPAREN = r'\('            # (
t_RPAREN = r'\)'            # )
t_SEMICOLON = r';'          # ;
t_ASSIGN = r'='             # =
t_CONCAT = r'<>'            # <>
t_COMMA = r','              # ,
t_LBRACKET = r'\['          # [
t_RBRACKET = r'\]'          # ]
t_COLON = r':'              # :

def t_MAIOR(t):
    r'/\\'                  # /\
    return t

def t_MENOR(t):
    r'\\/'                  # \/
    return t

# Nomes de funções reservadas
reserved = {
    'ESCREVER': 'WRITE',    # Palavra reservada ESCREVER
    'ENTRADA': 'READ',      # Palavra reservada ENTRADA
    'ALEATORIO': 'RANDOM',  # Palavra reservada ALEATORIO
    'FUNCAO': 'FUNCTION',   # Palavra reservada FUNCAO
    'FIM': 'END',           # Palavra reservada FIM
}

# Identificadores e palavras reservadas
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[\?\!]?'   # Identificadores
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Verifica se é palavra reservada
    return t

# Cadeias de caracteres
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'   # Expressão regular para cadeias de caracteres
    t.value = t.value[1:-1]    # Remove as aspas duplas
    return t

# Comentários
def t_COMMENT(t):
    r'\-\-.*|\{-[^-]*-\}'      # Expressão regular para comentários
    pass  # Ignora o comentário

# Números
def t_NUMBER(t):
    r'\d+'                     # Expressão regular para números
    t.value = int(t.value)     # Converte o valor para inteiro
    return t

# Caracteres ignorados (espaços e tabulações)
t_ignore = ' \t'

# Quebras de linha
def t_newline(t):
    r'\n+'                     # Expressão regular para novas linhas
    t.lexer.lineno += t.value.count("\n")  # Incrementa o número de linhas

# Regra de tratamento de erros
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")  # Imprime o carácter ilegal
    t.lexer.skip(1)                           # Ignora o carácter ilegal

# Constrói o lexer
lexer = lex.lex()
