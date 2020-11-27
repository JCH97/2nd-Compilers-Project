import ply.lex as lex
from cmp import Token
from parser import CoolGrammar

literals = ['+', '-', '*', '/', ':', ';', '(', ')', '{', '}', '@', '.', ',']

reserved = {
    'class': 'CLASS',
    'inherits': 'INHERITS',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'fi': 'FI',
    'while': 'WHILE',
    'loop': 'LOOP',
    'pool': 'POOL',
    'let': 'LET',
    'in': 'IN',
    'case': 'CASE',
    'of': 'OF',
    'esac': 'ESAC',
    'new': 'NEW',
    'isvoid': 'ISVOID',
}

ignored = [' ', '\f', '\r', '\t', '\v']

tokens = [    
    'TYPE', 'ID', 'INTEGER', 'STRING', 'BOOL', 'ACTION', 'ASSIGN', 'LESS', 'LESSEQUAL', 'EQUAL', 'INT_COMPLEMENT', 'NOT',
] + list(reserved.values())

tokens_dict = dict()

for t in tokens + literals:
    try:
        tokens_dict[t] = CoolGrammar[t.lower()]
    except KeyError:
        pass


tokens_dict['ACTION'] = CoolGrammar['=>']
tokens_dict['ASSIGN'] = CoolGrammar['<-']
tokens_dict['LESS'] = CoolGrammar['<']
tokens_dict['LESSEQUAL'] = CoolGrammar['<=']
tokens_dict['EQUAL'] = CoolGrammar['=']
tokens_dict['INT_COMPLEMENT'] = CoolGrammar['~']

def t_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"[^\0\n"]*(\\\n[^\0\n"]*)*"'
    t.value = t.value[1:-1]
    return t


def t_BOOL(t):
    r'true|false'
    t.value = True if t.value == 'true' else False
    return t


def t_COMMENT(t):
    r'--[^\n]+\n|\(\*[^(\*\))]+\*\)'
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def find_column(input, token):
    if token:
        line_start = input.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

def t_NOT(t):
    r'[nN][oO][tT]'
    return t

def t_TYPE(t):
    r'[A-Z][A-Za-z0-9_]*'
    return t


def t_ID(t):
    r'[a-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t

t_ASSIGN = r'<-'
t_LESS = r'<'
t_LESSEQUAL = r'<='
t_EQUAL = r'='
t_INT_COMPLEMENT = r'~'

t_ACTION = r'=>'

def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)


t_ignore = ''.join(ignored)

def tokenizer(code):
    ###### CREATE LEXER ######
    # lex.lex(optimize=1) compress code and file
    lexer = lex.lex()

    lexer.input(code)

    tokens = []

    while True:
        token = lexer.token()
        if token is None:
            break
        tokens.append(Token(token.value, tokens_dict[token.type], token.lineno, find_column(code, token)))

    tokens.append(Token('$', CoolGrammar.EOF))

    return tokens

##### PROCESS INPUT ######


# if __name__ == '__main__':

#     # Get file as argument

#     import sys
#     if len(sys.argv) != 2:
#         print('You need to specify a cool source file to read from.', sys.stderr)
#         sys.exit(1)
#     if not sys.argv[1].endswith('.cl'):
#         print('Argument needs to be a cool source file ending on ".cl".',  sys.stderr)
#         sys.exit(1)

#     sourcefile = sys.argv[1]

#     # Read source file

#     global readed
#     with open(sourcefile, 'r') as source:
#         readed = source.read()
#         lexer.input(readed)

#     # Read tokens

#     while True:
#         token = lexer.token()
#         col = find_column(readed, token)
#         if token is None:
#             break
#         print(token.value, token.lineno, col)
