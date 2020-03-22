#!/usr/bin/env python3

# std
import argparse
import sys
from typing import Callable, Tuple, List, Optional
import os
import readline
from pathlib import PurePath
import logging

# 3rd
from termcolor import colored

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env, pass_fct
from verzettler.log import logger


def add_debug_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--log",
        help="Level of the log: 'd' (debug), 'i' (info), 'w' (warning), "
             "'e' (error), 'c' (critical).",
        default="i",
        choices=list("diwec"),
    )


def add_zk_dirs_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input directories of the zettelkastens. If left blank, will try"
             " to set from ZK_HOME environment variable. "
    )


def default_arg_handling(args: argparse.Namespace) -> None:
    if hasattr(args, "input"):
        if not args.input:
            args.input = get_zk_base_dirs_from_env()
            logger.debug(f"Got zk directories {args.input} from env.")
        if not args.input:
            logger.critical(
                "Zettelkasten input directories were neither specified by "
                "command line, nor set in the ZK_HOME environment variable. "
                "Exit. "
            )
            sys.exit(111)
    if hasattr(args, "log"):
        abbrev2loglevel = {
            "d": logging.DEBUG,
            "i": logging.INFO,
            "w": logging.WARNING,
            "e": logging.ERROR,
            "c": logging.CRITICAL,
        }
        logger.setLevel(abbrev2loglevel[args.log])


def init_zk_from_cli(additional_argparse_setup: Callable = pass_fct) \
        -> Tuple[Zettelkasten, argparse.Namespace]:
    parser = argparse.ArgumentParser()
    add_zk_dirs_arg(parser)
    add_debug_args(parser)
    additional_argparse_setup(parser)
    args = parser.parse_args()
    default_arg_handling(args)

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
    results.sort(key=lambda p: p.name)
    if not results:
        return None
    elif len(results) == 1:
        return results[0]

    max_n = max(5, get_n_terminal_rows() - 5)
    for i, r in enumerate(results):
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
