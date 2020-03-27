#!/usr/bin/env python3
from sys import argv
import calltree as ct
import cube_file_utils as cfu
import tree_parsing as tp

lines = ct.get_call_tree_lines(cfu.get_cube_dump_w_text(argv[1]))

assert list(tp.iterate(tp.hierarchy(lines, tp.level_fun))) == lines
print("All ok")
