from llvmlite import ir


class Object:
    def __init__(self, module):
        t: ir.IdentifiedStructType = module.context.get_identified_type("Obj")
        if not t.elements:
            # type | ref count | ptr to obj
            t.set_body(ir.IntType(64), ir.IntType(64), ir.PointerType(ir.IntType(8)))
        self.type = t


class String:
    def __init__(self, module):
        t: ir.IdentifiedStructType = module.context.get_identified_type("String")
        if not t.elements:
            t.set_body(ir.IntType(64), ir.PointerType(ir.IntType(8)))
        self.type = t


class Int:
    def __init__(self, module, width):
        t: ir.IntType = ir.IntType(width)
        self.type = t
