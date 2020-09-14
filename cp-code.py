import cmp.visitor as visitor
from cmp.semantic import SemanticError
from cmp.semantic import Attribute, Method, Type
from cmp.semantic import SelfType, AutoType, ErrorType
from cmp.semantic import Context, Scope
from parser import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode
from parser import MemberCallNode, IfThenElseNode, WhileLoopNode, BlockNode, LetInNode, CaseOfNode
from parser import AssignNode, UnaryNode, BinaryNode
from parser import FunctionCallNode, NewNode, AtomicNode
from parser import CoolGrammar, CoolParser
from lexer import tokenizer
from cmp.utils import Token
from cmp.evaluation import evaluate_reverse_parse
from typeCollector import TypeCollector
from typeBuilder import TypeBuilder
from typeChecker import TypeChecker
from formatVisitor import FormatVisitor

WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'


tokens_dict = {
    'CLASS': CoolGrammar['class'],
    'INHERITS': CoolGrammar['inherits'],
    'IF': CoolGrammar['if'],
    'THEN': CoolGrammar['then'],
    'ELSE': CoolGrammar['else'],
    'FI': CoolGrammar['fi'],
    'WHILE': CoolGrammar['while'],
    'LOOP': CoolGrammar['loop'],
    'POOL': CoolGrammar['pool'],
    'LET': CoolGrammar['let'],
    'IN': CoolGrammar['in'],
    'CASE': CoolGrammar['case'],
    'OF': CoolGrammar['of'],
    'ESAC': CoolGrammar['esac'],
    'NEW': CoolGrammar['new'],
    'ISVOID': CoolGrammar['isvoid'],
    'TYPE': CoolGrammar['type'],
    'ID': CoolGrammar['id'],
    'INTEGER': CoolGrammar['integer'],
    'STRING': CoolGrammar['string'],
    'BOOL': CoolGrammar['bool'],
    'ACTION': CoolGrammar['=>'],
    'ASSIGN': CoolGrammar['<-'],
    'LESS': CoolGrammar['<'],
    'LESSEQUAL': CoolGrammar['<='],
    'EQUAL': CoolGrammar['='],
    'INT_COMPLEMENT': CoolGrammar['~'],
    'NOT': CoolGrammar['not'],
    '+': CoolGrammar['+'],
    '-': CoolGrammar['-'],
    '*': CoolGrammar['*'],
    '/': CoolGrammar['/'],
    ':': CoolGrammar[':'],
    ';': CoolGrammar[';'],
    '(': CoolGrammar['('],
    ')': CoolGrammar[')'],
    '{': CoolGrammar['{'],
    '}': CoolGrammar['}'],
    '@': CoolGrammar['@'],
    '.': CoolGrammar['.'],
    ',': CoolGrammar[',']
}


def pprint_tokens(tokens):
    ocur, ccur, semi = CoolGrammar['{'], CoolGrammar['}'], CoolGrammar[';']
    indent = 0
    pending = []
    for token in tokens:
        pending.append(token)
        if token.token_type in {ocur, ccur, semi}:
            if token.token_type == ccur:
                indent -= 1
            print('    '*indent + ' '.join(str(t.token_type) for t in pending))
            pending.clear()
            if token.token_type == ocur:
                indent += 1
    print(' '.join([str(t.token_type) for t in pending]))


def run_pipeline(text):
    print('=================== TEXT ======================')
    print(text)
    print('================== TOKENS =====================')
    tokens = [Token(token.value, tokens_dict[token.type])
              for token in tokenizer(text)] + [Token('$', CoolGrammar.EOF)]
    pprint_tokens(tokens)
    print('=================== PARSE =====================')
    #print([t.token_type for t in tokens])
    parse, operations = CoolParser([t.token_type for t in tokens])
    print('\n'.join(repr(x) for x in parse))
    print('==================== AST ======================')
    ast = evaluate_reverse_parse(parse, operations, tokens)
    formatter = FormatVisitor()
    tree = formatter.visit(ast)
    print(tree)
    print('============== COLLECTING TYPES ===============')
    errors = []
    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context
    print('Errors:', errors)
    print('Context:')
    print(context)
    print('=============== BUILDING TYPES ================')
    builder = TypeBuilder(context, errors)
    builder.visit(ast)
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    print('Context:')
    print(context)
    print('============== CHECKING TYPES ====================')
    checker = TypeChecker(context, errors)
    scope = checker.visit(ast)
    print('Errors: [')
    for error in errors:
        print('\t', error)
    print(']')
    return ast, errors, context, scope


if __name__ == '__main__':
    file = open('code.cl')
    run_pipeline(file.read())
    file.close()
