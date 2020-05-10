#!/usr/bin/env python3

# std
import subprocess
import logging
from pathlib import Path
import threading

# 3rd
from flask import Flask
from flask import render_template, redirect

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env, get_jekyll_home_from_env
from verzettler.log import logger
from verzettler.note_converter import JekyllConverter


jekyll_home = get_jekyll_home_from_env()
if jekyll_home is None:
    raise ValueError("Jekyll home not found!")
logger.debug(f"Jekyll home is {jekyll_home}")

app = Flask(__name__, template_folder=jekyll_home, static_folder=jekyll_home)
app.config['SECRET_KEY'] = 'asfnfl1232#'

# https://stackoverflow.com/questions/9508667/reload-flask-app-when-template-file-changes
app.config['TEMPLATES_AUTO_RELOAD'] = True

zk = Zettelkasten()
for d in get_zk_base_dirs_from_env():
    zk.add_notes_from_directory(d)

jekyll_converter = JekyllConverter(zk=zk)


def reload_note_after_program_exit(proc: subprocess.Popen, nid):
    print(f"Waiting for {proc.pid} to terminate")
    proc.wait(timeout=60*30)
    print(f"{proc.pid} terminated, reloading note")
    jekyll_dir = get_jekyll_home_from_env() / "pages"
    jekyll_converter.convert_write(zk[nid], path=jekyll_dir / zk[nid].path.name)
    print(f"Updated {nid}")


@app.route("/open/<program>/<zid>")
def open_external(program, zid):
    path = zk[zid].path
    if program == "typora":
        print("Opening typora")
        proc = subprocess.Popen(["typora", path])
        threading.Thread(target=lambda: reload_note_after_program_exit(proc, zid)).start()
        return redirect(f"/open/{zid}")
    else:
        return "Invalid program"


@app.route("/search/<search>")
def search(search):
    # Split any extensions
    search = Path(search).stem
    results = [note for note in zk.notes if search in note.path.name or search in note.title or search in note.path.name.replace("_", " ")]
    if len(results) == 1:
        return open(results[0].nid)
    elif len(results) > 1:
        out = "<ul>"
        for result in results:
            out += f'<li><a href="/open/{result.nid}">{result.title} ({result.path.stem})</a></li>'
        out += "</ul>"
        return out
    else:
        return "No results"


@app.route("/open/<notespec>")
def open(notespec: str):
    if notespec.isnumeric():
        name = zk[notespec].path.stem
    else:
        name = Path(notespec).stem
    jekyll_html_path = Path("_site") / "pages" / (name + ".html")
    return render_template(str(jekyll_html_path))


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
