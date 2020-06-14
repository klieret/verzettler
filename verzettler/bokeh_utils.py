#!/usr/bin/env python3

# 3rd
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


def interactive_int_histogram(
        data,
        bins,
        title,
        x_axis_label,
        x_tooltip
):
    """Plot interactive histogram using bokeh.

    Adapted from
    https://gist.github.com/bhishanpdl/43f5ddad264c1a712979ddc63dd3d6ee

    df: pandas dataframe
    col: column of panda dataframe to plot (eg. age of users)
    n_bins: number of bins, e.g. 9
    bin_range: list with min and max value. e.g. [10,100] age of users.
    title: title of plot. e.g. 'Airnb Users Age Distribution'
    x_axis_label: x axis label. e.g. 'Age (years)'.
    x_tooltip: x axis tooltip string. e.g. 'Age'

    """
    arr_hist, edges = np.histogram(data, bins=bins)

    # todo: do I really need pandas for this?
    # Column data source
    arr_df = pd.DataFrame({
        'count': arr_hist,
        'left': edges[:-1],
        'right': edges[1:],
        'middle': (edges[:-1]+edges[1:])/2}
    )
    arr_df['f_count'] = ['%d' % count for count in arr_df['count']]
    arr_df['f_middle'] = ['%d' % count for count in arr_df['middle']]

    # column data source
    arr_src = ColumnDataSource(arr_df)

    # Set up the figure same as before
    p = figure(
        plot_height=300,
        sizing_mode='scale_width',
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label='Count'
    )

    # Add a quad glyph with source this time
    p.quad(
        bottom=0,
        top='count',
        left='left',
        right='right',
        source=arr_src,
        fill_color='red',
        hover_fill_alpha=0.7,
        hover_fill_color='blue',
        line_color='black'
    )

    # Add style to the plot
    p.title.align = 'center'
    p.title.text_font_size = '18pt'
    p.xaxis.axis_label_text_font_size = '12pt'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.axis_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'

    # Add a hover tool referring to the formatted columns
    hover = HoverTool(tooltips=[(x_tooltip, '@f_middle'),
                                ('Count', '@f_count')])

    # Add the hover tool to the graph
    p.add_tools(hover)

    return p
