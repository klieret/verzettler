#!/usr/bin/env python3

# std
from pathlib import Path
import argparse

# ours
from verzettler.cli_util import init_zk_from_cli


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

    def add_additional_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-o",
            "--output",
            help="Output html file",
            default="out.html"
        )

    zk, args = init_zk_from_cli(additional_argparse_setup=add_additional_arguments)
    with open(args.output, "w") as outf:
        outf.write(format_dot_html(zk.dot_graph()))


if __name__ == "__main__":
    cli()
