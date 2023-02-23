from llvmlite import ir


class AkiType(ir.IdentifiedStructType):
    pass


# class Object(AkiType):
#     def __init__(self, codegen):
#         t: ir.IdentifiedStructType = codegen.get_identified_type("Obj")
#         if not t.elements:
#             # type | ref count | ptr to obj
#             t.set_body(ir.IntType(64), ir.IntType(64), ir.PointerType(ir.IntType(8)))
#         self.type = t


class StringConstant(AkiType):
    def __init__(self, codegen, base_value, name):
        t: ir.IdentifiedStructType = codegen.get_identified_type(
            "String", self.__class__
        )
        if not t.elements:
            t.set_body(ir.IntType(64), ir.PointerType(ir.IntType(8)))

        text = base_value + "\x00"
        bytes_text = bytearray(text, encoding="utf8")
        string_constant = ir.Constant(
            ir.ArrayType(ir.IntType(8), len(bytes_text)), bytes_text
        )
        string_const_ref = ir.GlobalVariable(
            codegen.module, string_constant.type, f"const:str_txt_{name}"
        )
        string_const_ref.global_constant = True
        string_const_ref.linkage = "internal"
        string_const_ref.initializer = string_constant

        self.const_ref = string_const_ref

        string_var = ir.GlobalVariable(
            codegen.module,
            t,
            f"const:str_obj_{name}",
        )
        string_var.global_constant = True
        string_var.linkage = "internal"
        string_var.initializer = t(
            [
                ir.Constant(ir.IntType(64), len(bytes_text)),
                string_const_ref.bitcast(ir.PointerType(ir.IntType(8))),
            ]
        )
        self.value = string_var

    def aki_str(self, val, codegen):
        builder = codegen.builder
        p1 = builder.gep(
            val,
            [
                ir.Constant(ir.IntType(32), 0),
                ir.Constant(ir.IntType(32), 1),
            ],
        )
        p1 = builder.load(p1)
        return p1


class AkiScalar:
    @classmethod
    def make(cls, *a, **ka):
        item = cls(*a, **ka)
        item.__class__ = cls
        return item


class Int(ir.IntType, AkiScalar):
    aki_ops = {"+": "add", "-": "sub", "*": "mul", "/": "div"}

    def add(self, builder, lhs, rhs):
        return builder.add(lhs, rhs)

    def sub(self, builder, lhs, rhs):
        return builder.sub(lhs, rhs)

    def mul(self, builder, lhs, rhs):
        return builder.mul(lhs, rhs)

    def div(self, builder, lhs, rhs):
        return builder.sdiv(lhs, rhs)

    aki_comps = {">": "gt", "<": "lt"}

    def lt(self, builder, lhs, rhs):
        return builder.icmp_signed("<", lhs, rhs)
