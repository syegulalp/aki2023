from llvmlite import ir
from aki import aki_types


def print_(builder: ir.IRBuilder, args):
    fn = builder.module.globals.get("printf")
    m: ir.Module = builder.module
    if fn is None:
        ftype = ir.FunctionType(ir.IntType(8), [ir.PointerType(ir.IntType(8))])
        fn = ir.Function(builder.module, ftype, "printf")

    p = args[0]
    
    # right now we only deal with strings
    
    if p.type.pointee == aki_types.String(m).type:
        p1 = builder.gep(
            p,
            [
                ir.Constant(ir.IntType(32), 0),
                ir.Constant(ir.IntType(32), 1),
            ],
        )
        p1 = builder.load(p1)
        result = builder.call(fn, [p1])
        return result
    else:
        raise ValueError
