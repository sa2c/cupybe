'''
General utilities for parsing a list of lines into a hierarchical structure.
'''


def level_fun(line):
    import re
    splitpoint = re.search('\w', line).span()[0]
    return int(line[:splitpoint].count(' ') / 2)



def collect_hierarchy(
    lines,
    level_fun,
    read_fun=lambda line: line,
    assemble_fun=lambda root, children: (root, children),
):
    """
    Reorders a list of lines that can be mapped to a level via ``level_fun``
    into a hierarchical structure of the kind

    .. code-block:: python3

        (root_line,
             [(child_line,
                  [(grandchild_line,
                      [...])]),
              (sibling_line,
                  [...]),
              ...])
    
    The lines can be parsed/transformed with ``read_fun``, and the nodes can be
    transformed with ``assemble_fun``.

    A line's parent is the last previous line which satisfes the relation
    ``level_fun(parent_line) == level_fun(line) - 1``.

    Recursive function.

    Parameters
    ----------
    lines : list of str
        The lines to be inserted in a tree;
    level_fun : callable(string) -> int
        A function that computes the level for each line.
    read_fun : callable(string) -> ParsedObject
        A function to parse the line. Default: identity function.
    assemble_fun : callable(ParsedObject, list of AssembledObject) -> AssembledObjects
        A function that is used to assemble the result. Default: 
        ``lambda root,children : (root,children)``.

    Returns
    -------
    assembled : AssembledObject
        The result

    '''

    root = read_fun(lines[0])  # There always is at least an element
    level = level_fun(root) + 1

    # Starts of all the groups
    starts = [i for i, line in enumerate(lines) if level_fun(line) == level]
    # Ends of all the groups
    ends = starts[1:] + [len(lines)]

    children = [
        collect_hierarchy(lines[s:e], level_fun, read_fun)
        for s, e in zip(starts, ends)
        if s < e
    ]

    return assemble_fun(root, children)


# FOR TESTING


def iterate(node):
    root, children = node
    yield root
    for child in children:
        yield from iterate(child)
