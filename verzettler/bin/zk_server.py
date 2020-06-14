#!/usr/bin/env python3

# std
import subprocess
import logging
from pathlib import Path
import threading
import collections

# 3rd
from flask import Flask
from flask import render_template, redirect
from bokeh.plotting import figure, output_file, save
from bokeh.embed import components
import numpy as np
from bokeh.resources import INLINE
import tabulate

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env
from verzettler.log import logger
from verzettler.note_converter import PandocConverter, dotgraph_html


templates = Path(__file__).resolve().parent.parent / "templates"
statics = Path(__file__).resolve().parent.parent / "static"


app = Flask(__name__, template_folder=templates, static_folder=statics)
app.config['SECRET_KEY'] = 'asfnfl1232#'

# https://stackoverflow.com/questions/9508667/reload-flask-app-when-template-file-changes
app.config['TEMPLATES_AUTO_RELOAD'] = True

zk = Zettelkasten()
for d in get_zk_base_dirs_from_env():
    zk.add_notes_from_directory(d)

# jekyll_converter = JekyllConverter(zk=zk)
pandoc_converter = PandocConverter(zk=zk, self_contained=False)


# def reload_note_after_program_exit(proc: subprocess.Popen, nid):
#     print(f"Waiting for {proc.pid} to terminate")
#     proc.wait(timeout=60*30)
#     print(f"{proc.pid} terminated, reloading note")
#     jekyll_dir = get_jekyll_home_from_env() / "pages"
#     jekyll_converter.convert_write(zk[nid], path=jekyll_dir / zk[nid].path.name)
#     print(f"Updated {nid}")


@app.route("/open/<program>/<zid>")
def open_external(program, zid):
    path = zk[zid].path
    if program == "typora":
        print("Opening typora")
        proc = subprocess.Popen(["typora", path])
        # threading.Thread(target=lambda: reload_note_after_program_exit(proc, zid)).start()
        return redirect(f"/open/{zid}")
    else:
        return "Invalid program"


@app.route("/dashboard")
def dashboard():
    plots = [make_link_histogram(), make_backlink_histogram()]
    plots = [components(plot) for plot in plots]
    scripts, divs = list(zip(*plots))
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    max_depth = max(zk.get_nnotes_by_depth().keys())
    table_data = [
        (f"Number of notes", f"{len(zk._nid2note)}"),
        (f"Number of links", f"{zk._graph.size()}"),
        (f"Links/note", f"{zk._graph.size()/len(zk._nid2note):.2f}"),
        (f"Number of tags", f"{len(zk.tags)}"),
        (f"Number of orphans", f"{len(zk.get_orphans())} "),
        (f"Maximum depth", f"{max_depth}")
    ]
    table = tabulate.tabulate(table_data, tablefmt="html")

    return render_template(
        'dashboard.html',
        scripts=scripts,
        divs=divs,
        js_resources=js_resources,
        css_resources=css_resources,
        table=table
    )


def interactive_int_histogram(
        data,
        bins,
        title,
        x_axis_label,
        x_tooltip
):
    """Plot interactive histogram using bokeh.

    Adapted from https://gist.github.com/bhishanpdl/43f5ddad264c1a712979ddc63dd3d6ee

    df: pandas dataframe
    col: column of panda dataframe to plot (eg. age of users)
    n_bins: number of bins, e.g. 9
    bin_range: list with min and max value. e.g. [10,100] age of users.
    title: title of plot. e.g. 'Airnb Users Age Distribution'
    x_axis_label: x axis label. e.g. 'Age (years)'.
    x_tooltip: x axis tooltip string. e.g. 'Age'

    """
    import pandas as pd
    import numpy as np
    from bokeh.plotting import figure

    from bokeh.models import ColumnDataSource, HoverTool

    arr_hist, edges = np.histogram(data, bins=bins)

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


def make_link_histogram():
    data = [len(note.links) for note in zk.notes]
    bins = [i -0.5 for i in range(20)]
    plot = interactive_int_histogram(
        data,
        bins=bins,
        title="Links per note",
        x_axis_label="Links per note",
        x_tooltip="Links per note"
    )

    return plot


def make_backlink_histogram():
    backlinks = collections.defaultdict(int)
    for note in zk.notes:
        for link in note.links:
            backlinks[link] += 1
    data = list(backlinks.values())
    bins = [i -0.5 for i in range(20)]
    plot = interactive_int_histogram(
        data,
        bins=bins,
        title="Backlinks per note",
        x_axis_label="Backlinks per note",
        x_tooltip="Backlinks per note"
    )

    return plot

def depth_histogram():
    data = zk.get_nnotes_by_depth()



# todo: search with program
# todo: fulltext search as an option
@app.route("/search/<search>")
def search(search):
    # Split any extensions
    search = Path(search).stem
    results = zk.search(search)
    if len(results) == 1:
        return redirect(f"/open/{results[0].nid}")
    elif len(results) > 1:
        out = "<ul>"
        for result in results:
            out += f'<li><a href="/open/{result.nid}">{result.title} ({result.path.stem})</a></li>'
        out += "</ul>"
        return out
    else:
        return "No results"


@app.route("/lucky/<search>")
def search_lucky(search):
    search = Path(search).stem
    if search.startswith("."):
        logger.debug(f"Redirecting to {search[1:]}")
        # e.g. allows access the dashboard with .dashboard
        return redirect(f"/{search[1:]}")
    results = zk.search(search)
    if results:
        return redirect(f"/open/{results[0].nid}")
    else:
        return "No results"


@app.route("/open/<notespec>")
def open(notespec: str):
    logger.debug(f"Opening {notespec}")
    if notespec.isnumeric():
        note = zk[notespec]
    else:
        note = zk.get_by_path(notespec)
    converted = pandoc_converter.convert(note)
    dot = "".join(dotgraph_html(zk, note))
    return render_template(
        "page.html",
        pandoc_output=converted,
        title=note.title,
        dot=dot,
    )


@app.route("/open/")
@app.route("/")
def root():
    return open(zk.root)


@app.route("/assets/<path>")
def asset(path: str):
    realpath = Path("_site") / "assets" / path
    print(path, realpath)
    return app.send_static_file(str(realpath))


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run()
