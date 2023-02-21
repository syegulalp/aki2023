from lark import Lark
from lark.indenter import PythonIndenter
from lark.visitors import Interpreter

from llvmlite import ir
from aki import codegen

kwargs = dict(postlex=PythonIndenter(), start="file_input")
parser = Lark.open_from_package(
    "lark", "python.lark", ["grammars"], parser="lalr", **kwargs
)


class Walker(Interpreter):
    def __init__(self):
        self.codegen = codegen.Codegen()

    def file_input(self, tree):
        # ideally, codegen_function w/some options passed?
        function, builder = self.codegen.codegen_function()
        for child in tree.children:
            result = self.visit(child)
        # TODO: no ir references in this module if we can help it
        builder.ret(ir.Constant(function.function_type.return_type, 0))

    def funccall(self, tree):
        call_name, arguments = self.visit_children(tree)
        self.codegen.codegen_funccall(call_name, arguments)

    def expr_stmt(self, tree):
        return self.visit_children(tree)

    def var(self, tree):
        return self.visit_children(tree)[0]

    def arguments(self, tree):
        return self.visit_children(tree)

    def name(self, token):
        return str(token.children[0])

    def string(self, token):
        return self.codegen.codegen_string(token)
