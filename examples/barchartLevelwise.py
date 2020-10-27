#!/usr/bin/env python3
##################################################################
#
# Produce a bar chart plot, where bars represent the time spent (or some other
# metric) in a given functions, or some other metric function-wise. The data
# to plot represents the function calls a given level of the calltree (the
# script can be modified to be to select any range of levels).
#
# Author    : Dr Chennakesava Kadapa
# Date      : 02-Apr-2020
# Copyright : @SA2C
##################################################################
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

import merger as mg
import index_conversions as ic
import pandas as pd
import matplotlib.pyplot as plt
import calltree as ct
import sys
import os

inpfilename = "../test_data/profile-25m-nproc40-nsteps10.cubex"
metric = "time"
exclincl = Fals
e
nfuncs = 10

if len(sys.argv) > 1:
    inpfilename = sys.argv[1]

if len(sys.argv) > 2:
    metric = sys.argv[2]

if len(sys.argv) > 3:
    exclincl = (sys.argv[3] == "T")

if len(sys.argv) > 4:
    nfuncs = int(sys.argv[4])

#######################################################
# This gives us a number of outputs
# (see https://cupybelib.readthedocs.io/en/latest/merger.html)

output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

parent_series = (output_i
                 .ctree_df
                 .set_index('Cnode ID')
                 .loc[:,'Parent Cnode ID'])

# get depth level for each function in the call tree
levels = ct.get_level(parent_series)


# We convert the Cnode IDs to short callpaths in the dataframe.
df_i = ic.convert_index(
    output_i.df, output_i.ctree_df, target='Short Callpath')


# extract the data
res = df_i.reset_index()[['Short Callpath', 'Thread ID',
                          metric]].groupby('Short Callpath').sum().sort_values(
                              [metric])[metric]

res_df = pd.DataFrame(res)

#res_df.index = pd.MultiIndex.from_tuples(res_df.index.str.split(',').tolist())
time = res_df.reset_index()['time']
fname = res_df.reset_index()['Short Callpath'].str.extract(
    r'(\w+),([0-9]+)')[0]
cnode_id = res_df.reset_index()['Short Callpath'].str.extract(
    r'(\w+),([0-9]+)')[1].astype(int)

combined = pd.merge(
    left = (pd.concat([time, fname, cnode_id], axis='columns')
        .rename({'time': 'time', 0: 'fname', 1: 'Cnode ID'},
                axis='columns')),
    right=levels.reset_index().rename({0: 'level'}, axis='columns'),
    on='Cnode ID')


# to extract functions called only at the 3rd level
time_data = combined[combined['level'] == 2].sort_values(
    by=['level', 'time'], ascending=False)

print(time_data)

time_data.plot(kind='bar', x='fname', y='time')

plt.xlabel("Function name", fontsize=14)
plt.title(
    "metric=" + metric + " " +
    ("(Exclusive)" if exclincl == True else "(Inclusive)"),
    fontsize=14)
plt.legend('', frameon=False)

metric_time_list = ["time", "max_time", "min_time"]

if (metric in metric_time_list):
    plt.ylabel("Time [s]", fontsize=14)
    plt.yscale('log')
elif (metric == "visits"):
    plt.ylabel("Number of visits", fontsize=14)
else:
    print("Metric type not supported!")
    sys.exit()

plt.xticks(rotation=70)
plt.tight_layout()
plt.show()

