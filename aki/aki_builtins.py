from llvmlite import ir

def print(builder: ir.IRBuilder, args):
    fn = builder.module.globals.get("printf")
    if fn is None:
        ftype = ir.FunctionType(ir.IntType(8), [ir.PointerType(ir.IntType(8))])
        fn = ir.Function(builder.module, ftype, "printf")

    p = args[0]
    q = builder.bitcast(p, ir.PointerType(ir.IntType(8)))
    result = builder.call(fn, [q])

    return result
