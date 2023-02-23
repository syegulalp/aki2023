from aki.walker import Walker, parser
from aki.jitengine import JitEngine

text = r"""
y = 1
z = y
x = "Hello world"
print(x)
print("Hello world")
"""

tree = parser.parse(text)
# print(tree.pretty())

jit = JitEngine()

w = Walker()
w.visit(tree)

# print(str(w.codegen.module))

mod = jit.compile_ir(str(w.codegen.module))
func_ptr = jit.engine.get_function_address("main")

from ctypes import CFUNCTYPE

cfunc = CFUNCTYPE(None)(func_ptr)
res = cfunc()
