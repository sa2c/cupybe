#!/usr/bin/env python3
import merger as mg
from sys import argv

input_files = argv[1:]
output = mg.process_multi(input_files)

common = output['common']
assert common.index.names == ['Cnode ID', 'Thread ID']
assert common.columns.names == ['run', 'metric']

noncommon = output['noncommon']
assert noncommon.index.names == ['Cnode ID', 'Thread ID']
assert noncommon.columns.names == ['metric']

tree_df = output['tree_df']

# Common metrics

trans_common = mg.cnode_id_to_path(common,tree_df)
trans_common.index.names
trans_common.columns.names

assert trans_common.index.names == ['Full Callpath', 'Thread ID']
assert trans_common.columns.names == ['run', 'metric']

print("Column names are as expected for the 'common' dataframe.")

# Non common metrics

trans_noncommon = mg.cnode_id_to_path(noncommon,tree_df)
trans_noncommon.index.names
trans_noncommon.columns.names

assert trans_noncommon.index.names == ['Full Callpath', 'Thread ID']
assert trans_noncommon.columns.names == ['metric']


print("Column names are as expected for the 'non-common' dataframe.")
