from lark import Lark
from lark.indenter import PythonIndenter
from lark.visitors import Interpreter

from llvmlite import ir
from aki import codegen

kwargs = dict(postlex=PythonIndenter(), start="file_input")
parser = Lark.open_from_package(
    "lark", "python.lark", ["grammars"], parser="lalr", **kwargs
)

# TODO: load and store


class Walker(Interpreter):
    def __init__(self):
        self.codegen = codegen.Codegen()
        self.fcw = FuncCallWalker(self.codegen)
        self.vw = ValueWalker(self.codegen)

    def file_input(self, tree):
        # ideally, codegen_function w/some options passed?
        function, builder = self.codegen.codegen_function()
        for child in tree.children:
            result = self.visit(child)
        # TODO: no ir references in this module if we can help it
        if not builder.block.is_terminated:
            builder.ret(ir.Constant(function.function_type.return_type, 0))

    def funccall(self, tree):
        children = tree.children
        call_name = self.visit(children[0])
        arguments = [self.fcw.visit(a) for a in children[1].children]
        self.codegen.codegen_funccall(call_name, arguments)

    def expr_stmt(self, tree):
        return self.visit_children(tree)

    def var(self, tree):
        return self.visit_children(tree)[0]

    def arguments(self, tree):
        return self.visit_children(tree)

    def name(self, tree):
        return str(tree.children[0])

    def string(self, token):
        return self.codegen.codegen_string(token)

    def number(self, tree):
        val = tree.children[0]
        return self.codegen.codegen_int(val)

    def assign(self, tree):
        target_name = self.visit(tree.children[0])
        value = self.vw.visit(tree.children[1])
        x = self.codegen.codegen_assignment(target_name, value)
        return x

    def arith_expr(self, tree):
        lhs = self.visit(tree.children[0])
        rhs = self.visit(tree.children[2])
        op = str(tree.children[1])
        return self.codegen.codegen_operation(lhs, rhs, op)

    # def const_true(self, tree):
    #     return ir.Constant(ir.IntType(1), 1)

    def while_stmt(self, tree):
        b = self.codegen.builder
        condition, operations = tree.children[0:2]
        start, loop, end = self.codegen.codegen_loop_start()
        condition = self.visit(condition)
        b.cbranch(condition, loop, end)
        b.position_at_start(loop)
        for op in operations.children:
            self.visit(op)
        b.branch(start)
        b.position_at_start(end)

    def comparison(self, tree):
        lhs, op, rhs = tree.children
        lhs = self.vw.visit(lhs)
        rhs = self.vw.visit(rhs)
        op = op.children[0]
        return self.codegen.codegen_comparison(lhs, rhs, op)


class ValueWalker(Walker):
    def __init__(self, cgen: codegen.Codegen):
        self.codegen = cgen

    def name(self, tree):
        return self.codegen.codegen_get_value(tree.children[0])


class FuncCallWalker(Walker):
    def __init__(self, cgen: codegen.Codegen):
        self.codegen = cgen

    def name(self, tree):
        name_val = tree.children[0]
        return self.codegen.codegen_get_value(name_val)
