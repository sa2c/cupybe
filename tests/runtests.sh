#!/bin/bash

# Make sure cube_dump is visible
which cube_dump &> /dev/null || (echo "cube_dump not accessible!" && exit 1) || exit 1

export PYTHONPATH=$PYTHONPATH:../src

pytest -v


export FAILED=.failed.tests
touch $FAILED

function run_test(){
    ($@ &> $1.output || (echo "$1 failed." | tee -a $FAILED ; exit 1)) && echo "$1 ok."
}
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





