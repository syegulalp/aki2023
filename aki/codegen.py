from llvmlite import ir

from aki import aki_types


class Codegen:
    def __init__(self):
        self.module = ir.Module()
        self.str_name = 0
        self.strings = {}
        self.symtab = {}

    def codegen_function(self, name="main", ftype=None):
        if not ftype:
            ftype = ir.FunctionType(ir.IntType(8), [])
        func = ir.Function(self.module, ftype, name)
        block = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)
        return func, self.builder

    def codegen_get_var(self, name, load=False):
        var = self.symtab.get(name)
        if var is None:
            raise ValueError
        return var

    def codegen_funccall(self, call_name, args):
        func = self.module.globals.get(call_name)
        from aki import aki_builtins as bi

        if not func:
            func = bi.__dict__.get(call_name)
        if not func:
            func = bi.__dict__.get(call_name + "_")
        if not func:
            raise NameError
        return func(self, args)

    def codegen_assignment(self, target_name, value):
        var = self.symtab.get(target_name)
        if var is None:
            if not isinstance(value.type, ir.PointerType):
                var = self.builder.alloca(value.type, name=target_name)
                self.builder.store(value, var)
                self.symtab[target_name] = var
            else:
                self.symtab[target_name] = value
                var = value
        return var

    def codegen_int(self, value):
        int_value = int(value)
        return ir.Constant(ir.IntType(64), int_value)

    def codegen_string(self, token):
        base_text = token.children[0][1:-1]
        text = self.strings.get(base_text)
        if text is None:
            string_var = aki_types.StringConstant(self.module, base_text, self.str_name)
            self.str_name += 1
            self.strings[base_text] = string_var
            string_var = string_var.value
        else:
            string_var = text.value

        return string_var
