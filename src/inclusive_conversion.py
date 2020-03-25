'''
Utilities to convert metrics to inclusive.
'''

import calltree as ct

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


def transpose_for_conversion(df):
    '''
    In order to be converted, the index must contain only ``Cnode ID``.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be transposed

    Returns
    -------
    transposed: pandas.DataFrame
        The transposed DataFrame with ``Cnode ID`` as index.
    '''
    levels_to_unstack = [ name for name in df.index.names if name != 'Cnode ID']
    return df.unstack(levels_to_unstack)

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
