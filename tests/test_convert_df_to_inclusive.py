#!/usr/bin/env python3.8
'''
This test checks that the function to compute the inclusive data from the 
exclusive data yields the same values as the ones obtained from `cube_dump`
using the 'incl' flag.
'''
import calltree as ct
import datadump as dd
import merger as mg
import metrics as mt

import pandas as pd
import numpy as np
from sys import argv

input_file = argv[1]

convertible_metrics = mt.get_inclusive_convertible_metrics(input_file)

dump_excl = (dd.get_dump(profile_file=input_file, exclusive=True).set_index([
    'Cnode ID', 'Thread ID'
]).unstack('Thread ID').rename_axis(mapper=['metric', 'Thread ID'],
                                    axis='columns').sort_index())

dump_incl = (dd.get_dump(profile_file=input_file, exclusive=False).set_index([
    'Cnode ID', 'Thread ID'
]).unstack('Thread ID').rename_axis(mapper=['metric', 'Thread ID'],
                                    axis='columns').sort_index())

calltree = ct.get_call_tree('profile.cubex')

# dataframe conversion

dump_excl = mg.select_inclusive_convertible_metrics( dump_excl, convertible_metrics)
dump_incl_comp = mg.convert_df_to_inclusive(dump_excl,
                                            calltree).sort_index()
dump_incl = mg.select_inclusive_convertible_metrics(dump_incl,
                                                    convertible_metrics)

assert (dump_excl.values != dump_incl.values).any()
print("Inclusive and exclusive results partially differ as expected.")
assert (dump_excl.values == dump_incl.values).any()
print("Inclusive and exclusive results are partially equal as expected.")

def check_float_equality(a,b):
    comp = a.values 
    ref = b.values
    den = (np.abs(comp) + np.abs(ref))
    check = np.abs(comp-ref)/ den
    
    assert np.all((check < 1e-5) | (a == b))

check_float_equality(dump_incl_comp,dump_incl)

print(
    "Results from convert_df_to_inclusive coincide with the ones coming from cube_dump."
)

# series conversion
for col in dump_excl:
    print(f"Processing column {col}...")
    series_excl = dump_excl[col]
    series_incl = dump_incl[col]

    series_incl_comp = mg.convert_series_to_inclusive(series_excl,
                                                      calltree).sort_index()

    assert any(series_excl != series_incl)
    print("Inclusive and exclusive results partially differ as expected.")
    assert any(series_excl == series_incl)
    print("Inclusive and exclusive results are partially equal as expected.")

    check_float_equality(series_incl_comp,series_incl)

    print(
        "Results from conversion coincide with the ones coming from cube_dump."
    )
