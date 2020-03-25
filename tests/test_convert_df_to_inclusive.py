#!/usr/bin/env python3
'''
This test checks that the function to compute the inclusive data from the 
exclusive data yields the same values as the ones obtained from `cube_dump`
using the 'incl' flag.
'''
import calltree as ct
import cube_file_utils as cfu
import inclusive_conversion as ic
import metrics as mt
import test_utils as tu

import pandas as pd
import numpy as np
from sys import argv

input_file = argv[1]

convertible_metrics = mt.get_inclusive_convertible_metrics(input_file)

def get_df(exclusive):
    return (cfu.get_dump(profile_file=input_file, exclusive=exclusive)
        .set_index([ 'Cnode ID', 'Thread ID' ])
        .rename_axis(mapper=['metric'], axis='columns')
        .sort_index())

dump_excl = get_df(exclusive = True)

dump_incl = get_df(exclusive = False)

calltree = ct.get_call_tree('profile.cubex')

# dataframe conversion

dump_excl = ic.select_metrics( dump_excl, convertible_metrics)
dump_incl_comp = ic.convert_df_to_inclusive(dump_excl, calltree).sort_index()

dump_incl = ic.select_metrics(dump_incl, convertible_metrics)

assert (dump_excl.values != dump_incl.values).any()
print("Inclusive and exclusive results partially differ as expected.")
assert (dump_excl.values == dump_incl.values).any()
print("Inclusive and exclusive results are partially equal as expected.")


tu.check_float_equality(dump_incl_comp,dump_incl)

print(
    "Results from convert_df_to_inclusive coincide with the ones coming from cube_dump."
)

# series conversion
def transform(df):
    return df.unstack( [ name for name in df.index.names if name != 'Cnode ID' ] )

dump_excl = transform(dump_excl)
dump_incl = transform(dump_incl)

for col in dump_excl:
    print(f"Processing column {col}...")
    series_excl = dump_excl[col]
    series_incl = dump_incl[col]

    series_incl_comp = ic.convert_series_to_inclusive(series_excl,
                                                      calltree).sort_index()

    assert any(series_excl != series_incl)
    print("Inclusive and exclusive results partially differ as expected.")
    assert any(series_excl == series_incl)
    print("Inclusive and exclusive results are partially equal as expected.")

    tu.check_float_equality(series_incl_comp,series_incl)

    print(
        "Results from conversion coincide with the ones coming from cube_dump."
    )
