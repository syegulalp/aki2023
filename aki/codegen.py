from llvmlite import ir

from aki import aki_types


class Codegen:
    def __init__(self):
        self.module = ir.Module()
        self.str_name = 0
        self.strings = {}
        self.symtab = {}

    def get_identified_type(self, i_type, klass):
        type_to_get = self.module.context.get_identified_type(i_type)
        type_to_get.__class__ = klass
        return type_to_get

    def codegen_function(self, name="main", ftype=None):
        if not ftype:
            ftype = ir.FunctionType(ir.IntType(8), [])
        func = ir.Function(self.module, ftype, name)
        block = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)
        return func, self.builder

    def codegen_get_var(self, name):
        var = self.symtab.get(name)
        if var is None:
            raise ValueError
        return var

    def codegen_get_value(self, name):
        var = self.codegen_get_var(name)
        if isinstance(var, ir.AllocaInstr):
            var = self.builder.load(var)
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
            if isinstance(value.type, aki_types.AkiScalar):
                var = self.builder.alloca(value.type, name=target_name)
                self.builder.store(value, var)
                self.symtab[target_name] = var
            else:
                self.symtab[target_name] = value
                var = value
        else:
            self.builder.store(value, var)
        return var

    def codegen_operation(self, lhs, rhs, operation):
        t = lhs.type
        op = getattr(t, t.aki_ops[operation])
        result = op(self.builder, lhs, rhs)
        return result

    def codegen_comparison(self, lhs, rhs, operation):
        t = lhs.type
        op = getattr(t, t.aki_comps[operation])
        result = op(self.builder, lhs, rhs)
        return result

    def codegen_loop_start(self):
        condition_block = self.builder.append_basic_block("loop_start")
        loop_block = self.builder.append_basic_block("loop_body")
        after_loop_block = self.builder.append_basic_block("after_loop")
        self.builder.branch(condition_block)
        self.builder.position_at_start(condition_block)
        return condition_block, loop_block, after_loop_block

    def codegen_int(self, value):
        int_value = int(value)
        t = aki_types.Int.make(64)
        f = ir.Constant(t, int_value)
        return f

    def codegen_string(self, token):
        base_text = token.children[0][1:-1]
        return self.codegen_string_constant(base_text)

    def codegen_string_constant(self, base_text):
        text = self.strings.get(base_text)
        if text is None:
            string_var = aki_types.StringConstant(self, base_text, self.str_name)
            self.str_name += 1
            self.strings[base_text] = string_var
            string_var = string_var.value
        else:
            string_var = text.value

        return string_var
