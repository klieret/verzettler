#!/usr/bin/env python3

# std
from pathlib import Path
import argparse

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


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input directories of the zettelkastens."
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output html file"
    )
    args = parser.parse_args()
    zk = Zettelkasten()
    for inpt_dir in args.input:
        zk.add_zettels_from_directory(inpt_dir)
    # todo: should that really be here?
    zk.transform_all()
    with open(args.output, "w") as outf:
        outf.write(format_dot_html(zk.dot_graph()))


if __name__ == "__main__":
    cli()
