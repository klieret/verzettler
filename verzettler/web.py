#!/usr/bin/env python3

# std
from pathlib import Path
import sys

# ours
from verzettler.zettelkasten import Zettelkasten


def format_dot_html(dot_str: str) -> str:
    html_resource_dir = Path(__file__).parent.resolve() / "html_resources"
    js_path = html_resource_dir / "vis-network.min.js"
    html_path = html_resource_dir / "dot.html"
    dot_str = dot_str.replace("'", "\\'")
    dot_str = dot_str.replace("\n", "' + \n'")
    with open(html_path) as html_file:
        html = "\n".join(html_file.readlines())
        html = html.replace("{js_path}", str(js_path.resolve()))
        html = html.replace("{dotgraph}", dot_str)
    return html


if __name__ == "__main__":
    zk = Zettelkasten()
    zk.add_zettels_from_directory(sys.argv[1])
    zk.transform_all()
    with open(sys.argv[2], "w") as outf:
        outf.write(format_dot_html(zk.dot_graph()))
