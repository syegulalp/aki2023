from llvmlite import ir

from aki import aki_types, codegen as cg


def print_(codegen: cg.Codegen, args):
    builder = codegen.builder
    m: ir.Module = builder.module
    fn = m.globals.get("printf")
    if fn is None:
        ftype = ir.FunctionType(ir.IntType(8), [ir.PointerType(ir.IntType(8))])
        fn = ir.Function(builder.module, ftype, "printf")

    for arg in args:
        result = None

        if isinstance(arg.type.pointee.aki, aki_types.StringConstant):
            result = arg.type.pointee.aki.aki_str(arg, codegen)

        if result:
            builder.call(fn, [result])
            continue

        raise ValueError
