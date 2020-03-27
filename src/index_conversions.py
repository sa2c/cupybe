"""
This module manages the conversion of indices between different formats,
e.g. ``Cnode IDs``, ``Full Callpath`` and ``Short Callpath``.

``Short Callpath`` means the name of the function followed by the ``Cnode ID``,
separated by comma.
"""
from itertools import filterfalse
import pandas as pd

possible_index_cols = ["Short Callpath", "Full Callpath", "Cnode ID"]


def find_index_col(df):
    """
    Finds the column in the index that can be transformed.
    """
    index_candidates = list(
        filterfalse(lambda x: x not in possible_index_cols, df.index.names)
    )

    assert len(index_candidates) == 1, "Not clear which index to use."
    return index_candidates[0]


def get_short_callpath(tree_df):
    # short callpath = "FunctionName,CnodeId"
    return tree_df["Function Name"].str.cat(tree_df["Cnode ID"].astype(str), sep=",")


def convert_index(df, tree_df, target=None):
    """
    Converts the the index of a DataFrame to ``Short Callpath``,
    ``Full Callpath`` or ``Cnode ID``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame where the conversion needs to happen
    tree_df: pandas.DataFrame
        DataFrame representation of the call tree, which contains the 
        information for the translation.
    target : str 
        Can be ``Short Callpath``, ``Full Callpath``, ``Cnode ID`` or ``None``.

    Returns
    -------
    res : pandas.DataFrame
        A DataFrame identical to ``df``, but with a different index.

    """
    cnames = list(df.columns.names)
    inames = list(df.index.names)

    assert None not in cnames, "workaround not implemented"
    assert None not in inames, "workaround not implemented"

    assert type(df) == pd.DataFrame
    assert type(tree_df) == pd.DataFrame or tree_df is None
    assert type(target) == str or target is None

    new_index_col = target
    possible_index_cols = ["Short Callpath", "Full Callpath", "Cnode ID"]

    old_index_col = find_index_col(df)
    if old_index_col == new_index_col:
        return df
    else:
        assert (
            tree_df is not None
        ), "tree_df needed when index does not contain Cnode ID"

    needed_tree_cols = [old_index_col, new_index_col]

    if "Short Callpath" in needed_tree_cols:
        tree_df["Short Callpath"] = get_short_callpath(tree_df)

    needed_tree_data = tree_df[needed_tree_cols]

    new_index_levels = list(inames)
    new_index_levels[inames.index(old_index_col)] = new_index_col

    return (
        pd.merge(df.stack(cnames).reset_index(), needed_tree_data, on=old_index_col)
        .drop(old_index_col, axis="columns")  # , new_index_levels, cnames)
        .set_index(new_index_levels + cnames)[0]
        .unstack(cnames)
    )
