#!/usr/bin/env python3

# std
from pathlib import Path
import argparse
import sys

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env
from verzettler.log import logger


def format_dot_html(dot_str: str) -> str:
    html_resource_dir = Path(__file__).parent.resolve().parent / "html_resources"
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
        help="Input directories of the zettelkastens. If left blank, will try"
             " to set from ZK_HOME environment variable. "
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output html file",
        default="out.html"
    )
    args = parser.parse_args()
    if not args.input:
        args.input = get_zk_base_dirs_from_env()
    if not args.input:
        logger.critical(
            "Zettelkasten input directories were neither specified by command "
            "line, nor set in the ZK_HOME environment variable. Exit. "
        )
        sys.exit(111)

    zk = Zettelkasten()
    for inpt_dir in args.input:
        zk.add_zettels_from_directory(inpt_dir)
    with open(args.output, "w") as outf:
        outf.write(format_dot_html(zk.dot_graph()))


if __name__ == "__main__":
    cli()
