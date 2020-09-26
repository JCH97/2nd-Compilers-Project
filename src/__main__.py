import eel
from controllers import tokenizer, CoolParser, evaluate_reverse_parse, FormatVisitor, TypeChecker, TypeBuilder, TypeCollector, TypeInferer

eel.init('public')

def _tokenizer(code):
    comment = "================== TOKENS ====================="

    return (comment, tokenizer(code))

def _parse(tokens, errors = []):
    comment = '=================== PARSE ====================='

    parse, operations = CoolParser(tokens)

    if not operations:
        errors.append(f'Unexpected token "{parse.lex}" in line "{parse.line}" and column "{parse.column}"')
        return (comment, None, None)
    
    return (comment, parse, operations)

def _getAST(parse, operations, tokens):
    return evaluate_reverse_parse(parse, operations, tokens)

def _collectingTypes(ast, errors = []):
    comment = '============== COLLECTING TYPES ==============='

    collector = TypeCollector(errors)
    collector.visit(ast)
    context = collector.context

    return (comment, context)

def _buildingTypes(context, ast, errors = []):
    comment = "=============== BUILDING TYPES =================="
    builder = TypeBuilder(context, errors)
    builder.visit(ast)

    return comment

def _checkingTypes(context, ast, errors = []):
    comment =  '============== CHECKING TYPES ===================='
    checker = TypeChecker(context, errors)
    scope = checker.visit(ast)

    return (comment, scope)

def _infererTypes(context, ast, scope, errors: list = [], inference: list = []):
    comment = '============== INFERINING TYPES ==============='
    inferer = TypeInferer(context, errors, inference)
    while inferer.visit(ast, scope): pass

    return comment
    
@eel.expose
def handler(code: str):
    errors: list = []

    comment_tokenizer, tokens = _tokenizer(code)
    comment_parser, parser, operations = _parse(tokens, errors)

    if len(errors):
        return {
            'errors': errors
        }

    ast = _getAST(parser, operations, tokens)

    comment_collecting, context = _collectingTypes(ast, errors)
    comment_building = _buildingTypes(context, ast, errors)
    comment_checking, scope = _checkingTypes(context, ast, errors)

    inference: list = []
    
    comment_inferer  = _infererTypes(context, ast, scope, errors, inference)

    return {
        'errors': errors,
        'context': context.__str__(),
        'inference': inference
    }

eel.start('index.html')

# if __name__ == '__main__':
#     from pathlib import Path
    
#     code = (Path.cwd() / 'test' / '3.cl').read_text()
#     handler(code)