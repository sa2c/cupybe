#!/usr/bin/env python3.8
'''
This test checks that the function to compute the inclusive data from the 
exclusive data yields the same values as the ones obtained from `cube_dump`
using the 'incl' flag.
'''
import calltree as ct
import datadump as dd
import merger as mg

import pandas as pd
from sys import argv

input_file = argv[1]

dump_excl  = (dd.get_dump(profile_file=input_file,exclusive = True)
        .set_index(['Cnode ID', 'Thread ID'])
        .unstack('Thread ID'))
calltree = ct.get_call_tree('profile.cubex')

dump_incl = mg.convert_df_to_inclusive(dump_excl,calltree).sort_index()

dump_incl_ref  = (dd.get_dump(profile_file=input_file,exclusive = False)
        .set_index(['Cnode ID', 'Thread ID'])
        .unstack('Thread ID')).sort_index()

assert any(dump_excl != dump_incl_ref)
print("Inclusive and exclusive results partially differ as expected.")
assert any(dump_excl == dump_incl_ref)
print("Inclusive and exclusive results are partially equal as expected.")
assert all(dump_incl_ref == dump_incl)
print("Results from convert_df_to_inclusive coincide with the ones coming from cube_dump.")

