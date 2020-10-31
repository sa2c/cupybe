#!/usr/bin/env python3
"""
This example script processes a single `.cubex` file, and shows the
inclusive time as a sunburst plot and as a treemap.
The color of the plot elements is now dependent on the imbalance between ranks.

Usage: ./example2.py <cubex file> 

if <cubex file> is not provided, '../test_data/profile.cubex' is used.

"""
if __name__ == "__main__":
    import merger as mg
    import index_conversions as ic
    import pandas as pd
    from sys import argv

    # This gives us a number of outputs
    # (see https://cupybelib.readthedocs.io/en/latest/merger.html)

    if len(argv) == 1:
        input_file = "../test_data/profile.cubex"
    else:
        input_file = argv[1]
        print("Opening file", input_file)

    output_i = mg.process_cubex(input_file, exclusive=False)

    df_i = output_i.df  # Dataframes with the metrics

    tree = output_i.ctree_df  # Dataframe containing info on the calltree

    # We convert the Cnode IDs to short callpaths in the dataframe.
    df_i = ic.convert_index(df_i, tree, target="Short Callpath")

    # We calculate the mean of the time
    times_mean = df_i.time.groupby("Short Callpath").mean().rename("mean")

    # We get a measure of imbalance between threads
    times_max = df_i.time.groupby("Short Callpath").max()
    times_min = df_i.time.groupby("Short Callpath").min()
    times_imbalance = ((times_max - times_min) / times_mean).rename("imbalance")

    # We do a merge (=join) on the tree dataframe to find the parent-child relation
    parent_child = (
        pd.merge(
            left=tree,
            right=tree,
            left_on="Cnode ID",
            right_on="Parent Cnode ID",
            suffixes=("-Parent", ""),
        )
        # we select the two columns we're interested in
        .loc[:, ["Short Callpath", "Short Callpath-Parent"]].set_index("Short Callpath")
    )  # so that we can join eas

    def filter_small_time(df, rel_threshold):
        """
        Removes rows relative to small time function calls.
        """
        column = df["Time (Inclusive)"]
        condition = column > column.max() * rel_threshold
        return df.loc[condition, :]

    data = (
        pd.concat([times_mean, times_imbalance, parent_child], axis="columns")
        .reset_index()
        .rename(
            mapper={
                "index": "Short Callpath",
                "mean": "Time (Inclusive)",
                "imbalance": "Time Imbalance",
                "Short Callpath-Parent": "Parent",
            },
            axis="columns",
        )
        .pipe(filter_small_time, rel_threshold=0.0001)
    )

    # PLOTLY
    import plotly.express as px

    # sunburst
    sunburst = px.sunburst(
        data,
        names=data["Short Callpath"],
        parents=data["Parent"],
        values=data["Time (Inclusive)"],
        color=data["Time Imbalance"],
        branchvalues="total",
    )

    # Shows in a browser.
    sunburst.show()  # it can be exported to .png or .jpeg from the browser view
    sunburst.write_html("sunburst2.html")  # a huge html file is produced

    # treemap
    treemap = px.treemap(
        data,
        names=data["Short Callpath"],
        parents=data["Parent"],
        values=data["Time (Inclusive)"],
        color=data["Time Imbalance"],
        branchvalues="total",
    )

    # Shows in a browser.
    treemap.show()  # it can be exported to .png or .jpeg from the browser view
    treemap.write_html("treemap2.html")  # a huge html file is produced
