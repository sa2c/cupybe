#!/usr/bin/env python3
################################################################################
# Author    : Dr Chennakesava Kadapa
# Date      : 02-Apr-2020
# Copyright : @SA2C
################################################################################
#
# Usage:
#
# barchartNfuncs.py <cubex-filename>  <metric>  <exclincl>  <nfuncs>
# <cubex-filename> : name of the .cubex file
# <metric>         : visits, time, max_time, min_time
# <exclincl>       : T = Exclusive, F = Inclusive
# <nfuncs>         : number of functions to plot
#
# Example:
#
# python3  barchartNfuncs.py  profile.cubex  time T  10
#
################################################################################
'''
Produces a bar chart plot of time spent (or some other metric) in the functions
called by a root function that can be chosen by name.
'''
if __name__ == '__main__':
    import merger as mg
    import index_conversions as ic
    import pandas as pd
    import matplotlib.pyplot as plt
    import calltree as ct
    import os
    
    data_dir = "../test_data"
    inpfilename = os.path.join(data_dir, "profile-5m-nproc40-nsteps10.cubex")
    metric = "time"
    exclincl = False
    
    rootfuncname = "ns3d_"
    
    ### Processing
    
    # Reading, parsing and loading data in the cubex file
    output_i = mg.process_cubex(inpfilename, exclusive=exclincl)
    
    call_tree = output_i.ctree
    
    func_node = next(
        node for node in ct.iterate_on_call_tree(call_tree)
        if node.fname == rootfuncname)
    
    children_info = [
        node.fname + "," + str(node.cnode_id)
        for node in ct.iterate_on_call_tree(func_node, 1)
    ]
    
    # We convert the Cnode IDs to short callpaths in the dataframe.
    df_i = ic.convert_index(
        output_i.df, output_i.ctree_df, target='Short Callpath')
    
    res_df = df_i.loc[children_info]
    
    res = res_df.reset_index()[[
        'Short Callpath', 'Thread ID', metric
    ]].groupby('Short Callpath').sum().sort_values([metric],
                                                   ascending=False)[metric]
    
    res = res.head(11 if len(res) > 11 else len(res)).tail(
        10 if len(res) > 10 else len(res) - 1)
    
    res.plot(kind='bar')
    
    plt.xlabel(
        "Function name: " + rootfuncname, fontsize=12, color='blue', fontweight='bold')
    plt.title(
        "metric: " + metric + " " +
        ("(Exclusive)" if exclincl == True else "(Inclusive)"),
        fontsize=12)
    plt.ylabel("Time [s]", fontsize=12)
    
    plt.legend('', frameon=False)
    
    plt.tight_layout()
    plt.yscale('log')
    plt.ylim(10**1, 10**4)
    plt.xticks(rotation=80)
    plt.show()
    
