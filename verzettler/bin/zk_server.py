#!/usr/bin/env python3

# std
import subprocess
import logging
from pathlib import Path
import threading

# 3rd
from flask import Flask
from flask import render_template, redirect
from bokeh.plotting import figure, output_file, save
from bokeh.embed import components
import numpy as np
from bokeh.resources import INLINE

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env
from verzettler.log import logger
from verzettler.note_converter import PandocConverter


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
    plots = [make_link_histogram()]
    scripts, divs = list(zip(*plots))
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    return render_template('dashboard.html', scripts=scripts, divs=divs, js_resources=js_resources, css_resources=css_resources,)


def make_link_histogram():
    plot = figure(plot_height=300, plot_width=800)  # sizing_mode='scale_width'

    data = [len(note.links) for note in zk.notes]
    bins = [i -0.5 for i in range(20)]
    hist, edges = np.histogram(data, density=False, bins=bins)

    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color="white")

    # output_file("test.html")
    # save(plot)

    script, div = components(plot)

    return script, div


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
    # jekyll_html_path = Path("_site") / "pages" / (name + ".html")
    # https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
    # todo: return app.send_static_file('index.html')
    # return render_template(str(jekyll_html_path))
    return render_template("page.html", pandoc_output=pandoc_converter.convert(note))


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
