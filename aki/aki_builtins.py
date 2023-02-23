from llvmlite import ir

from aki import aki_types, codegen as cg


def print_(codegen: cg.Codegen, args):
    builder = codegen.builder
    m: ir.Module = builder.module
    fn = m.globals.get("printf")
    if fn is None:
        ftype = ir.FunctionType(
            ir.IntType(8), [ir.PointerType(ir.IntType(8))], var_arg=True
        )
        fn = ir.Function(builder.module, ftype, "printf")

    formatter = []
    out_args = []

    for arg in args:
        result = None

        if isinstance(arg.type, ir.IntType):
            result = arg
            formatter.append("%i")

        elif isinstance(arg.type, ir.PointerType):
            t = arg.type.pointee
            if isinstance(t, aki_types.StringConstant):
                result = t.aki_str(arg, codegen)
                formatter.append("%s")

        if not result:
            raise ValueError

        out_args.append(result)

    formatter.append("\n")

    f1 = codegen.codegen_string_constant(" ".join(formatter))
    return builder.call(fn, [f1.initializer.constant[1]] + out_args)
