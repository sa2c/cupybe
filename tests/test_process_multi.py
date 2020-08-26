#!/usr/bin/env python3
'''
Just a test to see that everything runs correctly.
'''
import glob
import merger as mg
import logging
from test_utils import SCALASCA_OUTPUT

def test_process_multi():
    files = glob.glob(f'{SCALASCA_OUTPUT}/*/profile.cubex')
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    print("Processing single dump")
    res = mg.process_cubex(files[0])
    print("Calltree:")
    print(res.ctree)
    print("Metrics:")
    print(res.df)
    
    print("Processing multiple dump")
    
    output  = mg.process_multi(files)
    print("Common metrics to all the profile files:")
    print(output.common)
    print("Metrics specific to single profile files:")
    print(output.noncommon)
    

if __name__ == "__main__":
    test_process_multi()
