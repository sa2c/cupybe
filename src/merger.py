"""
Utilities to merge the information that comes from multiple '.cubex' files
"""
import calltree as ct
import datadump as dd
import logging


def process_cubex(profile_file):
    import pandas as pd
    # Getting all callgraph information
    logging.debug(f"Reading {profile_file}...")
    call_tree = ct.get_call_tree(profile_file)
    call_tree_df = ct.calltree_to_df2(call_tree)
    dump_df = dd.get_dump(profile_file)

    df = pd.merge(dump_df, call_tree_df, how='inner', on='Cnode ID')

    return {'calltree': call_tree, 'calltree_df': call_tree_df, 'df': df}


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


def process_multi(profile_files):
    import pandas as pd
    # Assuming that the calltree info is equal for all
    # .cubex files, up to isomorphism.
    first_file_info = process_cubex(profile_files[0])
    call_tree = first_file_info['calltree']
    call_tree_df = first_file_info['calltree_df']

    logging.debug(f"Reading {len(profile_files)} files...")
    dfs = [process_cubex(pf)['df'] for pf in profile_files]

    def adjust_df(df):
        # Function names, Cnode ID and Parent Cnode ID
        # can always be retrieved from the full callpath.
        # Cnode IDs could also change between '.cubex' files,
        # in principle.
        cols_to_drop = ['Cnode ID', 'Function Name', 'Parent Cnode ID']
        # TODO: Move from using 'Thread ID' to the proper
        #       full system path.
        new_index_columns = ['Full Callpath', 'Thread ID']
        return (df.drop(cols_to_drop,
                        axis='columns').set_index(new_index_columns))

    logging.debug(f"Adjusting dataframes...")
    dfs2 = [adjust_df(df) for df in dfs]

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

    def replace_fcpath_with_cnodeID(df):
        colnames = df.columns.names + ['Thread ID']
        return (df
                .unstack('Thread ID')
                .pipe( lambda x: pd.DataFrame(
                        data=x.values, 
                        index=x.index, 
                        columns=pd.Index(x.columns)))
                .join(tmp, how='inner')
                .set_index('Cnode ID') # nukes the current idx
                .pipe( lambda x: pd.DataFrame(
                        data=x.values,
                        index=x.index,
                        columns=pd.MultiIndex.from_tuples(
                            x.columns, 
                            names=colnames)
                        )))

    df_common = replace_fcpath_with_cnodeID(df_common)
    df_noncommon = replace_fcpath_with_cnodeID(df_noncommon)

    return call_tree, df_common, df_noncommon


def convert_series_to_inclusive(series, call_tree):
    '''
    Converts a series having Cnode IDs as index from exclusive to inclusive.
    Takes as input a CallTreeNode object (hopefully the root).
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

def convert_df_to_inclusive(df_by_cnode_id, call_tree):
    '''
    Converts a DataFrame having Cnode IDs as index from exclusive to inclusive.
    '''
    def aggregate(root):
        value = df_by_cnode_id.loc[root.cnode_id,:]
        for child in root.children:
             value += aggregate(child)
        return value

    import pandas as pd
    return (pd.concat(objs = [ aggregate(n) for n in ct.iterate_on_call_tree(call_tree) ],
                keys = [ n.cnode_id for n in ct.iterate_on_call_tree(call_tree)])
                .rename_axis(mapper = ['Cnode ID', 'metric', 'Thread ID'],axis = 'index')
                .unstack(['metric','Thread ID'])
                )



