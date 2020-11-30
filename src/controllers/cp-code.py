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
from typeInfer import TypeInferer
from pathlib import Path

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
    tokens = tokenizer(text)
    pprint_tokens(tokens)
    print('=================== PARSE =====================')
    #print([t.token_type for t in tokens])
    parse, operations = CoolParser(tokens)
    if not operations:  # error y el Token donde se detecto el error viene en parse
        print(f'Unexpected token "{parse.lex}" in line "{parse.line}" and column "{parse.column}"')
        return
    # print('\n'.join(repr(x) for x in parse))
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
    print('============== INFERINING TYPES ===============')
    inferer = TypeInferer(context, errors)
    while inferer.visit(ast, scope):
        pass
    print(scope)
    tree = formatter.visit(ast)
    print(tree)
    print('Context:')
    print(context)
    return ast, errors, context, scope


if __name__ == '__main__':
    p = Path.cwd() / 'test' / '6.cl'

    with open(p) as file:
        run_pipeline(file.read())