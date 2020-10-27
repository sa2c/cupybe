#!/usr/bin/env python3
##################################################################
#
# Script for plotting score-p profile data using 'cupybe' library
#
# Author    : Dr Chennakesava Kadapa
# Date      : 20-Apr-2020
# Copyright : @SA2C
##################################################################
#
# Usage:
# Provide the list of .cubex files you want to use. See line 80.
#
# python3 barchartFuncwise-multiplecases.py
#
# Example:
#
# python3 barchartFuncwise-multiplecases.py
#
################################################################################

import merger as mg
import index_conversions as ic
import pandas as pd
import matplotlib.pyplot as plt
import calltree as ct
import sys
import os
import numpy as np

metric = "visits"
exclincl = False

funcnames = [
    "MAIN__", "initia_", "ns3d_", "splitblocks_", "tdist_calc_",
    "solve_jacobi_", "calc_flux_"
]

funcname = funcnames[0]


def get_metric_by_function(inpfilename):
    '''
    get depth level for each function in the call tree
    '''

    call_tree = ct.get_call_tree(inpfilename)

    func_node = next(
        node for node in ct.iterate_on_call_tree(call_tree)
        if node.fname == funcname)

    children_info = [
        node.fname + "," + str(node.cnode_id)
        for node in ct.iterate_on_call_tree(func_node, 1)
    ]

    #####
    #
    output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

    # We convert the Cnode IDs to short callpaths in the dataframe.
    df_i = ic.convert_index(
        output_i.df, output_i.ctree_df, target='Short Callpath')

    res_df = df_i.loc[children_info]

    res = res_df.reset_index()[[
        'Short Callpath', 'Thread ID', metric
    ]].groupby('Short Callpath').sum().sort_values([metric],
                                                   ascending=False)[metric]

    #res = res.head( 11 if len(res) > 11 else len(res)).tail( 10 if len(res) > 10 else len(res)-1 )
    res = res.head(11 if len(res) > 11 else len(res))

    return res


# Provide .cubex files here
data_dir = "../test_data"
data_filenames = [
    os.path.join(data_dir, "profile-5m-nproc40-nsteps10.cubex"),
    os.path.join(data_dir, "profile-10m-nproc40-nsteps10.cubex"),
    os.path.join(data_dir, "profile-25m-nproc40-nsteps10.cubex")
]

data_file1, data_file2, data_file3 = [
    get_metric_by_function(f) for f in data_filenames
]

# the sorted list of functions (wrt a metric) need not be the same in all the simulations)
# to make sure that we correctly plot the corresponding values for a particular function from multiple simulations
# let's create a new dataframe from the Series computed above for each simulation
#
df = pd.DataFrame({'M1': data_file1, 'M2': data_file2, 'M3': data_file3})

df.sort_values(['M1'], ascending=False, inplace=True)

df.plot(kind='bar')

plt.xlabel(
    "Function name: " + funcname, fontsize=12, color='blue', fontweight='bold')
plt.title(
    "metric: " + metric + " " +
    ("(Exclusive)" if exclincl == True else "(Inclusive)"),
    fontsize=12)
plt.legend(frameon=False)

metric_time_list = ["time", "max_time", "min_time"]

if (metric in metric_time_list):
    plt.ylabel("Time [s]", fontsize=12)
    plt.ylim(10**1, 10**5)
    plt.yscale('log')
elif (metric == "visits"):
    plt.ylabel("Number of visits", fontsize=12)
#    plt.yscale('log')
#    if(max(data[:,2]) > 10**4):
else:
    print("Metric type not supported!")
    sys.exit()

#plt.xticks(X, data_file1.index)
plt.xticks(rotation=80)
plt.tight_layout()

figfilename = "FuncsVsMetric.png"
print(f"Saving figure {figfilename}")
plt.savefig(figfilename, dpi=200)
