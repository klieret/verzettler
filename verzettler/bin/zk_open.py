#!/usr/bin/env python3

# std
import argparse
import subprocess
from pathlib import Path
from typing import List

# 3rd

# ours
from verzettler.cli_util import get_zk_dirs_from_cli, get_path_selection
from verzettler.log import logger


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
        parser.add_argument(
            "-a",
            "--action",
            help="Action to be executed with the search result. {file} will be "
                 "replaced with the search result. E.g. 'vim {file}' to open "
                 "the file in vim (make sure to use the single quotes to not "
                 "have your shell meddling). For convenience: "
                 "If '{file}' is not found in this "
                 "string, then '{file}' is appended, i.e. 'vim' is equivalent "
                 "to 'vim {file}'.",
            default="",
            type=str,
        )

    args = get_zk_dirs_from_cli(
        additional_argparse_setup=add_additional_argparse_arguments
    )

    results = get_search_results(
        search_dirs=args.input,
        search_term=args.search
    )

    selection = get_path_selection(results)
    if not selection:
        return
    elif not args.action:
        print(selection)
    else:
        if '{file}' not in args.action:
            args.action = args.action + " {file}"

        command = args.action.format(file=selection)
        logger.debug(f"Running in system: '{command}'")

        subprocess.run(command, shell=True)


if __name__ == "__main__":
    cli()
