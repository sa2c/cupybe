#!/usr/bin/env python3
import cube_file_utils as cfu
import calltree as ct
from sys import argv

filename = argv[1]

call_tree = ct.get_call_tree(filename)

df = ct.calltree_to_df(call_tree).set_index('Cnode ID')

parent_series = df['Parent Cnode ID']

levels = ct.get_level(parent_series)


for cnode_id in levels.index:
    assert levels[cnode_id] == 0 or levels[cnode_id] == levels[parent_series[cnode_id]] + 1 

