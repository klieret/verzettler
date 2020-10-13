#!/usr/bin/env python3

# std
from pathlib import Path
import argparse
import sys

# ours
from verzettler.cli_util import init_zk_from_cli
from verzettler.zettelkasten import Zettelkasten
from verzettler.log import logger
from verzettler.dotgraphgenerator import DotGraphGenerator


def format_dot_html(dot_str: str) -> str:
    html_resource_dir = (
        Path(__file__).parent.resolve().parent / "html_resources"
    )
    js_resource_dir = (
        Path(__file__).parent.resolve().parent / "static/js/"
    )
    js_path = js_resource_dir / "vis-network.min.js"
    html_path = html_resource_dir / "dot.html"
    dot_str = dot_str.replace("'", "\\'")
    dot_str = dot_str.replace("\n", "' + \n'")
    with open(html_path) as html_file:
        html = "\n".join(html_file.readlines())
        html = html.replace("{js_path}", str(js_path.resolve()))
        html = html.replace("{dotgraph}", dot_str)
    return html


def _get_dot(zk: Zettelkasten):
    return DotGraphGenerator(zk=zk).graph_from_notes(
        list(map(lambda n: n.nid, zk.notes))
    )


def _output_html(zk: Zettelkasten, path: Path) -> None:
    with path.open("w") as outf:
        outf.write(format_dot_html(_get_dot(zk)))


def _output_dot(zk: Zettelkasten, path: Path) -> None:
    with path.open("w") as outf:
        outf.write(_get_dot(zk=zk))


output_format_to_converter = {".html": _output_html, ".dot": _output_dot}


def cli():
    def add_additional_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-o",
            "--output",
            help=f"Output file. The following file formats are "
            f"supported: {', '.join(output_format_to_converter.keys())}.",
            default="out.html",
        )

    zk, args = init_zk_from_cli(
        additional_argparse_setup=add_additional_arguments
    )
    args.output = Path(args.output)
    try:
        output_format_to_converter[args.output.suffix](zk, args.output)
    except KeyError:
        logger.critical(f"Unsupported suffix: {args.output.suffix}")
        sys.exit(86)


if __name__ == "__main__":
    cli()
