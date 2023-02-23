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
        return self.codegen.codegen_assignment(target_name, value)


class ValueWalker(Walker):
    def __init__(self, cgen: codegen.Codegen):
        self.codegen = cgen

    def name(self, tree):
        return self.codegen.codegen_get_var(tree.children[0])


class FuncCallWalker(Walker):
    def __init__(self, cgen: codegen.Codegen):
        self.codegen = cgen

    def name(self, tree):
        name_val = tree.children[0]
        return self.codegen.codegen_get_var(name_val, load=True)
