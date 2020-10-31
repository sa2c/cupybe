#!/usr/bin/env python3
##################################################################
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
"""
Produces a bar chart plot that displays the time spent in the N
most expensive functions.
"""
if __name__ == "__main__":
    import merger as mg
    import index_conversions as ic
    import matplotlib.pyplot as plt
    import sys

    inpfilename = "../test_data/profile-25m-nproc40-nsteps10.cubex"
    metric = "time"
    exclincl = True
    nfuncs = 10

    if len(sys.argv) > 1:
        inpfilename = sys.argv[1]

    if len(sys.argv) > 2:
        metric = sys.argv[2]

    if len(sys.argv) > 3:
        exclincl = sys.argv[3] == "T"

    if len(sys.argv) > 4:
        nfuncs = int(sys.argv[4])

    # This gives us a number of outputs
    # (see https://cupybe.readthedocs.io/en/latest/merger.html)

    output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

    # We convert the Cnode IDs to short callpaths in the dataframe.
    df_i = ic.convert_index(output_i.df, output_i.ctree_df, target="Short Callpath")

    # We calculate the mean of the time

    res = (
        df_i.reset_index()[["Short Callpath", "Thread ID", metric]]
        .groupby("Short Callpath")
        .sum()
        .sort_values([metric], ascending=False)[metric]
        .head(nfuncs)
    )

    print(res)

    res.plot(kind="bar")

    plt.xlabel("Function name", fontsize=14)
    plt.title(
        "metric="
        + metric
        + " "
        + ("(Exclusive)" if exclincl == True else "(Inclusive)"),
        fontsize=14,
    )

    metric_time_list = ["time", "max_time", "min_time"]

    if metric in metric_time_list:
        plt.ylabel("Time [s]", fontsize=14)
    elif metric == "visits":
        plt.ylabel("Number of visits", fontsize=14)
    else:
        print("Metric type not supported!")
        sys.exit()

    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.show()
