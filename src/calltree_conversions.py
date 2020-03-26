'''
Utilities to convert metrics to inclusive.
'''

import calltree as ct
import pandas as pd
import pandas as pd
import index_conversions as ic


def convert_series_to_inclusive(series, call_tree):
    '''
    Converts a series having Cnode IDs as index from exclusive to inclusive.
    Takes as input a CallTreeNode object (hopefully the root).

    *Notice: The results may be nonsensical unless the metric acted upon is 
    "INCLUSIVE convertible"*

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
    if type(series.index) == pd.MultiIndex and len(series.index.levels) > 1:
        raise NotImplementedError("MultiIndex not supported for series")

    assert series.index.name == "Cnode ID","MultiIndex not supported for series"

    # LRU cache does not work because of 
    # TypeError: unhashable type: 'list'
    #from functools import lru_cache
    #@lru_cache
    def aggregate(root):
        value = series.loc[root.cnode_id]
        for child in root.children:
             value += aggregate(child)
        return value

    return (pd.DataFrame(
            data = [ (node.cnode_id,aggregate(node)) 
                for node in ct.iterate_on_call_tree(call_tree) ],
            columns = ['Cnode ID','metric'])
        .set_index('Cnode ID')
        .metric)


def select_metrics(df, selected_metrics):
    ''' Selects `selected_metrics` out of a DataFrame.

    This function solves some problems:

    - Finding the ``metric`` level in ``df.columns``;
    - Selecting, out of ``selected_metrics`` only the ones that are also in the
      Data Frame;
    - Dealing with both the cases when ``df.columns`` is a 
      ``pandas.MultiIndex`` or a ``pandas.Index``.

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
    if type(df.columns) == pd.MultiIndex:
        metric_level = df.columns.names.index('metric')
        nlevels = len(df.columns.names)
        df_metrics = df.columns.levels[metric_level]
    elif type(df.columns) == pd.Index:
        assert df.columns.name == 'metric'
        metric_level = 0 
        nlevels = 1 
        df_metrics = df.columns

    # choosing the metrics
    possible_metrics = set(selected_metrics).intersection(
            set(df_metrics))

    if type(df.columns) == pd.MultiIndex:
        metric_indexer = [slice(None)]*nlevels
        metric_indexer[metric_level] = list(possible_metrics)
        return df.loc[:,tuple(metric_indexer)]
    elif type(df.columns) == pd.Index:
        return df.loc[:,list(possible_metrics)]



def convert_df_to_inclusive(df_convertible, call_tree, tree_df = None):
    '''
    Converts a DataFrame from exclusive to inclusive. A level named 
    ``Cnode ID``, ``Full Callpath`` or ``Short Callpath`` must be in the index.

    Parameters
    ----------
    df_convertible : pandas.DataFrame
        A DataFrame containing only metrics that can be converted safely from
        exclusive to inclusive.
    call_tree: CallTreeNode
        A recursive representation of the call tree.
    tree_df : pandas.DataFrame or None
        In case ``df_convertible`` is not indexed by ``Cnode ID``, a dataframe
        that can be used to retrieve the ``Cnode ID`` from the index of 
        ``df_convertible``.

    Returns
    -------
    res : DataFrame
        A DataFrame

    '''

    old_index_name = ic.find_index_col(df_convertible)

    # dfcr = df_convertible_reindexed
    dfcr = ic.convert_index(df_convertible,tree_df,target = 'Cnode ID')

    levels_to_unstack = [
        name for name in df_convertible.index.names if name != 'Cnode ID'
    ]
    df_transposed = df_convertible.unstack(levels_to_unstack)

    def aggregate(root):
        value = df_transposed.loc[root.cnode_id,:]
        for child in root.children:
             value += aggregate(child)
        return value

    names = df_transposed.columns.names

    return (pd.concat(
                objs = [ 
                    aggregate(n) for n in ct.iterate_on_call_tree(call_tree) 
                    ],
                keys = [ 
                    n.cnode_id for n in ct.iterate_on_call_tree(call_tree)
                    ]
                )
                .rename_axis(mapper = ['Cnode ID'] + names,axis = 'index')
                .unstack(names)
                .pipe(ic.convert_index,tree_df,old_index_name)
                .stack(levels_to_unstack)
                )
