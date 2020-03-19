#!/usr/bin/env python3.8
from sys import argv
from calltree import *

cube_dump_w_text = get_cube_dump_w_text(argv[1])
call_tree_lines = get_call_tree_lines(cube_dump_w_text)
calltree = calltree_from_lines(call_tree_lines)
max_len = get_max_len(calltree)
calltree_repr = calltree_to_string(calltree, '', max_len)
print("Tree Representation:")
print(calltree_repr)

import pandas as pd
data = get_full_paths_from_id(calltree)
df = pd.DataFrame(data, columns=['Cnode ID', 'Full Callpath'])
print("Cnode ID vs. Full Callpath dictionary:")
print(df)

df = calltree_to_df(calltree)
print("Dataframe representation of the Call Tree:")
print(df)

# testing that the tree representation matches the one in the 
# cube_dump output
import re
reference = (re.sub(
    '[|-]', '', '\n'.join([
        re.sub('\s*\[\s*\(\s*id=([0-9]+).*$', '\g<1>', line)
        for line in get_call_tree_lines(cube_dump_w_text)
    ])))

calltree_repr = (re.sub('[\-:]', '',
                        calltree_to_string(calltree, '', 0)).replace(
                            '|', ' ').replace('   ', '  '))

for i, (linea, lineb) in enumerate(
        zip(reference.split('\n'), calltree_repr.split('\n'))):
    assert linea == lineb, f" Line {i}: '{linea}' != '{lineb}'"
print("Tree representation test: OK")
