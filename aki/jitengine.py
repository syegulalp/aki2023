import llvmlite.binding as llvm


class JitEngine:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    def __init__(self):
        self.engine = self.create_execution_engine()
        self.reset()

    def reset(self):
        self.modules = {}
        self.engines = {}

    def create_execution_engine(self):
        self.target = llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine(
            opt=3, codemodel="default"
        )
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, self.target_machine)

        self.pm = llvm.ModulePassManager()
        llvm.PassManagerBuilder().populate(self.pm)
        return engine

    def compile_ir(self, llvm_ir, opt_level=3):
        if opt_level is True:
            opt_level = 3

        try:
            mod = llvm.parse_assembly(llvm_ir)
        except RuntimeError as e:
            print(llvm_ir)
            raise e
        mod.verify()

        with open("output.ll", "w") as f:
            f.write(str(mod))

        if opt_level:
            self.pm.opt_level = opt_level
            self.pm.run(mod)

        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()

        with open("output.opt.ll", "w") as f:
            f.write(str(mod))

        with open("output.obj", "wb") as f:
            f.write(self.target_machine.emit_object(mod))

        with open("output.asm", "w") as f:
            f.write(self.target_machine.emit_assembly(mod))

        return mod
