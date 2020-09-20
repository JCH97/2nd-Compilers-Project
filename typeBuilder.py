import cmp.visitor as visitor

from cmp.semantic import AutoType, SelfType, ErrorType, SemanticError
from parser import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode

ERROR = '[Error] Linea %d: , Columna %d: '


class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors

        # Building built-in types
        self.object_type = self.context.get_type('Object')

        self.io_type = self.context.get_type('IO')
        self.io_type.set_parent(self.object_type)

        self.int_type = self.context.get_type('Int')
        self.int_type.set_parent(self.object_type)
        self.int_type.sealed = True

        self.string_type = self.context.get_type('String')
        self.string_type.set_parent(self.object_type)
        self.string_type.sealed = True

        self.bool_type = self.context.get_type('Bool')
        self.bool_type.set_parent(self.object_type)
        self.bool_type.sealed = True

        self.object_type.define_method('abort', [], [], self.object_type)
        self.object_type.define_method('type_name', [], [], self.string_type)
        self.object_type.define_method('copy', [], [], SelfType())

        self.io_type.define_method('out_string', ['x'], [
                                   self.string_type], SelfType())
        self.io_type.define_method(
            'out_int', ['x'], [self.int_type], SelfType())
        self.io_type.define_method('in_string', [], [], self.string_type)
        self.io_type.define_method('in_int', [], [], self.int_type)

        self.string_type.define_method('length', [], [], self.int_type)
        self.string_type.define_method(
            'concat', ['s'], [self.string_type], self.string_type)
        self.string_type.define_method(
            'substr', ['i', 'l'], [self.int_type, self.int_type], self.string_type)

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node):
        for def_class in node.declarations:
            self.visit(def_class)

        try:
            self.context.get_type('Main').get_method('main')
        except SemanticError:
            self.errors.append(
                ERROR % (node.line, node.column) + 'The class "Main" and its method "main" are needed.')

    @visitor.when(ClassDeclarationNode)
    def visit(self, node):
        self.current_type = self.context.get_type(node.id.lex)

        if node.parent:
            try:
                parent_type = self.context.get_type(node.parent.lex)
                self.current_type.set_parent(parent_type)
            except SemanticError as ex:
                self.errors.append(
                    ERROR % (node.parent.line, node.parent.column) + ex.text)
        else:
            self.current_type.set_parent(self.object_type)

        for feature in node.features:
            self.visit(feature)

    @visitor.when(AttrDeclarationNode)
    def visit(self, node):
        try:
            attr_type = self.context.get_type(node.type.lex)
        except SemanticError as ex:
            self.errors.append(
                ERROR % (node.type.line, node.type.column) + ex.text)
            attr_type = ErrorType()

        try:
            self.current_type.define_attribute(node.id.lex, attr_type)
        except SemanticError as ex:
            self.errors.append(
                ERROR % (node.id.line, node.id.column) + ex.text)

    @visitor.when(FuncDeclarationNode)
    def visit(self, node):
        arg_names, arg_types = [], []
        for idx, typex in node.params:
            try:
                arg_type = self.context.get_type(typex.lex)
            except SemanticError as ex:
                self.errors.append(
                    ERROR % (typex.line, typex.column) + ex.text)
                arg_type = ErrorType()

            arg_names.append(idx.lex)
            arg_types.append(arg_type)

        try:
            ret_type = self.context.get_type(node.type.lex)
        except SemanticError as ex:
            self.errors.append(
                ERROR % (node.type.line, node.type.column) + ex.text)
            ret_type = ErrorType()

        try:
            self.current_type.define_method(
                node.id.lex, arg_names, arg_types, ret_type)
        except SemanticError as ex:
            self.errors.append(
                ERROR % (node.type.line, node.type.column) + ex.text)
