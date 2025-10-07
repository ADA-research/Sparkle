"""Helper classes/method for LaTeX and bibTeX."""

import math

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import pylatex as pl
import kaleido

kaleido.get_chrome_sync()  # Ensure chrome is available for Kaleido


class AutoRef(pl.base_classes.CommandBase):
    """AutoRef command for PyLateX."""

    _latex_name = "autoref"
    packages = [pl.Package("hyperref")]


def comparison_plot(
    data_frame: pd.DataFrame, title: str = None
) -> plotly.graph_objects.Figure:
    """Creates a comparison plot from the given data frame.

    The first column is used for the x axis, the second for the y axis.

    Args:
        data_frame: The data frame with the data
        x_label: The label for the x axis
        y_label: The label for the y axis
        title: The title of the plot
        output_plot: The path where the plot should be written to

    Returns:
        The plot object
    """
    from scipy import stats

    # Determine if data is log scale, linregress tells us how linear the data is
    linregress = stats.linregress(
        data_frame[data_frame.columns[0]].to_numpy(),
        data_frame[data_frame.columns[1]].to_numpy(),
    )
    log_scale = not (linregress.rvalue > 0.65 and linregress.pvalue < 0.05)

    if log_scale and (data_frame < 0).any(axis=None):
        # Log scale cannot deal with negative and zero values, set to smallest non zero
        data_frame[data_frame < 0] = np.nextafter(0, 1)

    # Maximum value should come from the objective?
    min_value, max_value = data_frame.min(axis=None), data_frame.max(axis=None)
    # Slightly more than min/max for interpretability
    if log_scale:  # Take next step on log scale
        max_value = 10 ** math.ceil(math.log(max_value, 10))
        plot_range = (min_value, max_value)
    else:  # Take previous/next step on linear scale
        order_magnitude = math.ceil(math.log(max_value, 10))
        next_step_max = math.ceil(max_value / (10 ** (order_magnitude - 1))) * 10 ** (
            order_magnitude - 1
        )
        plot_range = (0, next_step_max) if min_value > 0 else (min_value, next_step_max)
    fig = px.scatter(
        data_frame=data_frame,
        x=data_frame.columns[0],
        y=data_frame.columns[1],
        range_x=plot_range,
        range_y=plot_range,
        title=title,
        log_x=log_scale,
        log_y=log_scale,
        width=1000,
        height=1000,
    )
    # Add dividing diagonal
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=max_value,
        y1=max_value,
        line=dict(color="grey", dash="dot", width=1),
    )
    # Add maximum lines
    fig.add_shape(
        type="line",
        opacity=0.7,
        x0=0,
        y0=max_value,
        x1=max_value,
        y1=max_value,
        line=dict(color="red", width=1.5, dash="longdash"),
    )
    fig.add_shape(
        type="line",
        opacity=0.7,
        x0=max_value,
        y0=0,
        x1=max_value,
        y1=max_value,
        line=dict(color="red", width=0.5, dash="longdash"),
    )
    fig.update_traces(marker=dict(color="RoyalBlue", symbol="x"))
    fig.update_layout(plot_bgcolor="white", autosize=False, width=1000, height=1000)
    minor = dict(ticks="inside", ticklen=6, showgrid=True) if log_scale else None
    # Tick every 10^(log(max)) / 10 for linear scale, log scale is resolved by plotly
    dtick = 1 if log_scale else 10 ** (math.ceil(math.log(max_value, 10)) - 1)
    fig.update_xaxes(
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        minor=minor,
        dtick=dtick,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    fig.update_yaxes(
        mirror=True,
        tickmode="linear",
        ticks="outside",
        tick0=0,
        minor=minor,
        dtick=dtick,
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    return fig
