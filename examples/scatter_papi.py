#!/usr/bin/env python3
"""
This example reads the `.cubex` files containing PAPI counter values produced
by scalasca and combines them using CUPyBE.
Then, it creates some scatter plots (using matplotlib) which mimic the 
roofline diagrams, estimating an arithmetic intensity-like and a FLOP-like 
quantity from, respectively, load/store operations or cache reads and floating 
point vector operations, and floating point operations and execution time.

Usage: ./scatter_papi.py [scalasca dir]

If `scalasca dir` is absent, then the current directory is taken as input.
"""
if __name__ == "__main__":
    import merger as mg
    import calltree as ct
    import index_conversions as ic
    import pickle

    import pandas as pd
    from glob import glob
    from matplotlib import pyplot as plt
    from sys import argv
    from os import path

    # Get directory where all the files are
    if len(argv) == 1:
        input_dir = "."
    else:
        input_dir = argv[1]
        print("Opening dir", input_dir)

    # Reading all cubex files and parsing them using cupybe
    # If this has already done, load the picked file instead for speed.
    files = glob(path.join(input_dir, "*", "profile.cubex"))
    pickle_archive = path.join(input_dir, "data.pickle")

    try:
        with open(pickle_archive, "rb") as f:
            data = pickle.load(f)
        inoutput, exoutput, files_check = data
        if files_check != files:
            raise Exception("Data  does not contain the expected files.")
    except:
        inoutput = mg.process_multi(files, exclusive=False)
        exoutput = mg.process_multi(files, exclusive=True)
        with open(pickle_archive, "wb") as f:
            data = pickle.dump((inoutput, exoutput, files), f)

    # renaming variables for convenience
    inctree_df = inoutput.ctree_df
    inctree = inoutput.ctree
    inncmetrics = inoutput.ncmetrics

    # index from Cnode ID to short callpath for readability
    incommon = ic.convert_index(inoutput.common, inctree_df, target="Short Callpath")
    innoncommon = ic.convert_index(
        inoutput.noncommon, inctree_df, target="Short Callpath"
    )

    # renaming variables for convenience
    exctree_df = exoutput.ctree_df
    exctree = exoutput.ctree
    exncmetrics = exoutput.ncmetrics

    # index from Cnode ID to short callpath for readability
    excommon = ic.convert_index(exoutput.common, exctree_df, target="Short Callpath")
    exnoncommon = ic.convert_index(
        exoutput.noncommon, exctree_df, target="Short Callpath"
    )

    # list of Cnodes taking more than 1% of the total time.
    # exclusive, and inclusive

    intime = incommon.stack("run").time
    avgintime_rank = intime.groupby(["Short Callpath", "Thread ID"]).mean()
    avgintime = avgintime_rank.groupby("Short Callpath").sum()

    extime = excommon.stack("run").time
    avgextime_rank = extime.groupby(["Short Callpath", "Thread ID"]).mean()
    avgextime = avgextime_rank.groupby("Short Callpath").sum()

    # total_time == avgintime.max(), only if all the data is considered.
    total_time = avgextime.sum()
    threshold = 0.01
    significant_nodes_ex = avgextime > total_time * threshold
    significant_nodes_in = avgintime > total_time * threshold

    # focusing now on significant, exclusive statistics
    ## initialisation, known to be in function 'initia_'

    initialisation_node = next(
        n for n in ct.iterate_on_call_tree(exctree) if n.fname == "initia_"
    )

    cnode_index = exnoncommon.unstack("Thread ID").index
    not_initialisation = pd.Series(data=True, index=cnode_index)

    for n in ct.iterate_on_call_tree(initialisation_node):
        not_initialisation[n.fname + "," + str(n.cnode_id)] = False

    ## MPI functions
    mpi_cnodes = pd.Series(data=cnode_index.str.contains("MPI"), index=cnode_index)

    ## Taking only data that
    ## - is significant
    ## - is not initialisation
    ## - is not mpi calls
    significant_exnoncommon = exnoncommon.unstack("Thread ID")[
        significant_nodes_ex & not_initialisation & (~mpi_cnodes)
    ].stack("Thread ID")

    # categorical out of the index
    cnodes = pd.Series(
        data=significant_exnoncommon.reset_index()["Short Callpath"], dtype="category"
    )
    cnodes.index = significant_exnoncommon.index

    ## computing metrics

    # average time spent on cnode on a given rank for the chosen cnodes
    significant_avgextime_rank = avgextime_rank.unstack("Thread ID")[
        significant_nodes_ex & not_initialisation & (~mpi_cnodes)
    ].stack("Thread ID")

    # Total instructions per second
    ops = significant_exnoncommon.PAPI_TOT_INS / significant_avgextime_rank

    # vectorised operations, single precision and double precision, per second
    flops_vec = (
        significant_exnoncommon.PAPI_VEC_SP + significant_exnoncommon.PAPI_VEC_DP
    ) / significant_avgextime_rank

    # ratio between vectorised operations and L3 RW operations
    arithint_3 = (
        significant_exnoncommon.PAPI_VEC_SP + significant_exnoncommon.PAPI_VEC_DP
    ) / (significant_exnoncommon.PAPI_L3_TCR + significant_exnoncommon.PAPI_L3_TCW)

    # ratio between vectorised operations and L2 RW operations
    arithint_2 = (
        significant_exnoncommon.PAPI_VEC_SP + significant_exnoncommon.PAPI_VEC_DP
    ) / (significant_exnoncommon.PAPI_L2_TCR + significant_exnoncommon.PAPI_L2_TCW)

    arithint = (
        significant_exnoncommon.PAPI_VEC_SP + significant_exnoncommon.PAPI_VEC_DP
    ) / significant_exnoncommon.PAPI_LST_INS

    # plotting

    data_to_plot = pd.concat(
        [
            cnodes,
            significant_avgextime_rank,
            ops,
            flops_vec,
            arithint_2,
            arithint_3,
            arithint,
        ],
        axis="columns",
    )
    data_to_plot.columns = [
        "cnode",
        "time",
        "ops",
        "ops_vec",
        "arintv2",
        "arintv3",
        "arint",
    ]

    data_to_plot["size"] = (data_to_plot.time / data_to_plot.time.max() * 100).astype(
        int
    )

    def plot_scatter(x, y, title):
        # not working due to a bug in 1.0.3
        plt.figure()
        ax = plt.axes()

        from itertools import cycle

        colors = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        markers = cycle([".", "o", "v", "^", "<", ">", "s", "*", "+", "x", "D"])

        data_to_plot.groupby("cnode").apply(
            lambda df: df.plot.scatter(
                x=x,
                y=y,
                s=df["size"],
                label=df.cnode[0],
                ax=ax,
                color=next(colors),
                marker=next(markers),
            )
        )

        plt.legend()
        plt.title(title)

    plot_scatter("arintv2", "ops_vec", "Pseudo-roofline L2")
    plot_scatter("arintv3", "ops_vec", "Pseudo-roofline L3")
    plot_scatter("arint", "ops_vec", "Pseudo-roofline - LD-ST")

    ## Tabling data
    # Significant ExNonCommon aggregate
    senc_aggregate = significant_exnoncommon.groupby("Short Callpath").sum()
    # Significant Time aggregate
    st_aggregate = significant_avgextime_rank.groupby("Short Callpath").sum()

    # Total cache misses
    fig = plt.figure(figsize=(8, 6))
    senc_aggregate[[col for col in senc_aggregate.columns if "TCM" in col]].plot.barh(
        ax=plt.axes()
    )
    plt.title("Cache Misses")
    fig.subplots_adjust(left=0.2)

    # Total time, for reference
    fig = plt.figure(figsize=(8, 6))
    st_aggregate.plot.barh(ax=plt.axes())
    plt.title("Aggregate time")
    fig.subplots_adjust(left=0.2)
