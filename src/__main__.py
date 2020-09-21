import eel
from .controllers import *

eel.init('public')

@eel.expose
def handler(code: str):
    print('================== TOKENS =====================')
    # tokens = [Token(token.value, tokens_dict[token.type])
    #   for token in tokenizer(text)] + [Token('$', CoolGrammar.EOF)]
    tokens = tokenizer(code)
    pprint_tokens(tokens)
    print('=================== PARSE =====================')
    #print([t.token_type for t in tokens])
    parse, operations = CoolParser(tokens)
    if not operations:  # error y el Token donde se detecto el error viene en parse
        print(
            f'Unexpected token "{parse.lex}" in line "{parse.line}" and column "{parse.column}"')
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
    # tree = formatter.visit(ast)
    # print(tree)
    print('Context:')
    print(context)
    return ast, errors, context, scope
        

eel.start('index.html')
