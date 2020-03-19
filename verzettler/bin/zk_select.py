#!/usr/bin/env python3

# std
import argparse
import subprocess
from pathlib import Path
import readline
from typing import List

# 3rd

# ours
from verzettler.cli_util import \
    get_zk_dirs_from_cli, get_n_terminal_rows, get_path_selection


def get_search_results(
        search_dirs: List[Path],
        search_term: str
) -> List[Path]:
    sb_params = ["find", ]
    for d in search_dirs:
        sb_params.append(str(d))
    sb_params.extend(["-type", "f", "-not", "-wholename", "*/.git*", "-name",
                      f"*{search_term}*"])

    opt = subprocess.check_output(
        sb_params,
        universal_newlines=True,
    ).strip()

    if not opt.replace("\n", ""):
        return []

    return [Path(path_str) for path_str in opt.split("\n")]


def cli():
    def add_additional_argparse_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            dest="search",
            help="Search term",
        )

    args = get_zk_dirs_from_cli(
        additional_argparse_setup=add_additional_argparse_arguments
    )

    results = get_search_results(
        search_dirs=args.input,
        search_term=args.search
    )

    selection = get_path_selection(results)
    if selection:
        print(selection)


if __name__ == "__main__":
    cli()
