"""
Utilities to merge the information that comes from multiple '.cubex' files
"""
import calltree as ct
import datadump as dd
import logging


def process_cubex(profile_file):
    # Getting all callgraph information
    logging.debug(f"Reading {profile_file}...")
    call_tree_df = ct.get_call_tree_df(profile_file)
    dump_df = dd.get_dump(profile_file)

    df = dump_df.merge(call_tree_df, how='inner', on='Cnode ID')

    return {'calltree': call_tree_df, 'df': df}


def check_column_sets(column_sets):
    ''' 
    Checking that any pair of column sets shares only
    the columns that are common to all sets.
    '''
    common_cols = set.intersection(*column_sets)
    noncommon_columns_df = [ column_set.difference(common_cols) for column_set in column_sets ]

    from itertools import combinations
    for nccs1,nccs2 in combinations(noncommon_columns_df,2):
        assert len(nccs1.intersection(nccs2)) == 0, f"{nccs1}, {nccs2}"
    logging.debug("Column sets are ok.")

def process_multi(profile_files):
    import pandas as pd
    # Assuming that the calltree info is equal for all
    # .cubex files, up to isomorphism.
    call_tree_info = process_cubex(profile_files[0])['calltree']

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

    # finding columns common to all DFs
    # and creating a dataframe for those
    columns_df = [set(df.columns) for df in dfs2]
    common_cols = set.intersection(*columns_df)

    dfs2_common = [df.loc[:, common_cols] for df in dfs2]

    for i, df2 in enumerate(dfs2_common):
        df2.columns = pd.MultiIndex.from_tuples([(i, col)
                                                 for col in common_cols],
                                                names=['run', 'metric'])

    df_common = pd.concat(dfs2_common, axis='columns', join='inner')

    noncommon_columns_df = [ columns.difference(common_cols) for columns in columns_df ]

    dfs2_noncommon = [ df.loc[:,noncommon_columns] for df,noncommon_columns in zip(dfs2,noncommon_columns_df)]
    df_noncommon = pd.concat(dfs2_noncommon, axis='columns', join='inner')

    # TODO: Add the info from the call tree to the 
    #       dataframes
    return df_common,df_noncommon
