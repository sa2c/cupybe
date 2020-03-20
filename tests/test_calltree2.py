#!/usr/bin/env python3.8
'''
This script runs only a convenient function that returns all the info in 
a pandas dataframe.
'''

if __name__ == '__main__':
    from sys import argv
    from calltree import get_call_tree_df

    df = get_call_tree_df(argv[1])

    print("Dataframe representation of calltree:")
    print(df)

