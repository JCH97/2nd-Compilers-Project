from cmp import visitor, SelfType, AutoType, ErrorType
from parser import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode, IfThenElseNode, WhileLoopNode, BlockNode, LetInNode, CaseOfNode, AssignNode, UnaryNode, BinaryNode, LessEqualNode, LessNode, EqualNode, ArithmeticNode, NotNode, IsVoidNode, ComplementNode, FunctionCallNode, MemberCallNode, NewNode, AtomicNode, IntegerNode, IdNode, StringNode, BoolNode


class TypeInferer:
    def __init__(self, contxt, errors=[]):
        self.current_type = None
        self.current_method = None
        self.context = contxt
        self.errors = errors

        self.object_type = self.context.get_type('Object')
        self.io_type = self.context.get_type('IO')
        self.string_type = self.context.get_type('String')
        self.bool_type = self.context.get_type('Bool')
        self.int_type = self.context.get_type('Int')

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope):
        self.check = False

        for decl, childScope in zip(node.declarations, scope.children):
            self.visit(decl, childScope)

        return self.check

    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):

        self.current_type = self.context.get_type(node.id.lex)

        # visit attributes and  classDeclarations
        for feature, childScope in zip(node.features, scope.children):
            self.visit(feature, childScope)

        # recorrer todas las variables locales que estan definidas por typeChecker
        for attr, var in zip(self.current_type.attributes, scope.locals):
            if not var.infered:
                if isinstance(var, ErrorType):
                    var.type = AutoType()
                elif isinstance(var, AutoType):
                    pass
                else:
                    self.check = var.infered = True
                    attr.type = var.type

    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        if node.expression:
            attr = self.current_type.get_attribute(node.id.lex)

            # visitar la expression, el scope de la expression esta en 0 xq a los atributos solo se le puede asignar un tipo expression y xq tanto estas tienen su scope en 0
            self.visit(node.expression, scope.children[0], attr.type)
            exp_type = node.expression.static_type

            var = scope.find_variable(node.id.lex)
            if not var.infered:
                if isinstance(var, ErrorType):
                    pass
                elif isinstance(var, AutoType):
                    pass
                else:
                    var_type = exp_type
                    var.infered = self.check = True
                    attr_type = var_type

    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.id.lex)
        return_type = self.current_method.return_type

        #print(len(scope.children), node.id)
        self.visit(node.body, scope.children[0], self.current_type if isinstance(
            return_type, SelfType) else return_type)

        body_type = node.body.static_type

        # recorrido por los parametros del metodo, se visita de uno en adelante xq locaĺ[0] = self
        for i, var in enumerate(scope.locals[1:]):
            if not var.infered:
                if isinstance(var, ErrorType):
                    var_type = AutoType()
                elif isinstance(var, AutoType):
                    pass
                else:
                    var.infered = self.check = True
                    self.current_method.param_types[i] = var.type

        var = self.current_method.return_info
        if not var.infered:
            if isinstance(var, ErrorType):
                pass
            elif isinstance(var, AutoType):
                pass
            else:
                var.type = body_type
                var.infered = self.check = True
                self.current_method.return_type = var.type

    @visitor.when(IfThenElseNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.condition, scope.children[0], self.bool_type)

        self.visit(node.if_body, scope.children[1])
        self.visit(node.else_body, scope.children[2])

        if_type = node.if_body.static_type
        else_type = node.else_body.static_type
        node.static_type = if_type.type_union(else_type)

    @visitor.when(WhileLoopNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.condition, scope.children[0], self.bool_type)

        self.visit(node.body, scope.children[1])

        node.static_type = self.object_type

    @visitor.when(BlockNode)
    def visit(self, node, scope, expected_type=None):
        for exp, child_scope in zip(node.expressions[:-1], scope.children[:-1]):
            self.visit(exp, child_scope)

        node.static_type = node.expressions[-1].static_type

    @visitor.when(LetInNode)
    def visit(self, node, scope, expected_type=None):
        for (idx, typex, exp), child_scope, (i, var) in zip(node.let_body, scope.children[:-1], enumerate(scope.locals)):
            if exp:
                self.visit(exp, child_scope, var.type if var.infered else None)
                expr_type = exp.static_type

                if not var.infered:
                    if isinstance(expr_type, ErrorType):
                        pass
                    elif isinstance(expr_type, AutoType):
                        pass
                    else:
                        var.type = expr_type
                        var.infered = self.check = True
                        node.let_body[i] = (idx.lex, var.type, exp)

        self.visit(node.in_body, scope.children[-1], expected_type)

        for i, var in enumerate(scope.locals):
            if not var.infered:
                if isinstance(var.type, ErrorType):
                    var.type = AutoType()
                elif isinstance(var.type, AutoType):
                    pass
                else:
                    var.infered = self.changed = True
                    self.current_method.params_type[i] = var.type

        node.static_type = node.in_body.static_type

    @visitor.when(CaseOfNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.expression, scope.children[0])

        node.static_type = None

        for (idx, typex, exp), child_scope in zip(node.branches, scope.children[1:]):
            self.visit(exp, child_scope)
            exp_type = exp.static_type

            node.static_type = node.static_type.type_union(
                exp_type) if node.static_type else exp_type

    @visitor.when(AssignNode)
    def visit(self, node, scope, expected_type=None):
        var = scope.find_variable(
            node.id.lex) if scope.is_defined(node.id.lex) else None

        self.visit(node.expression,
                   scope.children[0], var.type if var and var.infered else None)
        expr_type = node.expression.static_type

        if var and not var.infered:
            if isinstance(expr_type, ErrorType) or isinstance(var.type, ErrorType):
                pass
            elif isinstance(expr_type, AutoType):
                pass
            else:
                var.type = expr_type if isinstance(
                    var.type, AutoType) else var.type.type_union(expr_type)

        node.static_type = expr_type

    @visitor.when(NotNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.expression, scope.children[0], self.bool_type)

        node.static_type = self.bool_type

    @visitor.when(LessEqualNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.left, scope.children[0], self.int_type)

        self.visit(node.right, scope.children[1], self.int_type)

        node.static_type = self.bool_type

    @visitor.when(LessNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.left, scope.children[0], self.int_type)

        self.visit(node.right, scope.children[1], self.int_type)

        node.static_type = self.bool_type

    @visitor.when(EqualNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.left, scope.children[0], node.right.static_type)

        self.visit(node.right, scope.children[1], node.left.static_type)

        node.static_type = self.bool_type

    @visitor.when(ArithmeticNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.left, scope.children[0], self.int_type)
        self.visit(node.right, scope.children[1], self.int_type)

        node.static_type = self.int_type

    @visitor.when(IsVoidNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.expression, scope.children[0])

        node.static_type = self.bool_type

    @visitor.when(ComplementNode)
    def visit(self, node, scope, expected_type=None):
        self.visit(node.expression, scope.children[0], self.int_type)

        node.static_type = self.int_type

    @visitor.when(FunctionCallNode)
    def visit(self, node, scope, expected_type=None):
        node_type = None

        if node.type:
            try:
                node_type = self.context.get_type(node.type.lex)
            except SystemError as err:
                node_type = ErrorType()
            else:
                if isinstance(node_type, SelfType) or isinstance(node_type, AutoType):
                    node_type = ErrorType()

        self.visit(node.obj, scope.children[0], node_type)
        obj_type = node.obj.static_type

        try:
            obj_type = node_type if node_type else obj_type

            obj_method = obj_type.get_method(node.id.lex)

            node_type = obj_type if isinstance(
                obj_method.return_type, SelfType) else obj_method.return_type

        except SemanticError:
            node_type = ErrorType()
            obj_method = None

        if obj_method and len(node.args) == len(obj_method.param_types):
            for arg, var, child_scope in zip(node.args, obj_method.param_infos, scope.children[1:]):
                self.visit(arg, child_scope, var.type if var.infered else None)
        else:
            for arg, child_scope in zip(node.args, scope.children[1:]):
                self.visit(arg, child_scope)

        node.static_type = node_type

    @visitor.when(MemberCallNode)
    def visit(self, node, scope, expected_type=None):
        obj_type = self.current_type

        try:
            obj_method = obj_type.get_method(node.id.lex)

            node_type = obj_type if isinstance(
                obj_method.return_type, SelfType) else obj_method.return_type
        except SemanticError:
            node_type = ErrorType()
            obj_method = None

        if obj_method and len(node.args) == len(obj_method.param_types):
            for arg, var, child_scope in zip(node.args, obj_method.param_infos, scope.children):
                self.visit(arg, child_scope, var.type if var.infered else None)
        else:
            for arg, child_scope in zip(node.args, scope.children):
                self.visit(arg, child_scope)

        node.static_type = node_type

    @visitor.when(NewNode)
    def visit(self, node, scope, expected_type=None):
        try:
            node_type = self.context.get_type(node.type.lex)
        except SemanticError:
            node_type = ErrorType()

        node.static_type = node_type

    @visitor.when(IntegerNode)
    def visit(self, node, scope, expected_type=None):
        node.static_type = self.int_type

    @visitor.when(StringNode)
    def visit(self, node, scope, expected_type=None):
        node.static_type = self.string_type

    @visitor.when(IdNode)
    def visit(self, node, scope, expected_type=None):
        if scope.is_defined(node.token.lex):
            var = scope.find_variable(node.token.lex)

            if expected_type and not var.infered:
                if isinstance(expected_type, ErrorType) or isinstance(expected_type, SelfType):
                    print(f'Error!!!! {expected_type}')
                elif isinstance(expected_type, AutoType):
                    print(f'{expected_type}?????')
                elif isinstance(var.type, ErrorType):
                    pass
                elif isinstance(var.type, AutoType):
                    var.type = expected_type
                elif not var.type.conforms_to(expected_type):
                    var.type = expected_type if expected_type.conforms_to(
                        var.type) else ErrorType()

            node_type = var.type if var.infered else AutoType()
        else:
            node_type = ErrorType()

        node.static_type = node_type

    @visitor.when(BoolNode)
    def visit(self, node, scope, expected_type=None):
        node.static_type = self.bool_type
