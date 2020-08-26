import cmp.visitor as visitor
from cmp.semantic import Scope, SelfType, AutoType, ErrorType, SemanticError
from parser import ProgramNode, ClassDeclarationNode, AttrDeclarationNode, FuncDeclarationNode, IfThenElseNode, WhileLoopNode, BlockNode, LetInNode, CaseOfNode, AssignNode, UnaryNode, BinaryNode, LessEqualNode, LessNode, EqualNode, ArithmeticNode, NotNode, IsVoidNode, ComplementNode, FunctionCallNode, MemberCallNode, NewNode, AtomicNode, IntegerNode, IdNode, StringNode, BoolNode


WRONG_SIGNATURE = 'Method "%s" already defined in "%s" with a different signature.'
SELF_IS_READONLY = 'Variable "self" is read-only.'
LOCAL_ALREADY_DEFINED = 'Variable "%s" is already defined in method "%s".'
INCOMPATIBLE_TYPES = 'Cannot convert "%s" into "%s".'
VARIABLE_NOT_DEFINED = 'Variable "%s" is not defined in "%s".'
INVALID_OPERATION = 'Operation is not defined between "%s" and "%s".'


class TypeChecker:
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

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = Scope()
        for class_declaration in node.declarations:
            self.visit(class_declaration, scope.create_child())
        return scope

    # class <type> [inherits <type> ] {
        #   <feature_list> }
    @visitor.when(ClassDeclarationNode)
    def visit(self, node, scope):
        self.current_type = self.context.get_type(node.id)

        for f in node.features:
            if isinstance(f, AttrDeclarationNode):
                self.visit(f, scope.create_child())

        for a in self.current_type.attributes:
            scope.define_variable(a.name, a.type)

        for f in node.features:
            if isinstance(f, FuncDeclarationNode):
                self.visit(f, scope.create_child())

    # id: type [ <- <expression>]
    @visitor.when(AttrDeclarationNode)
    def visit(self, node, scope):
        # check attribute redefinition

        if node.expression:
            self.visit(node.expression, scope.create_child())

            expr_type = node.expression.static_type  # static type of the expression

            node_type = self.current_type.get_attribute(node.id).type
            node_type = self.current_type if isinstance(
                node_type, SelfType) else node_type

            if not expr_type.conforms_to(node_type):
                self.errors.append(INCOMPATIBLE_TYPES %
                                   (expr_type.name, node_type.name))

    # <id> (<id> : <type> , ..., <id> : <type>): <type> {
    #   <expr>
    # };
    @visitor.when(FuncDeclarationNode)
    def visit(self, node, scope):
        # check illegal redefinition

        self.current_method = self.current_type.get_method(node.id)
        scope.define_variable('self', self.current_type)

        # zip empareja uno con uno y crea y array de tuplas
        # a = [1, 2, 3]  b = ['a', 'b', 'c']  => zip(a, b) = [(1, 'a'), (2, 'b'), (3, 'c')]
        for pname, ptype in zip(self.current_method.param_names, self.current_method.param_types):
            scope.define_variable(pname, ptype)

        self.visit(node.body, scope.create_child())

        body_type = node.body.static_type
        return_type = self.current_type if isinstance(
            self.current_method.return_type, SelfType) else self.current_method.return_type

        if not body_type.conforms_to(return_type):
            self.errors.append(INCOMPATIBLE_TYPES %
                               (body_type.name, return_type.name))

    # if <expr> then <expr> else <expr> fi
    @visitor.when(IfThenElseNode)
    def visit(self, node, scope):
        self.visit(node.condition, scope.create_child())

        condition_type = node.condition.static_type
        if not condition_type.conforms_to(self.bool_type):
            self.errors.append(INCOMPATIBLE_TYPES %
                               (condition_type.name, self.bool_type.name))

        self.visit(node.if_body, scope.create_child())
        self.visit(node.else_body, scope.create_child())

        if_type = node.if_body.static_type
        else_type = node.else_body.static_type
        node.static_type = if_type.type_union(else_type)

    # while <expr> loop <expr> pool
    @visitor.when(WhileLoopNode)
    def visit(self, node, scope):
        self.visit(node.condition, scope.create_child())

        condition_type = node.condition.static_type
        if not condition_type.conforms_to(self.bool_type):
            self.errors.append(INCOMPATIBLE_TYPES %
                               (condition_type.name, self.bool_type.name))

        self.visit(node.body, scope.create_child())

        node.static_type = self.object_type

    # { <expr>; ... <expr>; }
    @visitor.when(BlockNode)
    def visit(self, node, scope):
        for exp in node.expressions:
            self.visit(exp, scope.create_child())

        node.static_type = node.expressions[-1].static_type

    # let <id1> : <type1> [ <- <expr1> ], ..., <idn> : <typen> [ <- <exprn> ] in <expr>
    @visitor.when(LetInNode)
    def visit(self, node, scope):
        child_scope = scope.create_child()

        for idx, typex, exp in node.let_body:
            try:
                node_type = self.context.get_type(typex)
            except SemanticError as err:
                self.errors.append(ex.text)
                node_type = ErrorType()

            id_type = self.current_type if isinstance(
                node_type, SelfType) else node_type

            if exp:
                self.visit(exp, scope.create_child())
                exp_type = exp.static_type

                if not exp_type.conforms_to(id_type):
                    self.errors.append(INCOMPATIBLE_TYPES %
                                       (exp_type.name, id_type.name))

            child_scope.define_variable(idx, id_type)

        self.visit(node.in_body, child_scope)
        node.static_type = node.in_body.static_type

    # case <expr0> of
        # <id1> : <type1> => <expr1>
        # . . .
        # <idn> : <typen> => <exprn>
    # esac
    @visitor.when(CaseOfNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())
        node.static_type = None

        for idx, typex, expr in node.branches:
            try:
                node_type = self.context.get_type(typex)
            except SemanticError as err:
                self.errors.append(err.text)
                node_type = ErrorType()

            id_type = self.current_type if isinstance(
                node_type, SelfType) else node_type

            child_scope = scope.create_child()
            child_scope.define_variable(idx, id_type)
            self.visit(expr, child_scope)
            expr_type = expr.static_type

            node.static_type = node.static_type.type_union(
                expr_type) if node.static_type else expr_type

    # <id> <- <expression>
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())
        exp_type = node.expression.static_type

        if scope.is_defined(node.id):
            var = scope.find_variable(node.id)
            node_type = var.type

            if var.name == 'self':
                self.errors.append(SELF_IS_READONLY)
            elif not exp_type.conforms_to(node_type):
                self.errors.append(INCOMPATIBLE_TYPES %
                                   (exp_type.name, node_type.name))
        else:
            self.errors.append(VARIABLE_NOT_DEFINED) % (
                node.id, self.current_method.name)

        node.static_type = exp_type

    @visitor.when(NotNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())
        expr_type = node.expression.static_type

        if not expr_type.conforms_to(self.bool_type):
            self.errors.append(INCOMPATIBLE_TYPES %
                               (expr_type.name, self.bool_type.name))

        node.static_type = self.bool_type

    # <exp1> <= <exp2>
    @visitor.when(LessEqualNode)
    def visit(self, node, scope):
        self.visit(node.left, scope.create_child())
        left_type = node.left.static_type

        if not left_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, self.int_type.name))

        self.visit(node.right, scope.create_child())
        right_type = node.right.static_type

        if not right_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (right_type.name, self.int_type.name))

        node.static_type = self.bool_type

    # <exp1> < <exp2>
    @visitor.when(LessNode)
    def visit(self, node, scope):
        self.visit(node.left, scope.create_child())
        left_type = node.left.static_type

        if not left_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, self.int_type.name))

        self.visit(node.right, scope.create_child())
        right_type = node.right.static_type

        if not right_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (right_type.name, self.int_type.name))

        node.static_type = self.bool_type

    # <exp1> = <exp2>
    @visitor.when(EqualNode)
    def visit(self, node, scope):
        self.visit(node.left, scope.create_child())
        left_type = node.left.static_type

        self.visit(node.right, scope.create_child())
        right_type = node.right.static_type

        # [0 ^ 0 = 0] [1 ^ 1 = 0] [0 ^ 1 = 1] [1 ^ 0 == 1]
        if left_type.conforms_to(self.int_type) ^ right_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, right_type.name))

        if left_type.conforms_to(self.string_type) ^ right_type.conforms_to(self.string_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, right_type.name))

        if left_type.conforms_to(self.bool_type) ^ right_type.conforms_to(self.bool_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, right_type.name))

        node.static_type = self.bool_type

    @visitor.when(ArithmeticNode)
    def visit(self, node, scope):
        self.visit(node.left, scope.create_child())
        left_type = node.left.static_type

        self.visit(node.right, scope.create_child())
        right_type = node.right.static_type

        if not left_type.conforms_to(self.int_type) or not right_type.conforms_to(self.int_type):
            self.errors.append(INVALID_OPERATION %
                               (left_type.name, right_type.name))

        node.static_type = self.int_type

    # isvoid <exp>
    @visitor.when(IsVoidNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())

        node.static_type = self.bool_type

    @visitor.when(ComplementNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope.create_child())

        expr_type = node.expression.static_type
        if not expr_type.conforms_to(self.int_type):
            self.errors.append(INCOMPATIBLE_TYPES %
                               (expr_type.name, self.int_type.name))

        node.static_type = self.int_type

    # <expr>.<id>(<expr>,...,<expr>)
    # <id>(<expr>,...,<expr>)
    # <expr>@<type>.id(<expr>,...,<expr>)
    @visitor.when(FunctionCallNode)
    def visit(self, node, scope):
        self.visit(node.obj, scope.create_child())
        obj_type = node.obj.static_type

        try:
            if node.type:
                try:
                    node_type = self.context.get_type(node.type)
                except SemanticError as err:
                    self.errors.append(err.text)
                    node_type = ErrorType()

                if not obj_type.conforms_to(node_type):
                    self.errors.append(INCOMPATIBLE_TYPES %
                                       (obj_type.name, node_type.name))

                obj_type = node_type

            obj_method = obj_type.get_method(node.id)

            if len(node.args) == len(obj_method.param_types):
                for arg, param_type in zip(node.args, obj_method.param_types):
                    self.visit(arg, scope.create_child())

                    arg_type = arg.static_type

                    if not arg_type.conforms_to(param_type):
                        self.errors.append(INCOMPATIBLE_TYPES %
                                           (arg_type.name, param_type.name))
            else:
                self.errors.append(
                    f'Method {obj_method.name} of {obj_type} only accepts {len(obj_method.param_type)} argument(s)')

            node_type = obj_type if isinstance(
                obj_method.return_type, SelfType) else obj_method.return_type
        except SemanticError as err:
            self.errors.append(err.text)
            node_type = ErrorType()

        node.static_type = node_type

    @visitor.when(MemberCallNode)
    def visit(self, node, scope):
        obj_type = self.current_type

        try:
            method = obj_type.get_method(node.id)

            if len(node.args) == len(method.param_types):
                for arg, param_type in zip(node.args, method.param_types):
                    self.visit(arg, scope.create_child())

                    arg_type = arg.static_type

                    if not arg_type.conforms_to(param_type):
                        self.errors.append(INCOMPATIBLE_TYPES %
                                           (arg_type.name, param_type.name))
            else:
                self.errors.append(
                    f'Method {method.name} of {obj_type} only accepts {len(method.param_type)} argument(s)')

            node_type = obj_type if isinstance(
                method.return_type, SelfType) else method.return_type

        except SemanticError as err:
            self.errors.append(err.text)

        node.static_type = node_type

    # new <type>
    @visitor.when(NewNode)
    def visit(self, node, scope):
        try:
            node_type = self.context.get_type(node.type)
        except SemanticError as err:
            self.errors.append(err.text)
            node_type = ErrorType()

        node.static_type = node_type

    @visitor.when(IntegerNode)
    def visit(self, node, scope):
        node.static_type = self.int_type

    @visitor.when(StringNode)
    def visit(self, node, scope):
        node.static_type = self.string_type

    @visitor.when(IdNode)
    def visit(self, node, scope):
        if scope.is_defined(node.lex):
            node_type = scope.find_variable(node.lex).type
        else:
            node_type = ErrorType()
            self.errors.append(VARIABLE_NOT_DEFINED %
                               (node.lex, self.current_method.name))

        node.static_type = node_type

    @visitor.when(BoolNode)
    def visit(self, node, scope):
        node.static_type = self.bool_type
