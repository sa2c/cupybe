#!/usr/bin/env python3
import cube_file_utils as cfu
import calltree as ct
from sys import argv
from test_utils import SINGLE_FILES
import pytest

@pytest.mark.parametrize("filename",SINGLE_FILES)
def test_get_level(filename):
    
    call_tree = ct.get_call_tree(filename)
    
    # testing series version
    df = ct.calltree_to_df(call_tree).set_index('Cnode ID')
    
    parent_series = df['Parent Cnode ID']
    
    levels = ct.get_level(parent_series)
    
    
    for cnode_id in levels.index:
        assert levels[cnode_id] == 0 or levels[cnode_id] == levels[parent_series[cnode_id]] + 1 
    
    # testing df version
    df = ct.calltree_to_df(call_tree)
    
    parent_series_2 = df[['Cnode ID','Parent Cnode ID']]
    
    levels_2 = ct.get_level(parent_series_2)
    
    for cnode_id in levels_2.index:
        #assert levels_2[cnode_id] == 0 or levels_2[cnode_id] == levels_2[parent_series_2.set_index('Cnode ID')[cnode_id]] + 1 
        assert levels_2[cnode_id] == 0 or levels_2[cnode_id] == levels_2[parent_series_2.set_index('Cnode ID').loc[cnode_id,'Parent Cnode ID']] + 1 
    
if __name__ == "__main__":
    test_get_level()
