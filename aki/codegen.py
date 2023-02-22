from llvmlite import ir
from aki import aki_builtins as bi
from aki import aki_types


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
            func = bi.__dict__.get(call_name + "_")
        if not func:
            raise NameError
        return func(self.builder, args)

    def codegen_string(self, token):
        # generates string constants at compile time

        base_text = token.children[0][1:-1]
        text = self.strings.get(base_text)
        if text is None:
            text = base_text + "\x00"
            bytes_text = bytearray(text, encoding="utf8")
            string_constant = ir.Constant(
                ir.ArrayType(ir.IntType(8), len(bytes_text)), bytes_text
            )
            string_const_ref = ir.GlobalVariable(
                self.module, string_constant.type, f"const:str_txt_{self.str_name}"
            )
            string_const_ref.global_constant = True
            string_const_ref.linkage = "internal"
            string_const_ref.initializer = string_constant

            string_var = ir.GlobalVariable(
                self.module,
                aki_types.String(self.module).type,
                f"const:str_obj_{self.str_name}",
            )
            string_var.global_constant = True
            string_const_ref.linkage = "internal"

            string_var.initializer = aki_types.String(self.module).type(
                [
                    ir.Constant(ir.IntType(64), len(bytes_text)),
                    string_const_ref.bitcast(ir.PointerType(ir.IntType(8))),
                ]
            )
            self.str_name += 1
            self.strings[base_text] = string_var

        else:
            string_var = text

        return string_var
