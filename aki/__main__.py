from aki.walker import Walker, parser
from aki.jitengine import JitEngine

text = r"""
print ("Hello world\n")
print ("What's going on?\n")
print ("Hello world\n")
"""

tree = parser.parse(text)
print(tree.pretty())

jit = JitEngine()

w = Walker()
w.visit(tree)

print(str(w.codegen.module))

mod = jit.compile_ir(str(w.codegen.module))
func_ptr = jit.engine.get_function_address("main")

print(func_ptr)

from ctypes import CFUNCTYPE

cfunc = CFUNCTYPE(None)(func_ptr)
res = cfunc()
print(res)
