#!/usr/bin/env python3.8
'''
Just a test to see that everything runs correctly.
'''
import glob
from merger import *
from sys import argv
import logging
files = glob.glob(f'{argv[1]}/*/profile.cubex')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
print("Processing single dump")
res = process_cubex(files[0])
print("Calltree:")
print(res['calltree'])
print("Metrics:")
print(res['df'])

print("Processing multiple dump")

output  = process_multi(files)
print("Common metrics to all the profile files:")
print(output['common'])
print("Metrics specific to single profile files:")
print(output['noncommon'])


