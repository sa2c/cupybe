#!/usr/bin/env python3
##################################################################
#
# Script for plotting score-p profile data using 'pycube' library
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


inpfilename ="../test_data/profile-25m-nproc40-nsteps10.cubex"
metric = "time"
exclincl = False
nfuncs = 10

if len(sys.argv) > 1:
    inpfilename = sys.argv[1]
else:
    print("No input file specified!")
    sys.exit()

if len(sys.argv) > 2:
    metric = sys.argv[2]

if len(sys.argv) > 3:
    exclincl = (sys.argv[3] == "T")

if len(sys.argv) > 4:
    nfuncs = int(sys.argv[4])


#### get depth level for each function in the call tree
#
#######################################################

call_tree = ct.get_call_tree(inpfilename)

df = ct.calltree_to_df(call_tree).set_index('Cnode ID')

parent_series = df['Parent Cnode ID']

levels = ct.get_level(parent_series)


#### get the data for the given metric
#
######################################

# This gives us a number of outputs 
# (see https://pycubelib.readthedocs.io/en/latest/merger.html)
#output_i = mg.process_cubex('../test_data/profile.cubex', exclusive=False)
#output_i = mg.process_cubex('../test_data/profile-25m-nproc40-nsteps10.cubex', exclusive=True)

output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

# We convert the Cnode IDs to short callpaths in the dataframe.
df_i = ic.convert_index(output_i.df, output_i.ctree_df, target = 'Short Callpath')

#df_i = df_i.rename(columns={"Short Callpath": "Short_Callpath"})
#df_i[['Callpath','CpathID']] = df_i.Short_Callpath.str.split(",",expand=True)
#df_i.CpathID = df_i.CpathID.astype(int)

# extract the data
res = df_i.reset_index()[['Short Callpath', 'Thread ID', metric]].groupby('Short Callpath').sum().sort_values([metric])[metric]

res_df = pd.DataFrame(res)

#res_df.index = pd.MultiIndex.from_tuples(res_df.index.str.split(',').tolist())
time = res_df.reset_index()['time']
fname = res_df.reset_index()['Short Callpath'].str.extract(r'(\w+),([0-9]+)')[0]
cnode_id = res_df.reset_index()['Short Callpath'].str.extract(r'(\w+),([0-9]+)')[1].astype(int)

combined = pd.merge(left= pd.concat([time,fname,cnode_id], axis = 'columns').rename({'time':'time',0:'fname',1:'Cnode ID'},axis = 'columns'), right = levels.reset_index().rename({0 : 'level'}, axis = 'columns'),on = 'Cnode ID')

#time_data = combined.sort_values(by = ['level','time']).head(10)

# to extract levels below third levels
time_data = combined[combined['level'] == 2].sort_values(by = ['level','time'], ascending=False)

print(time_data)

time_data.plot(kind='bar', x='fname', y='time')

plt.xlabel("Function name", fontsize=14)
plt.title("metric="+metric+" "+("(Exclusive)" if exclincl==True else "(Inclusive)"), fontsize=14)
plt.legend('',frameon=False)

metric_time_list = ["time", "max_time", "min_time"]

if (metric in metric_time_list):
    plt.ylabel("Time [s]", fontsize=14)
    plt.yscale('log')
elif (metric == "visits"):
    plt.ylabel("Number of visits", fontsize=14)
#    plt.yscale('log')
#    if(max(data[:,2]) > 10**4):
else:
    print("Metric type not supported!")
    sys.exit()

plt.xticks(rotation=70)
plt.tight_layout()
#plt.show()

plt.savefig("FuncsVsMetric.png")
