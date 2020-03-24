"""
Utilities to merge the information that comes from multiple '.cubex' files
"""
import calltree as ct
import cube_file_utils as cfu
import metrics as mt
import logging


def process_cubex(profile_file, exclusive = True):
    '''
    Processes a single ``.cubex`` file.

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
        A dataframe containing the profiling data
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
    dfs = [ output['df'] for output in outputs ] 
    conv_infos = [ output['conv_info'] for output in outputs ] 

    conv_info = set.union(*conv_infos)

    dfs2 = dfs

    # finding columns common to all DFs and creating
    # a dataframe for those
    columns_df = [set(df.columns) for df in dfs2]
    common_cols = set.intersection(*columns_df)

    dfs2_common = [df.loc[:, common_cols] for df in dfs2]

    for i, df2 in enumerate(dfs2_common):
        df2.columns = pd.MultiIndex.from_tuples([(i, col)
                                                 for col in common_cols],
                                                names=['run', 'metric'])

    df_common = pd.concat(dfs2_common, axis='columns', join='inner')

    # finding columns specific to each DFs and creating a
    # dataframe for those

    noncommon_columns_df = [
        columns.difference(common_cols) for columns in columns_df
    ]

    dfs2_noncommon = [
        df.loc[:, noncommon_columns]
        for df, noncommon_columns in zip(dfs2, noncommon_columns_df)
    ]

    df_noncommon = pd.concat(dfs2_noncommon, axis='columns', join='inner')
    # Using Cnode ID in the index instead of the full callpath
    # (using the Cnode ID - full callpath relationship
    #  from the first profile file)

    tmp = call_tree_df.loc[:, ['Full Callpath', 'Cnode ID']].set_index(
        'Full Callpath')

    return {'tree'      : call_tree,
            'tree_df'   : call_tree_df,
            'common'    : df_common, 
            'noncommon' : df_noncommon,
            'conv_info' : conv_info}


def convert_series_to_inclusive(series, call_tree):
    '''
    Converts a series having Cnode IDs as index from exclusive to inclusive.
    Takes as input a CallTreeNode object (hopefully the root).

    Notice: The results may be nonsensical unless the metric acted upon is
            "INCLUSIVE convertible"

    Parameters
    ----------
    series : Series
        A series representing exclusive measurements
    call_tree : CallTreeNode
        A recursive representation of the call tree.

    Returns
    -------
    res : Series
        A series having the same structure as the input, but with data summed
        over following the hierarchy given by the call_tree object.

    '''
    # LRU cache does not work because of 
    # TypeError: unhashable type: 'list'
    #from functools import lru_cache
    #@lru_cache
    def aggregate(root):
        value = series.loc[root.cnode_id]
        for child in root.children:
             value += aggregate(child)
        return value

    import pandas as pd
    return (pd.DataFrame(
            data = [ (node.cnode_id,aggregate(node)) 
                for node in ct.iterate_on_call_tree(call_tree) ],
            columns = ['Cnode ID','metric'])
        .set_index('Cnode ID')
        .metric)


def select_metrics(df, selected_metrics):
    ''' Selects `selected_metrics` out of a DataFrame.

    This function solves some problems:

    - Finding the ``metric`` level in ``df.columns``
    - Selecting, out of ``selected_metrics`` only the ones that are also in the
      Data Frame.


    Parameters
    ----------
    df: DataFrame
        A dataframe containing the metrics to be selected as columns. 
        The dataframe columns are a `MultiIndex`
    selected_metrics: iterable
        Contains the names of the metrics that need need to be selected

    Returns
    -------
    res : DataFrame
        a DataFrame contaning only the selected metrics.
        
    '''
    # finding the level in the columns with the metrics
    metric_level = df.columns.names.index('metric')
    nlevels = len(df.columns.names)

    # choosing the metrics
    possible_metrics = set(selected_metrics).intersection(
            set(df.columns.levels[metric_level]))

    metric_indexer = [slice(None)]*nlevels
    metric_indexer[metric_level] = list(possible_metrics)

    return df.loc[:,tuple(metric_indexer)]
 

def convert_df_to_inclusive(df_convertible, call_tree):
    '''
    Converts a DataFrame having Cnode IDs as index from exclusive to inclusive.

    Parameters
    ----------
    df_convertible : DataFrame
        A DataFrame containing only metrics that can be converted safely from
        exclusive to inclusive.
    call_tree: CallTreeNode
        A recursive representation of the call tree.

    Returns
    -------
    res : DataFrame
        A DataFrame

    '''
    def aggregate(root):
        value = df_convertible.loc[root.cnode_id,:]
        for child in root.children:
             value += aggregate(child)
        return value

    names = df_convertible.columns.names

    import pandas as pd
    return (pd.concat(objs = [ aggregate(n) for n in ct.iterate_on_call_tree(call_tree) ],
                keys = [ n.cnode_id for n in ct.iterate_on_call_tree(call_tree)])
                .rename_axis(mapper = ['Cnode ID'] + names,axis = 'index')
                .unstack(names)
                )
