#!/usr/bin/env python3
import calltree as ct
from cube_file_utils import get_cube_dump_w_text
from test_utils import SINGLE_FILES
from test_utils import SINGLE_FILE_CPP
import pytest

@pytest.mark.parametrize("filename",SINGLE_FILES)
def test_calltree1(filename):
    '''
    This script runs the algorithm, prints the results, and checks 
    that the representation of the call tree matches the one that is 
    "scraped" from the cube_dump output.
    '''
    cube_dump_w_text = get_cube_dump_w_text(filename)
    call_tree_lines = ct.get_call_tree_lines(cube_dump_w_text)
    calltree = ct.calltree_from_lines(call_tree_lines)
    max_len = ct.get_max_len(calltree)
    calltree_repr = ct.calltree_to_string(calltree, max_len)
    print("Tree Representation:")
    print(calltree_repr)
    
    import pandas as pd
    data = ct.get_fpath_vs_id(calltree)
    df = pd.DataFrame(data, columns=['Cnode ID', 'Full Callpath'])
    print("Cnode ID vs. Full Callpath dictionary:")
    print(df)
    
    df = ct.calltree_to_df(calltree)
    print("Dataframe representation of the Call Tree:")
    print(df)
    
    # testing that the tree representation matches the one in the 
    # cube_dump output
    import re
    def clean_line(line):
        l1 = re.sub(r'\s*\[\s*\(\s*id=([0-9]+).*$', r'\g<1>', line)
        return re.sub(r'\s*\[with.*\]\s*','',l1)
    reference = (re.sub(
        r'[:|-]', '', '\n'.join([
            clean_line(line)
            for line in ct.get_call_tree_lines(cube_dump_w_text)
        ])))
    
    calltree_repr = (re.sub(r'[\-:]', '',
                            ct.calltree_to_string(calltree, 0)).replace(
                                '|', ' ').replace('   ', '  '))
    
    for i, (linea, lineb) in enumerate(
            zip(reference.split('\n'), calltree_repr.split('\n'))):
        assert linea == lineb, f" Line {i}: '{linea}' != '{lineb}'"

if __name__ == '__main__':
    for filename in SINGLE_FILES:
        test_calltree1(filename)
    print("Tree representation test: OK")
 
