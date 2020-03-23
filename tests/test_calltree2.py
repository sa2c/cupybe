#!/usr/bin/env python3.8
'''
This script runs only a convenient function that returns all the info in 
a pandas dataframe.
'''

if __name__ == '__main__':
    from sys import argv
    from calltree import get_call_tree, calltree_to_df2
    from cube_file_utils import get_cube_dump_w_text

    call_tree = get_call_tree(argv[1])
    call_tree_df = calltree_to_df2(call_tree)

    print("Calltree:")
    print(call_tree)
    print("Dataframe representation of calltree:")
    print(call_tree_df)

