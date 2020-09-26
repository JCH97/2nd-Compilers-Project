from .cmp import visitor
from .cmp import Context, Scope, SelfType, AutoType, ErrorType, SemanticError
from .parser import ProgramNode, ClassDeclarationNode

ERROR = 'Linea %d: , Columna %d: '


class TypeCollector(object):
    def __init__(self, errors = []):
        self.context = Context()
        self.errors = errors

        self.context.add_type(SelfType())
        self.context.add_type(AutoType())

        self.context.create_type('Object')
        self.context.create_type('String')
        self.context.create_type('Int')
        self.context.create_type('IO')
        self.context.create_type('Bool')

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        for d in node.declarations:
            self.visit(d)

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        try:
            self.context.create_type(node.id.lex)
        except SemanticError as err:
            self.errors.append(ERROR % (node.id.line, node.id.column) + err)
