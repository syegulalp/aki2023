from llvmlite import ir
from aki import aki_builtins as bi


class Codegen:
    def __init__(self):
        self.module = ir.Module()
        self.str_name = 0
        self.strings = {}

    def codegen_function(self, name="main", ftype=None):
        if not ftype:
            ftype = ir.FunctionType(ir.IntType(8), [])
        func = ir.Function(self.module, ftype, name)
        block = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)
        return func, self.builder

    def codegen_funccall(self, call_name, args):
        func = self.module.globals.get(call_name)
        if not func:
            func = bi.__dict__.get(call_name)
        if not func:
            raise NameError
        return func(self.builder, args)

    def codegen_string(self, token):
        base_text = token.children[0][1:-1]
        text = self.strings.get(base_text)
        if text is None:
            text = base_text.replace("\\n", "\n")
            text += "\x00"
            string_constant = ir.Constant(
                ir.ArrayType(ir.IntType(8), len(text)), bytearray(text, encoding="utf8")
            )
            string_const_ref = ir.GlobalVariable(
                self.module, string_constant.type, f"@str_{self.str_name}"
            )
            string_const_ref.global_constant = True
            string_const_ref.linkage = "internal"
            string_const_ref.initializer = string_constant
            self.str_name += 1
            self.strings[base_text] = string_const_ref
        else:
            string_const_ref = text
        return string_const_ref
