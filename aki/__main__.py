from aki.walker import Walker, parser
from aki.jitengine import JitEngine

text = r"""
x = "Hello world"
# print("Hello", "world")
# print("Hello world")
z = 1
while z<5:
    y = 1
    while y<20:        
        print("You have", y, "turns left.")
        y = y+1
    z=z+1    
"""

tree = parser.parse(text)
open("output.tree", "w", encoding="utf8").write(tree.pretty())

jit = JitEngine()

w = Walker()
w.visit(tree)

mod = jit.compile_ir(str(w.codegen.module))
func_ptr = jit.engine.get_function_address("main")

from ctypes import CFUNCTYPE

cfunc = CFUNCTYPE(None)(func_ptr)
res = cfunc()
