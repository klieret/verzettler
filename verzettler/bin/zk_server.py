#!/usr/bin/env python3

# std
import subprocess
import logging
from pathlib import Path

# 3rd
from flask import Flask
from flask import render_template

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env, get_jekyll_home_from_env
from verzettler.log import logger


jekyll_home = get_jekyll_home_from_env()
if jekyll_home is None:
    raise ValueError("Jekyll home not found!")
logger.debug(f"Jekyll home is {jekyll_home}")

app = Flask(__name__, template_folder=jekyll_home, static_folder=jekyll_home)
app.config['SECRET_KEY'] = 'asfnfl1232#'
# Disable caching https://stackoverflow.com/questions/34066804/
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


zk = Zettelkasten()
for d in get_zk_base_dirs_from_env():
    zk.add_notes_from_directory(d)


@app.route("/open/<program>/<zid>")
def open_external(program, zid):
    path = zk[zid].path
    if program == "typora":
        print("Opening typora")
        subprocess.Popen(["typora", path])
        return open(zid)
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
        return ", ".join([result.path.name for result in results])
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


@app.route("/assets/<path>")
def asset(path: str):
    realpath = Path("_site") / "assets" / path
    print(path, realpath)
    return app.send_static_file(str(realpath))


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run()
