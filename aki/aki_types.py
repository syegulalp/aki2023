from llvmlite import ir


class String:
    def __init__(self, module):
        t: ir.IdentifiedStructType = module.context.get_identified_type("String")
        if not t.elements:
            t.set_body(ir.IntType(64), ir.PointerType(ir.IntType(8)))
        self.type = t
