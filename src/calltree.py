"""
Utilities to get a call tree (from the output of ``cube_dump -w``).

A call tree is represented as a tree of 
``(function_name,cnode_id,parent,[list of children])``
named tuples (of class ``CubeTreeNode``)
"""
import logging
from tree_parsing import collect_hierarchy,level_fun
from box import Box
import pandas as pd
import re
from cube_file_utils import get_lines, get_cube_dump_w_text


class CubeTreeNode(Box):
    """
    Holds attributes of a tree node read from cube commands such as cube dump.

    For a node of the cube call tree, the following attributes are available:

    .. py:attribute:: fname

       The name of the function;

    .. py:attribute:: cnode_id

       The unique ID related to the node in the call tree, read from id=value in string;

    .. py:attribute:: parent

       A binding to the parent node (can be ``None``);

    .. py:attribute:: children

       A list of bindings to child nodes.

    And others from cube_dump output.
    """

    def __repr__(root):
        """ An implementation for '__repr__'.

        Prints only the beginning and the end of the call tree.
        """
        lines = calltree_to_string(root).split("\n")
        res = lines[:5] + ["..."] + lines[-6:]
        l = max(len(line) for line in res)
        res = ["", "=" * l] + res + ["=" * l, ""]
        return "\n".join(res)

    def __init__(self,*args,**kwargs):
        if 'frozen_box' in kwargs:
            del kwargs['frozen_box']
        super().__init__(*args, frozen_box = True, **kwargs)


def iterate_on_call_tree(root, maxlevel=None):
    """Iterator on a tree (Generator).
    Can be used for searching in the tree, depth-first.

    Parameters
    ----------
    root: CubeTreeNode
        a CubeTreeNode representing the root of the tree;
    maxlevel : int or None
        the maximum depth of the recursion (``None`` means unlimited).

    Returns
    -------
    res : CubeTreeNode
        Iterator yielding ``CubeTreeNode`` s.
        
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
    call_tree : CubeTreeNode
        Recursive representation of a call tree
    full_path : bool
        Whether or not the full path needs to be in the output as a column

    Returns
    -------
    df : DataFrame
        A dataframe with "Function Name", "Cnode ID", "Parent Cnode ID", 
        "Level" and optionally "Full Callpath" as columns.

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

    # Adding info on levels
    levels = (get_level(df.set_index('Cnode ID')['Parent Cnode ID']) #
               .rename('Level') #
               .reset_index()) #
    df = pd.merge(df,levels,left_on = 'Cnode ID', right_on = 'Cnode ID')

    return df

def get_level(parent_series):
    '''
    This function computes the levels starting from the parent information.

    Parameters
    ----------
    parent_series : pandas.Dataframe or pandas.Series
        Either a DataFrame containing two columns - the CNode IDs of the parent
        and the Cnode IDs of the child, or a series containing the Cnode ID 
        of the parent indexed by the Cnode ID of the child.
    Returns
    -------
    levels : pandas.Series
        A series containing the levels of each node, indexed by Cnode ID
    '''
    if type(parent_series) == pd.DataFrame:
        parent_series = parent_series.set_index('Cnode ID')['Parent Cnode ID']
        print('Index changed')

    def get_single_level(idx):
        if idx == 0:
            return 0
        else:
            return 1 + get_single_level(parent_series[idx])

    levels = [ get_single_level(idx) for idx in parent_series.index ]

    return pd.Series(index = parent_series.index, data = levels)


def calltree_to_string(root, max_len=60, maxlevel=None, payload=None, full = True):
    """ For an understandable, ascii art representation of the call tree.

    Parameters
    ----------
    root : CubeTreeNode
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
    return _calltree_to_string(root, "", max_len, maxlevel, payload, full)


def _calltree_to_string(root, line_prefix="", max_len=60, maxlevel=None, payload=None, full = True):
    fname = root.fname_full if full else root.fname
    res = line_prefix + f"-{fname}:"
    to_print = str(root.cnode_id if payload is None else payload[root.cnode_id])
    res += " " * (max_len - len(res) - len(to_print))
    res += to_print + "\n"
    new_maxlevel = maxlevel - 1 if maxlevel is not None else None
    if len(root.children) != 0 and (maxlevel is None or maxlevel > 0):
        for child in root.children[:-1]:
            res += _calltree_to_string(
                child, line_prefix + "  |", max_len, new_maxlevel, payload, full
            )
        res += _calltree_to_string(
            root.children[-1], line_prefix + "   ", max_len, new_maxlevel, payload, full
        )
    return res


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

def create_node_cpp_template(line):
    """
    Parse a line in the call tree graph output by 'cube_dump -w'
    returning any attributes found, as well as attributes `parent` and `level`.

    INPUT:
          |-void Eigen::internal::call_dense_assignment_loop(const DstXprType&, const SrcXprType&, const Functor&) [with DstXprType = Eigen::Matrix<double, -1, -1, 1>; SrcXprType = Eigen::Matrix<double, -1, -1>; Functor = Eigen::internal::assign_op<double>]  [ ( id=257,   mod=), 632, 646, paradigm=compiler, role=function, url=, descr=, mode=/lustrehome/home/s.engkadac/mylibs/eigen-devel/Eigen/src/Core/AssignEvaluator.h]
    OUTPUT:
       fname = "Eigen::internal::call_dense_assignment_loop", 
       fname_full = "void Eigen::internal::call_dense_assignment_loop(const DstXprType&, const SrcXprType&, const Functor&)"
       template_subs = {'DstXprType': 'Eigen::Matrix<double, -1, -1, 1>',
                        'SrcXprType': 'Eigen::Matrix<double, -1, -1>',
                        'Functor': 'Eigen::internal::assign_op<double>'}
       cnode_id = 257
       ...
    """
    # finding the function name
    groups = re.search(r"(\|-)?([^[\|]*)\[with (.+)\]\s+\[(.*)\]",line).groups()
    fname = groups[1]
    template_args = groups[2]
    info = groups[3]

    # delete brackets
    info = re.sub(r"\(|\)", "", info).strip()

    # template substitutions 
    template_subs = dict([ (a.strip(), b.strip()) for a,b in [ s.split('=') for s in groups[2].split(';')]])

    # split entries into lists of key/value pairs
    entry_pairs = filter(
        lambda x: len(x) == 2, [entry.split("=") for entry in info.split(",")]
    )

    # extract attributes from entry pairs
    attrs = {key.strip(): value.strip() for key, value in entry_pairs}

    # set fname as function name
    fname_full = fname.strip()
    if '(' in fname:
        fname = fname[:fname.find('(')]
        fname = fname.split()[-1]

    attrs['fname'] = fname
    attrs['fname_full'] = fname_full

    # template substitutions
    attrs['template_subs'] = template_subs

    # rename id attr to cnode_id, if it exists
    if "id" in attrs:
        attrs['cnode_id'] = int(attrs["id"])
        del attrs["id"]

    # Ensure that each node has a parent attribute (None by default)
    attrs['parent'] = None
    attrs['children'] = []

    return CubeTreeNode(attrs)


def create_node_cpp(line):
    """
    Parse a line in the call tree graph output by 'cube_dump -w'
    returning any attributes found, as well as attributes `parent` and `level`.

    INPUT:
          |-virtual SolverPetsc::~SolverPetsc()  [ ( id=302,   mod=), 13, 20, paradigm=compiler, role=function, url=, descr=, mode=/lustrehome/home/s.engkadac/cfdsfemmpi/src/base/SolverPetsc.cpp]
    OUTPUT:
          CubeTreeNode with the attributes read from key=value pairs in input string. In this case: 
          fname="SolverPetsc::~SolverPetsc()", id=302, mod='', paradigm='mpi' etc
    """
    # finding the function name
    groups = re.search(r"(\|-)?([^[\|]*)\s+\[(.*)\]",line).groups()
    fname = groups[1]
    info = groups[2]

    # delete brackets
    info = re.sub(r"\(|\)", "", info).strip()

    # split entries into lists of key/value pairs
    entry_pairs = filter(
        lambda x: len(x) == 2, [entry.split("=") for entry in info.split(",")]
    )

    # extract attributes from entry pairs
    attrs = {key.strip(): value.strip() for key, value in entry_pairs}

    # set fname as function name
    fname_full = fname.strip()
    if '(' in fname_full:
        fname = fname_full[:fname_full.find('(')]
        fname = fname.replace(', ',',')
        fname = fname.split()[-1]

    attrs['fname'] = fname
    attrs['fname_full'] = fname_full

    # rename id attr to cnode_id, if it exists
    if "id" in attrs:
        attrs['cnode_id'] = int(attrs["id"])
        del attrs["id"]

    # Ensure that each node has a parent attribute (None by default)
    attrs['parent'] = None
    attrs['children'] = []

    return CubeTreeNode(attrs)


def create_node_simple(line):
    """
    Parse a line in the call tree graph output by 'cube_dump -w'
    returning any attributes found, as well as attributes `parent` and `level`.

    INPUT:
    '    |-MPI_Finalize  [ ( id=163,   mod=), -1, -1, paradigm=mpi, role=function, url=, descr=, mode=MPI]'
    OUTPUT:
    CubeTreeNode with the attributes read from key=value pairs in input string. In this case: fname="MPI_Finalize", id=163, mod='', paradigm='mpi' etc
    """

    # Find the info string between square brackets
    groups = re.search(r"(\|-)?(\S+)\s+\[(.*)\]",line).groups()
    fname = groups[1]
    info = groups[2]

    # delete brackets
    info = re.sub(r"\(|\)", "", info).strip()

    # split entries into lists of key/value pairs
    entry_pairs = filter(
        lambda x: len(x) == 2, [entry.split("=") for entry in info.split(",")]
    )

    # extract attributes from entry pairs
    attrs = {key.strip(): value.strip() for key, value in entry_pairs}

    # set fname as function name
    attrs['fname'] = fname 
    attrs['fname_full'] = fname

    # rename id attr to cnode_id, if it exists
    if "id" in attrs:
        attrs['cnode_id'] = int(attrs["id"])
        del attrs["id"]

    # Ensure that each node has a parent attribute (None by default)
    attrs['parent'] = None
    attrs['children'] = []

    return CubeTreeNode(attrs)

def create_node(line):
    def matches_addr_range(string):
        return re.search(r"\[0x[0-9a-f]+,0x[0-9a-f]+\)",string)

    for  create_node_fun in [create_node_simple, create_node_cpp, create_node_cpp_template]:
        node = create_node_fun(line)
        match_addr_range = matches_addr_range(node.fname)
        if match_addr_range:
            strtocheck = node.fname[:match_addr_range.span()[0]] + \
                    node.fname[match_addr_range.span()[1]:]
        else :
            strtocheck = node.fname
        brackets_in_fname = any( b in strtocheck for b in [')','('])
        if brackets_in_fname:
            print(node.fname)
        if 'cnode_id' in node.keys() and not brackets_in_fname:
            return node

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
    def assemble_function(root, children):

        def deorphan_and_freeze(child):
            res = dict(child)
            res['parent'] = root
            return CubeTreeNode(res)

        children = [ deorphan_and_freeze(child) for child in children ]
        root = dict(root) 
        root['children'] = children

        return CubeTreeNode(root)

    return collect_hierarchy(input_lines, level_fun, create_node, assemble_function)


def get_call_tree(profile_file):
    """
    Typical use case, gets all the information regarding the calltree

    Parameters
    ==========
    profile_file : str
        Name of the ``.cubex`` file

    Returns
    =======
    calltree : CubeTreeNode
        A recursive representation of the call tree.
    """
    # "call tree" object

    cube_dump_w_text = get_cube_dump_w_text(profile_file)
    call_tree_lines = get_call_tree_lines(cube_dump_w_text)
    calltree = calltree_from_lines(call_tree_lines)

    return calltree
