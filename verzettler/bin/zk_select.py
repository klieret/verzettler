#!/usr/bin/env python3

# std
import argparse
import subprocess
from pathlib import Path
import readline
from typing import List

# 3rd

# ours
from verzettler.cli_util import get_zk_dirs_from_cli


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


def set_autocompleter(results):
    def completer(text, state):
        options = [r.name for r in results if text in r.name]
        if state < len(options):
            return options[state]
        else:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")


def get_selection(results):
    if not results:
        return None
    elif len(results) == 1:
        return results[0]

    for i, r in enumerate(results):
        print(f"{i: 3}", r.name)
    set_autocompleter(results)
    selection = input("Your selection: ")
    if selection.isnumeric():
        return results[int(selection)]
    else:
        res = [r for r in results if r.name == selection]
        if not len(res) == 1:
            print("Your selection was not unique. Go again")
            return get_selection(results)
        return res[0]


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

    selection = get_selection(results)
    if selection:
        print(selection)


if __name__ == "__main__":
    cli()
