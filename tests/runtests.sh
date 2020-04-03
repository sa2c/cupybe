#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../src

export FAILED=.failed.tests
touch $FAILED

function run_test(){
    ($@ &> $1.output || (echo "$1 failed." | tee -a $FAILED ; exit 1)) && echo "$1 ok."
}
SINGLE_FILE=../test_data/profile.cubex
SCALASCA_OUTPUT=../test_data/scalasca_output

run_test ./test_calltree1.py $SINGLE_FILE 
run_test ./test_calltree2.py $SINGLE_FILE 
run_test ./test_process_multi.py $SCALASCA_OUTPUT 
run_test ./test_convert_df_to_inclusive.py $SINGLE_FILE
run_test ./test_convert_df_to_inclusive_multi.py $SCALASCA_OUTPUT/*/profile.cubex 
run_test ./test_convert_index.py $SCALASCA_OUTPUT/*/profile.cubex 
run_test ./test_tree_parsing.py $SINGLE_FILE
run_test ./test_get_level.py $SINGLE_FILE
(echo "Testing build of docs" && cd ../docs && make html ) 
(echo "Running examples" && cd ../examples 
run_test ./example1.py 
run_test ./example2.py )

echo "Failed Tests:"
if [ $(cat $FAILED | wc -l) -eq 0 ]
then 
    echo "None"
else
    cat $FAILED 
fi
rm -f $FAILED 



