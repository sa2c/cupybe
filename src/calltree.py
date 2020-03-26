"""
Utilities to get a call tree (from the output of ``cube_dump -w``).

A call tree is represented as a tree of 
``(function_name,cnode_id,parent,[list of children])``
named tuples (of class ``CallTreeNode``)
"""
import logging
from collections import namedtuple
import pandas as pd
import re
from cube_file_utils import get_lines, get_cube_dump_w_text

# Only members that are currently used.
CallTreeNode = namedtuple(
    "CallTreeNode", ["fname", "cnode_id", "parent", "children", "level", "attrs"]
)
"""A node of the call tree.

.. py:attribute:: fname
  
   The name of the function;

.. py:attribute:: cnode_id
   
   The unique ID related to the node in the call tree;

.. py:attribute:: parent
   
   A binding to the parent node (can be ``None``);

.. py:attribute:: children
   
   A list of bindings to child nodes.

"""


def iterate_on_call_tree(root, maxlevel=None):
    """Iterator on a tree (Generator).
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
        
    """
    yield root
    new_maxlevel = maxlevel - 1 if maxlevel is not None else None
    if len(root.children) != 0 and (maxlevel is None or maxlevel > 0):
        for child in root.children:
            yield from iterate_on_call_tree(child, new_maxlevel)


def calltree_to_df(call_tree, full_path=False):
    """Convert a call tree into a DataFrame.

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

    """

    tuples = [
        (n.fname, n.cnode_id, n.parent.cnode_id if n.parent is not None else pd.NA)
        for n in iterate_on_call_tree(call_tree)
    ]

    df = pd.DataFrame(
        data=tuples, columns=["Function Name", "Cnode ID", "Parent Cnode ID"]
    )

    if full_path:
        # full callpath vs cnode id for convenience
        data = get_fpath_vs_id(call_tree)
        fullpath_vs_id = pd.DataFrame(data, columns=["Cnode ID", "Full Callpath"])

        # function name, cnode_id, parent_cnode_id

        df = fullpath_vs_id.merge(right=df, how="inner", on="Cnode ID")

    return df


def calltree_to_string(root, max_len=60, maxlevel=None, payload=None):
    """ For an understandable, ascii art representation of the call tree.
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
    """
    return _calltree_to_string(root, "", max_len, maxlevel, payload)


def _calltree_to_string(root, line_prefix="", max_len=60, maxlevel=None, payload=None):
    res = line_prefix + f"-{root.fname}:"
    to_print = str(root.cnode_id if payload is None else payload[root.cnode_id])
    res += " " * (max_len - len(res) - len(to_print))
    res += to_print + "\n"
    new_maxlevel = maxlevel - 1 if maxlevel is not None else None
    if len(root.children) != 0 and (maxlevel is None or maxlevel > 0):
        for child in root.children[:-1]:
            res += _calltree_to_string(
                child, line_prefix + "  |", max_len, new_maxlevel, payload
            )
        res += _calltree_to_string(
            root.children[-1], line_prefix + "   ", max_len, new_maxlevel, payload
        )
    return res


def calltree_to_repr(root):
    """ An implementation for '__repr__'.

    Prints only the beginning and the end of the call tree.
    """
    lines = calltree_to_string(root).split("\n")
    res = lines[:5] + ["..."] + lines[-6:]
    l = max(len(line) for line in res)
    res = ["", "=" * l] + res + ["=" * l, ""]
    return "\n".join(res)


CallTreeNode.__repr__ = calltree_to_repr


def get_max_len(root):
    """
    For nicer printing. Not very precise.
    """
    return len(root.fname) + 1 + max(len(child.fname) for child in root.children)


def get_fpath_vs_id(root, parent_full_callpath=""):
    """
    Returns a list of (Cnode ID, full call path) tuples.
    """
    full_callpath = parent_full_callpath + root.fname
    data = [(root.cnode_id, full_callpath)]
    for child in root.children:
        data += get_fpath_vs_id(child, full_callpath + "/")
    return data


def create_node(line, parent, level):
    """
    Parse a line in the call tree graph output by 'cube_dump -w'
    returning the name, the node id and the level.

    INPUT:
    '    |-MPI_Finalize  [ ( id=163,   mod=), -1, -1, paradigm=mpi, role=function, url=, descr=, mode=MPI]'
    OUTPUT:
    ('MPI_Finalize',163,2)
    """

    splitpoint = line.find("[")
    fun_name = re.search("(\w+)\s+$", line[:splitpoint]).groups()[0]

    # find the info string between square brackets
    info = re.search("\[(.*)]", line).groups()[0]
    # remove brackets around id/mod
    info = re.sub("\(|\)", "", info).strip()

    # split entries into lists of key/value pairs
    entry_pairs = filter(
        lambda x: len(x) == 2, [entry.split("=") for entry in info.split(",")]
    )

    # strip whitespace
    attrs = {key.strip(): value.strip() for key, value in entry_pairs}

    return CallTreeNode(
        fname=fun_name,
        cnode_id=int(attrs["id"]),
        parent=parent,
        children=[],
        level=level,
        attrs=attrs,
    )


def get_call_tree_lines(cube_dump_w_text):
    """
    Select the lines relative to the call tree out of the
    output of 'cube_dump -w'.
    """
    return get_lines(
        cube_dump_w_text, start_hint="CALL TREE", end_hint="SYSTEM DIMENSION"
    )


def calltree_from_lines(input_lines):
    """
    Build the call tree structure from the output
    """

    # list of non-zero length lines
    lines = list(filter(lambda x: len(x) > 0, input_lines))

    root_node = create_node(lines.pop(0), parent=None, level=0)

    # last_node tracks the last node created
    last_node = root_node

    for line in lines[1:]:
        siblings = []

        level = line.count("|")

        if level == last_node.level:
            # ----- Sibling to last node -----
            # In this case, create a node and add it to the siblings list.
            # The parent of the last node is the parent of this node.

            last_node = create_node(line, last_node.parent, level=level)

        elif level > last_node.level:
            # ----- Child to last node -----
            # We've moved down to a child level, with the last node as a parent
            # so we need to change the `siblings` list to point to the children
            # of the last node, and pass the last node as parent to create_node

            siblings = last_node.children

            last_node = create_node(line, parent=last_node, level=level)
        else:
            # ----- Parent to last node -----
            # Since we're moving up a level compared to the previous node,
            # so `siblings` should refer to siblings of the parent.
            # We obtain this as the children of the grandparent node.
            # The parent of this new node will be the grandparent

            grandparent = last_node.parent.parent

            siblings = grandparent.children

            last_node = create_node(line, parent=grandparent, level=level)

        siblings.append(last_node)

    return root_node


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

    cube_dump_w_text = get_cube_dump_w_text(profile_file)
    call_tree_lines = get_call_tree_lines(cube_dump_w_text)
    calltree = calltree_from_lines(call_tree_lines)

    return calltree
