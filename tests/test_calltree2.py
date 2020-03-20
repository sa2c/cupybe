#!/usr/bin/env python3.8
'''
This script runs only a convenient function that returns all the info in 
a pandas dataframe.
'''

if __name__ == '__main__':
    from sys import argv
    from calltree import get_all_info

    all_repr = get_all_info(argv[1])

    print("Dataframe representation of calltree:")
    print(all_repr['df'])

