#!/usr/bin/env python3
import merger as mg
import index_conversions as ic
from sys import argv
import test_utils as tu
from glob import glob


def test_convert_index():
    input_files = glob(f"{tu.SCALASCA_OUTPUT}/*/profile.cubex")
    
    output = mg.process_multi(input_files)
    
    common = output.common
    assert common.index.names == ['Cnode ID', 'Thread ID']
    assert common.columns.names == ['run', 'metric']
    
    noncommon = output.noncommon
    assert noncommon.index.names == ['Cnode ID', 'Thread ID']
    assert noncommon.columns.names == ['metric']
    
    tree_df = output.ctree_df
    
    # Checkin all conversions in cicrle
    
    for target in ['Full Callpath',   # one way...
                   'Short Callpath',
                   'Cnode ID',
                   'Short Callpath',  # .. and back.
                   'Full Callpath',
                   'Cnode ID' ]:
    
        print(f"Target : {target}")
        # Common metrics
        common = ic.convert_index(common,tree_df,target)
        print(common.index.names   )
        print(common.columns.names )
        
        assert common.index.names == [target, 'Thread ID']
        assert common.columns.names == ['run', 'metric']
        
        print("Column names are as expected for the 'common' dataframe.")
        
        # Non common metrics 
        
        noncommon = ic.convert_index(noncommon,tree_df,target)
        print(noncommon.index.names  )    
        print(noncommon.columns.names)
        
        assert noncommon.index.names == [target, 'Thread ID']
        assert noncommon.columns.names == ['metric']
        
        print("Column names are as expected for the 'non-common' dataframe.")

if __name__ == "__main__":
    test_convert_index()

