import visitor as visitor
from parser import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode, IfThenElseNode, WhileLoopNode, BlockNode, LetInNode, CaseOfNodeAssignNode, UnaryNode, BinaryNode, LessEqualNode, LessNode, EqualNode, ArithmeticNode, NotNode, IsVoidNode, ComplementNode, FunctionCallNode, MemberCallNode, NewNode, AtomicNode, IntegerNode, IdNode, StringNode, BoolNode


class TypeCheck:
    def __init__(self, context, errors=[]):
        self.context = context
        self.errors = errors
        self.current_type = None
        self.current_method = None

        self.object_type = self.context.get_type('Object')
        self.io_type = self.context.get_type('IO')
        self.int_type = self.context.get_type('Int')
        self.string_type = self.context.get_type('String')
        self.bool_type = self.context.get_type('Bool')

    @visitor('on')
    def visit(self, node):
        pass

    @visitor(ProgramNode)
    def visit(self, node):
        pass
