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
import numpy as np


#inpfilename ="../test_data/profile-25m-nproc40-nsteps10.cubex"
inpfilename ="profile-5m-nproc40-nsteps10.cubex"
metric = "time"
exclincl = False
callpathid = 56

#funcname = "MAIN__"
funcname = "ns3d_"

#### get depth level for each function in the call tree
#
#######################################################

call_tree = ct.get_call_tree(inpfilename)

#df = ct.calltree_to_df(call_tree).set_index('Cnode ID')

#parent_series = df['Parent Cnode ID']

#levels = ct.get_level(parent_series)

func_node = next( node for node in ct.iterate_on_call_tree(call_tree) if node.fname==funcname)

children_info = [ node.fname+","+str(node.cnode_id) for node in ct.iterate_on_call_tree(func_node, 1) ]


#####
#
output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

# We convert the Cnode IDs to short callpaths in the dataframe.
df_i = ic.convert_index(output_i.df, output_i.ctree_df, target = 'Short Callpath')

res_df = df_i.loc[children_info]

res = res_df.reset_index()[['Short Callpath', 'Thread ID', metric]].groupby('Short Callpath').sum().sort_values([metric],ascending=False)[metric]

res = res.head( 11 if len(res) > 11 else len(res)).tail( 10 if len(res) > 10 else len(res)-1 )



res.plot(kind='bar')

plt.xlabel("Function name: "+funcname, fontsize=12, color='blue', fontweight='bold')
plt.title("metric: "+metric+" "+("(Exclusive)" if exclincl==True else "(Inclusive)"), fontsize=12)
plt.ylabel("Time [s]", fontsize=12)

plt.legend('', frameon=False)

plt.tight_layout()
plt.yscale('log')
plt.ylim(10**1, 10**4)
plt.xticks(rotation=80)
#plt.show()

plt.savefig("FuncsVsMetric.png")

