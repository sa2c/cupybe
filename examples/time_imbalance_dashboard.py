#!/usr/bin/env python3
"""
This example script processes a single `.cubex` file, starts a dashboard to
display the data as a sunburst or a treemap plot (the user can switch the 
visualisation to both types). The threshold for displaying the branches/leaves 
of the calltree, in terms of fraction of total runtime, can be adjusted with 
the slider.

Usage: ./example3.py <cubex file> 

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

    data_nofilter = (
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
    )

    def filter_small_time(df, rel_threshold):
        """
        Removes rows relative to small time function calls.
        """
        column = df["Time (Inclusive)"]
        condition = column > column.max() * rel_threshold
        return df.loc[condition, :]

    # PLOTLY
    import plotly.express as px

    # sunburst
    def sunburst(data):
        return px.sunburst(
            data,
            names=data["Short Callpath"],
            parents=data["Parent"],
            values=data["Time (Inclusive)"],
            color=data["Time Imbalance"],
            branchvalues="total",
        )

    # treemap
    def treemap(data):
        return px.treemap(
            data,
            names=data["Short Callpath"],
            parents=data["Parent"],
            values=data["Time (Inclusive)"],
            color=data["Time Imbalance"],
            branchvalues="total",
        )

        import dash

    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output

    external_stylesheets = []  #'https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    style_centered = {"text-align": "center"}
    app.layout = html.Div(
        style={"position": "fixed", "width": "100%", "height": "50em"},
        children=[
            html.H1(
                children="Cube Dump Data",
                style={
                    "text-align": "center",
                    "top": "0%",
                    "height": "10%",
                    "width": "100%",
                },
            ),
            html.Div(
                style={
                    "position": "absolute",
                    "top": "10%",
                    "width": "100%",
                    "height": "90%",
                },
                children=[
                    html.Div(
                        style={
                            "margin": "auto",
                            "position": "absolute",
                            "top": "0%",
                            "left": "0%",
                            "width": "15%",
                            "height": "100%",
                        },
                        children=[
                            html.H3(
                                children="Min Time threshold", style=style_centered
                            ),
                            dcc.Slider(
                                id="log-min-time-threshold",
                                min=-3,
                                step=0.1,
                                max=-0.5,
                                value=-2,
                            ),
                            html.Div(
                                children=[
                                    html.H5(
                                        children="Threshold Value:",
                                        style=style_centered,
                                    ),
                                    html.H5(id="threshold-value", children="0.01"),
                                ]
                            ),
                            html.H5(
                                children="Visualisation type", style=style_centered
                            ),
                            dcc.Dropdown(
                                id="vis-choice",
                                options=[
                                    {"label": "Treemap", "value": "treemap"},
                                    {"label": "Sunburst", "value": "sunburst"},
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "position": "absolute",
                            "top": "0%",
                            "right": "0%",
                            "width": "85%",
                            "height": "100%",
                        },
                        children=[
                            dcc.Graph(
                                id="hierarchy-datavis",
                                figure=treemap(filter_small_time(data_nofilter, 0.01)),
                                style={
                                    "position": "absolute",
                                    "height": "100%",
                                    "width": "100%",
                                },
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("hierarchy-datavis", "figure"),
        [Input("log-min-time-threshold", "value"), Input("vis-choice", "value")],
    )
    def update_visualisation(logthreshold, vistype):
        threshold = 10 ** logthreshold
        data = filter_small_time(data_nofilter, threshold)
        if vistype == "treemap":
            return treemap(data)
        elif vistype == "sunburst":
            return sunburst(data)
        else:  # Default
            return sunburst(data)

    @app.callback(
        Output("threshold-value", "children"),
        [Input("log-min-time-threshold", "value")],
    )
    def update_threshold_text(value):
        return f"{(10 ** value):1.4f}"

    if __name__ == "__main__":
        app.run_server(debug=True)
