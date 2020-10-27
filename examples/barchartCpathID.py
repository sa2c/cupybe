#!/usr/bin/env python3
##################################################################
#
# Script for plotting score-p profile data using 'cupybe' library
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
import numpy as np

if len(sys.argv) > 1:
    inpfilename = sys.argv[1]
else:
    inpfilename = "../test_data/profile-25m-nproc40-nsteps10.cubex"
    metric = "time"
    exclincl = False
    callpathid = 164
    print(f"No input specified!")

if len(sys.argv) > 2:
    metric = sys.argv[2]

if len(sys.argv) > 3:
    exclincl = (sys.argv[3] == "T")

if len(sys.argv) > 4:
    callpathid = int(sys.argv[4])


def pretty_print(string):
    num_spaces = 65 - len(string)
    print('# ' + string + ' ' * (num_spaces if num_spaces > 0 else 0) + ' #')


print('#' * 69)
pretty_print(f'Parameters:')
pretty_print(f'inpfilename: {inpfilename}')
pretty_print(f'metric:      {metric}')
pretty_print(f'exclincl:    {exclincl}')
pretty_print(f'callpathid:  {callpathid}')
print('#' * 69)

#### get the data for the given metric

# This gives us a number of outputs
# (see https://cupybelib.readthedocs.io/en/latest/merger.html)

output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

# We convert the Cnode IDs to short callpaths in the dataframe.
df_i = ic.convert_index(
    output_i.df, output_i.ctree_df, target='Short Callpath')

df_i = df_i.reset_index()
df_i = df_i.rename(columns={"Short Callpath": "Short_Callpath"})
df_i = df_i.rename(columns={"Thread ID": "Thread_ID"})
df_i[['Callpath', 'CpathID']] = df_i.Short_Callpath.str.split(",", expand=True)
df_i.CpathID = df_i.CpathID.astype(int)
df_i["Thread_ID"] = df_i["Thread_ID"].astype(int)

# extract the data

res_df = df_i[df_i['CpathID'] == callpathid]

plt.bar(res_df['Thread_ID'], res_df['time'], label=res_df.iloc[0, 0])

plt.xlabel("CPU number", fontsize=14)
plt.title(
    "metric=" + metric + " " +
    ("(Exclusive)" if exclincl == True else "(Inclusive)"),
    fontsize=14)
plt.legend()

metric_time_list = ["time", "max_time", "min_time"]

if (metric in metric_time_list):
    plt.ylabel("Time [s]", fontsize=14)
elif (metric == "visits"):
    plt.ylabel("Number of visits", fontsize=14)
else:
    print("Metric type not supported!")
    sys.exit()

xtks = np.linspace(1, len(res_df), num=9, dtype=int)
plt.xticks(xtks)
plt.xticks(rotation=70)
plt.tight_layout()

figfilename = "FuncsVsMetric.png"
print(f"Saving figure in {figfilename}.")
plt.savefig(figfilename)
