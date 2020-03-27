#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../src

function run_test(){
    ($@ &> $1.output || (echo "$1 failed." ; exit 1)) && echo "$1 ok."
}

run_test ./test_calltree1.py profile.cubex && \
run_test ./test_calltree2.py profile.cubex && \
run_test ./test_process_multi.py scalasca_output && \
run_test ./test_convert_df_to_inclusive.py profile.cubex && \
run_test ./test_convert_df_to_inclusive_multi.py scalasca_output/*/profile.cubex && \
run_test ./test_convert_index.py scalasca_output/*/profile.cubex && \
run_test ./test_tree_parsing.py profile.cubex && \
echo "Testing build of docs" && \
cd ../docs && make html
