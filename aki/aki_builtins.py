from llvmlite import ir
from aki import aki_types


def print_(builder: ir.IRBuilder, args):
    fn = builder.module.globals.get("printf")
    m: ir.Module = builder.module
    if fn is None:
        ftype = ir.FunctionType(ir.IntType(8), [ir.PointerType(ir.IntType(8))])
        fn = ir.Function(builder.module, ftype, "printf")

    for arg in args:
        if isinstance(arg.type, ir.IntType):
            raise NotImplementedError

        elif isinstance(arg.type, ir.PointerType):
            if arg.type.pointee == aki_types.String(m).type:
                p1 = builder.gep(
                    arg,
                    [
                        ir.Constant(ir.IntType(32), 0),
                        ir.Constant(ir.IntType(32), 1),
                    ],
                )
                p1 = builder.load(p1)
                result = builder.call(fn, [p1])
                continue

        raise ValueError
