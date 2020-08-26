#!/usr/bin/env python3

import calltree as ct
import cube_file_utils as cfu
import calltree_conversions as cc
import metrics as mt
import test_utils as tu

import pandas as pd
import numpy as np
from test_utils import SINGLE_FILES
import pytest

@pytest.mark.parametrize("input_file",SINGLE_FILES)
def test_convert_df_to_inclusive(input_file):
    '''
    This test checks that the function to compute the inclusive data from the 
    exclusive data yields the same values as the ones obtained from `cube_dump`
    using the 'incl' flag.
    '''
   
    convertible_metrics = mt.get_inclusive_convertible_metrics(input_file)
    
    def get_df(exclusive):
        return (cfu.get_dump(profile_file=input_file, exclusive=exclusive)
            .set_index([ 'Cnode ID', 'Thread ID' ])
            .rename_axis(mapper=['metric'], axis='columns')
            .sort_index())
    
    dump_excl = get_df(exclusive = True)
    
    dump_incl = get_df(exclusive = False)
    
    calltree = ct.get_call_tree(input_file)
    
    # dataframe conversion
    
    dump_excl = cc.select_metrics( dump_excl, convertible_metrics)
    dump_incl_comp = cc.convert_df_to_inclusive(dump_excl, calltree).sort_index()
    
    dump_incl = cc.select_metrics(dump_incl, convertible_metrics)
    
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
    
        series_incl_comp = cc.convert_series_to_inclusive(series_excl,
                                                          calltree).sort_index()
    
        assert any(series_excl != series_incl)
        print("Inclusive and exclusive results partially differ as expected.")
        assert any(series_excl == series_incl)
        print("Inclusive and exclusive results are partially equal as expected.")
    
        tu.check_float_equality(series_incl_comp,series_incl)
    
        print(
            "Results from conversion coincide with the ones coming from cube_dump."
        )

if __name__ == "__main__":
    test_convert_df_to_inclusive()
