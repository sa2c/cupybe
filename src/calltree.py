"""
Get a call tree from a .cubex file.
A call tree is represented as a tree of 
(function_name,cnode_id,[list_of_children])
named tuples.
"""
import logging
from collections import namedtuple

CallTreeNode = namedtuple('CallTreeNode',
                          ['fname', 'cnode_id', 'parent', 'children'])
CallTreeNode.__repr__ = lambda x : calltree_to_repr(x)

CallTreeLine = namedtuple('CallTreeLine', ['fname', 'cnode_id', 'level'])


def iterate_on_call_tree(root):
    yield root
    for child in root.children:
        yield from iterate_on_call_tree(child)


def calltree_to_df(call_tree):
    import pandas as pd
    tuples = [(n.fname, n.cnode_id,
               n.parent.cnode_id if n.parent is not None else pd.NA)
              for n in iterate_on_call_tree(call_tree)]

    df = pd.DataFrame(
        data=tuples, columns=['Function Name', 'Cnode ID', 'Parent Cnode ID'])
    return df


def calltree_to_string(root, line_prefix='', max_len=60):
    ''' 
    For an understandable representation of the call tree.
    '''
    res = line_prefix + f"-{root.fname}:"
    res += ' ' * (max_len - len(res))
    res += f"{root.cnode_id}\n"
    if len(root.children) != 0:
        for child in root.children[:-1]:
            res += calltree_to_string(child, line_prefix + '  |', max_len)
        res += calltree_to_string(root.children[-1], line_prefix + '   ',
                                  max_len)
    return res


def calltree_to_repr(root):
    '''
    An implementation for '__repr__'
    '''
    lines = calltree_to_string(root).split('\n')
    res = lines[:5] + ['...'] + lines[-6:]
    l = max(len(line) for line in res)
    res = ['','='*l] + res + ['='*l,''] 
    return '\n'.join(res)


def get_max_len(root):
    '''
    For nicer printing. Not very precise.
    '''
    return len(root.fname) + 1 + max(
        len(child.fname) for child in root.children)


def get_fpath_vs_id(root, parent_full_callpath=''):
    import pandas as pd
    full_callpath = parent_full_callpath + root.fname
    data = [(root.cnode_id, full_callpath)]
    for child in root.children:
        data += get_fpath_vs_id(child, full_callpath + '/')
    return data


def parse_line(line):
    '''                             
    INPUT:
    '    |-MPI_Finalize  [ ( id=163,   mod=), -1, -1, paradigm=mpi, role=function, url=, descr=, mode=MPI]'
    OUTPUT:
    ('MPI_Finalize',163,2)
    '''
    import re
    splitpoint = line.find('[')
    fun_name = re.search('(\w+)\s+$', line[:splitpoint]).groups()[0]
    cnode_id = re.search('id=([0-9]+)', line[splitpoint:]).groups()[0]

    # The following assumes that cube_dump uses 2 spaces for each level
    # This might change!
    splitpoint = re.search('\w', line).span()[0]
    level = line[:splitpoint].count(' ') / 2
    assert level == int(level), "Error in determining level"
    return CallTreeLine(fun_name, int(cnode_id), int(level))


def get_call_tree_lines(cube_dump_w_text):
    lines = cube_dump_w_text.split('\n')
    call_tree_start_line_idx = next(
        i for i, l in enumerate(lines) if 'CALL TREE' in l)
    call_tree_stop_line_idx = next(
        i for i, l in enumerate(lines) if 'SYSTEM DIMENSION' in l)
    call_tree_lines = [
        l for l in lines[call_tree_start_line_idx + 1:call_tree_stop_line_idx]
        if len(l.strip()) != 0
    ]
    logging.debug(f"No of lines: {len(call_tree_lines)}\n")
    return call_tree_lines


def calltree_from_lines(call_tree_lines):
    """
    Get a call tree from the output of the command 

    cube_dump -w <cubex_file>

    It is assumed that the tree is printed in a depth-first order.
    """

    parsed_lines = [parse_line(line) for line in call_tree_lines]
    logging.debug(f"No of functions found: {len(parsed_lines)}\n")
    root = parsed_lines[0]
    assert root.level == 0, f"First node is not root (level={root.level}), not depth first order?"
    res = CallTreeNode(root.fname, root.cnode_id, None, [])
    last_parent = res

    def add_children(node, level, remaining_lines):
        while len(remaining_lines) > 0 and remaining_lines[0].level > level:
            new_line = remaining_lines[0]
            remaining_lines = remaining_lines[1:]
            new_node = CallTreeNode(new_line.fname, new_line.cnode_id, node,
                                    [])
            remaining_lines = add_children(new_node, new_line.level,
                                           remaining_lines)
            node.children.append(new_node)
        return remaining_lines

    add_children(res, 0, parsed_lines[1:])

    return res


def get_cube_dump_w_text(profile_file):
    import subprocess
    cube_dump_process = subprocess.run(['cube_dump', '-w', profile_file],
                                       capture_output=True,
                                       text=True)
    return cube_dump_process.stdout


def calltree_to_df2(calltree):
    """
    Returns a df with 4 columns:
    - full callpath
    - function name
    - cnode id
    - parent cnode id
    """
    # full callpath vs cnode id for convenience
    import pandas as pd
    data = get_fpath_vs_id(calltree)
    fullpath_vs_id = pd.DataFrame(data, columns=['Cnode ID', 'Full Callpath'])

    # function name, cnode_id, parent_cnode_id
    fname_id_parentid = calltree_to_df(calltree)

    df_repr = fullpath_vs_id.merge(
        right=fname_id_parentid, how='inner', on='Cnode ID')

    return df_repr

def get_call_tree_df(profile_file):
    """
    Typical use case, gets all the information regarding the calltree
    """
    # "call tree" object
    cube_dump_w_text = get_cube_dump_w_text(profile_file)
    call_tree_lines = get_call_tree_lines(cube_dump_w_text)
    calltree = calltree_from_lines(call_tree_lines)


    return calltree_to_df2(calltree)
