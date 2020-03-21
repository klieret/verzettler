#!/usr/bin/env python3

# std
import argparse
import sys
from typing import Callable, Tuple, List, Optional
import os
import readline
from pathlib import PurePath

# 3rd
from termcolor import colored

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env, pass_fct
from verzettler.log import logger


def get_zk_dirs_from_cli(additional_argparse_setup: Callable = pass_fct) \
        -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input directories of the zettelkastens. If left blank, will try"
             " to set from ZK_HOME environment variable. "
    )
    additional_argparse_setup(parser)
    args = parser.parse_args()
    if not args.input:
        args.input = get_zk_base_dirs_from_env()
    if not args.input:
        logger.critical(
            "Zettelkasten input directories were neither specified by command "
            "line, nor set in the ZK_HOME environment variable. Exit. "
        )
        sys.exit(111)
    return args


def init_zk_from_cli(additional_argparse_setup: Callable = pass_fct) \
        -> Tuple[Zettelkasten, argparse.Namespace]:
    args = get_zk_dirs_from_cli(
        additional_argparse_setup=additional_argparse_setup
    )

    zk = Zettelkasten()
    for inpt_dir in args.input:
        zk.add_zettels_from_directory(inpt_dir)

    return zk, args


def get_n_terminal_rows() -> int:
    try:
        return os.get_terminal_size(0)[1]
    except OSError:
        return os.get_terminal_size(1)[1]


def set_path_autocompleter(results: List[PurePath]) -> None:
    def completer(text, state):
        options = [r.name for r in results if text in r.name]
        if state < len(options):
            return options[state]
        else:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")


def get_path_selection(results: List[PurePath]) -> Optional[PurePath]:
    if not results:
        return None
    elif len(results) == 1:
        return results[0]

    max_n = max(5, get_n_terminal_rows() - 5)
    for i, r in enumerate(sorted(results, key=lambda p: p.name)):
        print(colored(f"{i: 3}", "yellow"), r.name)
        if i > max_n:
            print(colored("... Rest omitted", "red"))
            break
    set_path_autocompleter(results)
    selection = input(colored("Your selection: ", attrs=["bold"]))
    if selection.isnumeric():
        return results[int(selection)]
    else:
        res = [r for r in results if selection in r.name]
        if not len(res) == 1:
            print(
                colored(
                    "Your selection was not unique. Go again!",
                    "red",
                    attrs=["bold"]
                )
            )
            return get_path_selection(results)
        return res[0]
