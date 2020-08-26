#!/usr/bin/env python3
'''
This script runs only a convenient function that returns all the info in 
a pandas dataframe.
'''
from calltree import get_call_tree, calltree_to_df
from cube_file_utils import get_cube_dump_w_text
from test_utils import SINGLE_FILES
import pytest

@pytest.mark.parametrize("filename",SINGLE_FILES)
def test_calltree2(filename):
    call_tree = get_call_tree(filename)
    call_tree_df = calltree_to_df(call_tree,full_path = True)

    print("Calltree:")
    print(call_tree)
    print("Dataframe representation of calltree:")
    print(call_tree_df)

if __name__ == '__main__':
    test_calltree2()
