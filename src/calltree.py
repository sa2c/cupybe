"""
Utilities to get a call tree (from the output of ``cube_dump -w``).

A call tree is represented as a tree of 
``(function_name,cnode_id,parent,[list of children])``
named tuples (of class ``CallTreeNode``)
"""
import logging
from collections import namedtuple

# Only members that are currently used.
CallTreeNode = namedtuple('CallTreeNode',
                          ['fname', 'cnode_id', 'parent', 'children'])
'''A node of the call tree.

.. py:attribute:: fname
  
   The name of the function;

.. py:attribute:: cnode_id
   
   The unique ID related to the node in the call tree;

.. py:attribute:: parent
   
   A binding to the parent node (can be ``None``);

.. py:attribute:: children
   
   A list of bindings to child nodes.

'''
CallTreeNode.__repr__ = lambda x: calltree_to_repr(x)

# Only members that are currently used.
CallTreeLine = namedtuple('CallTreeLine', ['fname', 'cnode_id', 'level'])

def iterate_on_call_tree(root,maxlevel = None):
    '''Iterator on a tree (Generator).
    Can be used for searching in the tree, depth-first.

    Parameters
    ----------
    root: CallTreeNode
        a CallTreeNode representing the root of the tree;
    maxlevel : int or None
        the maximum depth of the recursion (``None`` means unlimited).

    Returns
    -------
    res : CallTreeNode
        Iterator yielding ``CallTreeNode``\s.
        
    '''
    yield root
    new_maxlevel = maxlevel - 1 if maxlevel is not None else None
    if len(root.children) != 0 and (maxlevel is None or maxlevel > 0):
        for child in root.children :
            yield from iterate_on_call_tree(child, new_maxlevel)


def calltree_to_df(call_tree, full_path = False):
    '''Convert a call tree into a DataFrame.

    Parameters
    ----------
    call_tree : CallTreeNode
        Recursive representation of a call tree
    full_path : bool
        Whether or not the full path needs to be in the output as a column

    Returns
    -------
    df : DataFrame
        A dataframe with "Function Name", "Cnode ID", "Parent Cnode ID" and 
        optionally "Full Callpath" as columns.

    '''
    import pandas as pd
    tuples = [(n.fname, n.cnode_id,
               n.parent.cnode_id if n.parent is not None else pd.NA)
              for n in iterate_on_call_tree(call_tree)]

    df = pd.DataFrame(data=tuples,
                      columns=['Function Name', 'Cnode ID', 'Parent Cnode ID'])

    if full_path:
        # full callpath vs cnode id for convenience
        data = get_fpath_vs_id(call_tree)
        fullpath_vs_id = pd.DataFrame(data, columns=['Cnode ID', 'Full Callpath'])

        # function name, cnode_id, parent_cnode_id

        df = fullpath_vs_id.merge(right=df, how='inner', on='Cnode ID')

    return df


def calltree_to_string(root, max_len=60, maxlevel = None,payload = None):
    ''' For an understandable, ascii art representation of the call tree.
    Recursive function.

    Parameters
    ----------
    root : CallTreeNode
        The root of the tree;
    max_len : int
        Desired length of the printed line;
    maxlevel : int, None
        Maximum depth of the printed tree. If ``None``, no limit;
    payload : indexable
        Something that can be indexed by ``Cnode ID``, e.g. an ordered Series.

    Returns
    -------
    res : string
        string representation of the call tree and the payload.
    '''
    return _calltree_to_string(root,'',max_len,maxlevel, payload)


def _calltree_to_string(root, line_prefix='', max_len=60, maxlevel = None,payload = None):
    res = line_prefix + f"-{root.fname}:"
    to_print = str(root.cnode_id if payload is None else payload[root.cnode_id])
    res += ' ' * (max_len - len(res) - len(to_print))
    res += to_print + '\n'
    new_maxlevel = maxlevel - 1 if maxlevel is not None else None
    if len(root.children) != 0 and (maxlevel is None or maxlevel > 0):
        for child in root.children[:-1]:
            res += _calltree_to_string(child, line_prefix + '  |',
                                      max_len, new_maxlevel, payload)
        res += _calltree_to_string(root.children[-1], line_prefix + '   ',
                                  max_len, new_maxlevel, payload) 
    return res


def calltree_to_repr(root):
    ''' An implementation for '__repr__'. 

    Prints only the beginning and the end of the call tree.
    '''
    lines = calltree_to_string(root).split('\n')
    res = lines[:5] + ['...'] + lines[-6:]
    l = max(len(line) for line in res)
    res = ['', '=' * l] + res + ['=' * l, '']
    return '\n'.join(res)


def get_max_len(root):
    '''
    For nicer printing. Not very precise.
    '''
    return len(root.fname) + 1 + max(
        len(child.fname) for child in root.children)


def get_fpath_vs_id(root, parent_full_callpath=''):
    '''
    Returns a list of (Cnode ID, full call path) tuples.
    '''
    full_callpath = parent_full_callpath + root.fname
    data = [(root.cnode_id, full_callpath)]
    for child in root.children:
        data += get_fpath_vs_id(child, full_callpath + '/')
    return data


def parse_line(line):
    '''                             
    Parse a line in the call tree graph output by 'cube_dump -w'
    returning the name, the node id and the level.

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
    '''
    Select the lines relative to the call tree out of the
    output of 'cube_dump -w'.
    '''
    from cube_file_utils import get_lines
    return get_lines(cube_dump_w_text,start_hint = 'CALL TREE',
            end_hint = 'SYSTEM DIMENSION')


def calltree_from_lines(call_tree_lines):
    """
    Get a call tree from the relevant part of the output of the
    command 

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


def get_call_tree(profile_file):
    """
    Typical use case, gets all the information regarding the calltree

    Parameters
    ==========
    profile_file : str
        Name of the ``.cubex`` file

    Returns
    =======
    calltree : CallTreeNode
        A recursive representation of the call tree.
    """
    # "call tree" object
    from cube_file_utils import get_cube_dump_w_text
    cube_dump_w_text = get_cube_dump_w_text(profile_file)
    call_tree_lines = get_call_tree_lines(cube_dump_w_text)
    calltree = calltree_from_lines(call_tree_lines)

    return calltree

