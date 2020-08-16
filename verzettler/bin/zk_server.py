#!/usr/bin/env python3

# std
import subprocess
import logging
from pathlib import Path

# 3rd
from flask import Flask
from flask import render_template, redirect
from bokeh.embed import components
from bokeh.resources import INLINE
import tabulate

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util.paths import get_zk_base_dirs_from_env
from verzettler.log import logger
from verzettler.note_converter import PandocConverter, dotgraph_html
from verzettler.bokeh_plots import (
    make_backlink_histogram,
    make_link_histogram,
    depth_histogram,
    zk_name_pie_chart,
)


templates = Path(__file__).resolve().parent.parent / "templates"
statics = Path(__file__).resolve().parent.parent / "static"


app = Flask(
    __name__, template_folder=str(templates), static_folder=str(statics)
)
app.config["SECRET_KEY"] = "asfnfl1232#"

# https://stackoverflow.com/questions/9508667/reload-flask-app-when-template-file-changes
app.config["TEMPLATES_AUTO_RELOAD"] = True

zk = Zettelkasten()
for d in get_zk_base_dirs_from_env():
    zk.add_notes_from_directory(d)

# jekyll_converter = JekyllConverter(zk=zk)
pandoc_converter = PandocConverter(zk=zk, self_contained=False)


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
    plots = [
        make_link_histogram(zk=zk),
        make_backlink_histogram(zk=zk),
        depth_histogram(zk=zk),
        zk_name_pie_chart(zk=zk),
    ]
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
        (f"Maximum depth", f"{max_depth}"),
    ]
    table = tabulate.tabulate(table_data, tablefmt="html")

    return render_template(
        "dashboard.html",
        scripts=scripts,
        divs=divs,
        js_resources=js_resources,
        css_resources=css_resources,
        table=table,
    )


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
        "page.html", pandoc_output=converted, title=note.title, dot=dot,
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


def main():
    app.logger.setLevel(logging.DEBUG)
    app.run()


if __name__ == "__main__":
    main()
