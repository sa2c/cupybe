#!/bin/bash
export PYTHONPATH=$PYTHONPATH:../src

./test_calltree1.py profile.cubex && \
    ./test_calltree2.py profile.cubex && \
    ./test_process_multi.py scalasca_output
