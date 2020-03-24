"""
Utilities to merge the information that comes from multiple '.cubex' files
"""
import calltree as ct
import cube_file_utils as cfu
import metrics as mt
import logging


def process_cubex(profile_file, exclusive = True):
    '''
    Processes a single ``.cubex`` file, returning a number of 

    Parameters
    ----------
    profile_file : str
        The name of the ``.cubex`` file.
    exclusive : bool
        Whether to ask ``cube_dump`` for exclusive (True) or inclusive (False) 
        metrics.

    Returns
    -------
    calltree : calltree.CallTreeNode
        A call tree recursive object
    calltree_df : pandas.DataFrame
        A DataFrame representation of the call tree object
    df : pandas.DataFrame
        A dataframe containing the profiling data, from 
    conv_info : list
        convertibility information (to inclusive) for the metrics contained
        in the dump.

    '''
    import pandas as pd
    # Getting all callgraph information
    logging.debug(f"Reading {profile_file}...")
    call_tree = ct.get_call_tree(profile_file)
    call_tree_df = ct.calltree_to_df(call_tree,full_path = True)
    dump_df = cfu.get_dump(profile_file, exclusive)

    conv_info = mt.get_inclusive_convertible_metrics(profile_file)

    return {'calltree': call_tree, 
            'calltree_df': call_tree_df, 
            'df': dump_df,
            'conv_info': conv_info}


def check_column_sets(column_sets):
    ''' 
    Checking that any pair of column sets shares only
    the columns that are common to all sets.
    '''
    common_cols = set.intersection(*column_sets)
    noncommon_columns_df = [
        column_set.difference(common_cols) for column_set in column_sets
    ]

    from itertools import combinations
    for nccs1, nccs2 in combinations(noncommon_columns_df, 2):
        assert len(nccs1.intersection(nccs2)) == 0, f"{nccs1}, {nccs2}"
    logging.debug("Column sets are ok.")


def process_multi(profile_files, exclusive = True):
    ''' Processes ``.cubex`` files coming from different profiling runs, e.g.
    from a ``scalasca -analyze`` run.
   
    Assumes that there is a set of metrics which are common to all files,
    and that no pair of files share metrics that are not shared by all the 
    others.

    Parameters
    ----------
    profile_file : list
        List of ``.cubex`` filenames.
    exclusive : bool
        Whether to ask ``cube_dump`` for exclusive (True) or inclusive (False) 
        metrics.

    Returns
    -------
    tree : calltree.CallTreeNode
        A call tree recursive structure.
    tree_df : pandas.DataFrame
        DataFrame representation of the call tree.
    common : pandas.DataFrame
        A data frame containing all the data relative to metrics that are 
        shared among *all* the ``.cubex`` files.
    noncommon : pandas.DataFrame
        A data frame containing all the data relatige that are specific to 
        single ``.cubex`` files.
    conv_info : list
        A list of metrics that can be converted to inclusive.

    '''
    import pandas as pd
    # Assuming that the calltree info is equal for all
    # .cubex files, up to isomorphism.
    first_file_info = process_cubex(profile_files[0], exclusive)
    call_tree = first_file_info['calltree']
    call_tree_df = first_file_info['calltree_df']

    logging.debug(f"Reading {len(profile_files)} files...")
    outputs = [ process_cubex(pf, exclusive) for pf in profile_files]
    dfs = [ output['df'].set_index(['Cnode ID','Thread ID']) for output in outputs ] 
    conv_infos = [ output['conv_info'] for output in outputs ] 

    conv_info = set.union(*conv_infos)

    # finding columns common to all DFs and creating
    # a dataframe for those
    columns_df = [set(df.columns) for df in dfs]

    check_column_sets(columns_df)

    common_cols = set.intersection(*columns_df)

    dfs_common = [df.loc[:, common_cols] for df in dfs]

    for i, df in enumerate(dfs_common):
        df.columns = pd.MultiIndex.from_tuples([(i, col)
                                                 for col in common_cols],
                                                names=['run', 'metric'])

    df_common = pd.concat(dfs_common, axis='columns', join='inner')

    # finding columns specific to each DFs and creating a
    # dataframe for those

    noncommon_columns_df = [
        columns.difference(common_cols) for columns in columns_df
    ]

    dfs_noncommon = [
        df.loc[:, noncommon_columns]
        for df, noncommon_columns in zip(dfs, noncommon_columns_df)
    ]

    df_noncommon = (pd.concat(dfs_noncommon, axis='columns', join='inner')
            .rename_axis(mapper = ['metric'], axis = 'columns'))
    

    return {'tree'      : call_tree,
            'tree_df'   : call_tree_df,
            'common'    : df_common, 
            'noncommon' : df_noncommon,
            'conv_info' : conv_info}


def cnode_id_to_path(df,tree_df, full_path = True):
    '''
    Converts the ``Cnode ID`` in the index of a DataFrame to paths. 

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame where the conversion needs to happen
    tree_df: pandas.DataFrame
        DataFram representation of the call tree, which contains the 
        information for the translation.
    full_path : bool
        Whether or not to replace the ``Cnode ID`` with a full call path 
        (``True``) or with the plain function name.
        
    '''

    cnames = df.columns.names 
    inames = df.index.names 

    assert None not in cnames, "workaround not implemented"
    assert None not in inames, "workaround not implemented"

    needed_tree_cols  = ['Cnode ID', 'Full Callpath' if full_path else 'Function Name']

    needed_tree_data  = tree_df[needed_tree_cols]


    import pandas as pd 
    return ( pd.merge(
        df.stack(cnames).reset_index(),
        needed_tree_data,
        on = 'Cnode ID')
        .drop('Cnode ID', axis = 'columns')
        .stack(cnames)) # TODO: Run & Test

