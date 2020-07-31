import pyl.lex as lex

#### Tokens list ####
literals = ['+', '-', '*', '/', ':', ';', '(', ')', '{', '}', '@', '.', ',']

keywords = {
    'class': 'CLASS',
    'inhirits': 'INHIRITS',
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
    'esac': 'ESAC',
    'new': 'NEW',
    'isvoid': 'ISVOID'
}

ignored = [' ', '\n', '\f', '\r', '\t', '\v']

tokens = ['TYPE', 'ID', 'INTEGER', 'STRING', 'BOOL', 'ACTION', 'ASSIGN',
          'LESS', 'LESSEQUAL', 'EQUAL', 'INT_COMPLEMENT', 'NOT'] + list(keywords.values())

### TOKENS RULES ###

#### Primitive values #####


def t_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"[^\0\n"]*(\\\n[^\0\n"]*)*"'
    t.value = t.value[1:-1]
    return t


def t_BOOL(t):
    r'(true|false)'
    t.value = True if t == 'true' else False
    return t


def t_COMMENT(t):
    r'--[^\n]+\n|\(\*[^(\*\))]+\*\)'
    pass


def t_TYPE(t):
    r'[nN][oO][tT]'
    return t

# Identifiers


def t_TYPE(t):
    r'[A-Z][A-Za-z0-9_]*'
    return t


def t_ID(t):
    r'[a-z][A-Za-z0-9_]*'
    t.type = keywords.get(t.value.lower(), 'ID')
    return t

# Operators


t_ASSIGN = r'<-'
t_LESS = r'<'
t_LESSEQUAL = r'<='
t_EQUAL = r'='
t_INT_COMPLEMENT = r'~'

# Special keywords

t_ACTION = r'=>'


###### Special rules ######

def t_error(t):
    print("Ilegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)


t_ignore = ''.join(ignored)


##### Create lexer #######

lex.lex()

##### Tokenizer #####


def tokenizer(code):
    lex.input(code)

    tokens = []

    while True:
        token = lex.token()
        if token is None:
            break
        tokens.append(token)

    return tokens


##### PROCCESS INPUT ######

if __name__ == '__main__':

    # Get file as argument

    import sys
    if len(sys.argv) != 2:
        print('You need to specify a cool source file to read from.', file=sys.stderr)
        sys.exit(1)
    if not sys.argv[1].endswith('.cl'):
        print('Argument needs to be a cool source file ending on ".cl".',
              file=sys.stderr)
        sys.exit(1)

    sourcefile = sys.argv[1]

    # Read source file

    with open(sourcefile, 'r') as source:
        lex.input(source.read())

    # Read tokens

    while True:
        token = lex.token()
        if token is None:
            break
        print(token)
