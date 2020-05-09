#!/usr/bin/env python3

# std
import subprocess
import logging

# 3rd
from flask import Flask

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asfnfl1232#'


zk = Zettelkasten()
for d in get_zk_base_dirs_from_env():
    zk.add_notes_from_directory(d)


@app.route("/open/<program>/<zid>")
def open_external(program, zid):
    path = zk[zid].path
    if program == "typora":
        print("Opening typora")
        subprocess.Popen(["typora", path])


@app.route("/search/<search>")
def search(search):
    results = [zettel for zettel in zk if search in zettel.name or zettel.title]
    if len(results) == 1:
        pass


@app.route("open/<zid>")
def open(zid):
    path = zk[zid].path


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run()
