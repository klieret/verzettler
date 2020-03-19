#!/usr/bin/env python3

# std
import argparse
import sys
from typing import Callable, Tuple

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
