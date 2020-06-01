#!/bin/bash

# Make sure cube_dump is visible
which cube_dump || echo "cube_dump not accessible!" && exit 1

export PYTHONPATH=$PYTHONPATH:../src

export FAILED=.failed.tests
touch $FAILED

function run_test(){
    ($@ &> $1.output || (echo "$1 failed." | tee -a $FAILED ; exit 1)) && echo "$1 ok."
}
SINGLE_FILE=../test_data/profile.cubex
SINGLE_FILE_SAMPLING=../test_data/profile.wsampling.cubex
SCALASCA_OUTPUT=../test_data/scalasca_output

for file in ./test_*.py
do 
    if ! grep $file ./runtests.sh &> /dev/null
    then
        echo "WARNING: $file will not be run!"
    fi
done

run_test ./test_calltree1.py $SINGLE_FILE 
run_test ./test_calltree2.py $SINGLE_FILE 
run_test ./test_process_multi.py $SCALASCA_OUTPUT 
run_test ./test_convert_df_to_inclusive.py $SINGLE_FILE
run_test ./test_convert_df_to_inclusive_multi.py $SCALASCA_OUTPUT/*/profile.cubex 
run_test ./test_convert_index.py $SCALASCA_OUTPUT/*/profile.cubex 
run_test ./test_tree_parsing.py $SINGLE_FILE
run_test ./test_get_level.py $SINGLE_FILE

ln -s ./test_calltree1.py ./test_calltree1.sampling.py
ln -s ./test_calltree2.py ./test_calltree2.sampling.py
ln -s ./test_convert_df_to_inclusive.py ./test_convert_df_to_inclusive.sampling.py
ln -s ./test_tree_parsing.py ./test_tree_parsing.sampling.py
ln -s ./test_get_level.py ./test_get_level.sampling.py

echo "Running tests on cubex files obtained with sampling..."

run_test ./test_calltree1.sampling.py $SINGLE_FILE 
run_test ./test_calltree2.sampling.py $SINGLE_FILE 
run_test ./test_convert_df_to_inclusive.sampling.py $SINGLE_FILE
run_test ./test_tree_parsing.sampling.py $SINGLE_FILE
run_test ./test_get_level.sampling.py $SINGLE_FILE

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

rm -r ./test_calltree1.sampling.py 
rm -r ./test_calltree2.sampling.py 
rm -r ./test_convert_df_to_inclusive.sampling.py 
rm -r ./test_tree_parsing.sampling.py 
rm -r ./test_get_level.sampling.py 




