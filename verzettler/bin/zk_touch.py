#!/usr/bin/env python3

# std
import argparse
import datetime
from pathlib import Path, PurePath
from typing import Optional, Union
import os
import sys

# 3rd
import pyperclip

# ours
import verzettler.cli_util as cli_util
from verzettler.util.paths import get_zk_base_dirs_from_env
from verzettler.log import logger
from verzettler.bin.zk_open import add_action_option, handle_action_on_path
from verzettler.note import Note


def generate_zid() -> str:
    # todo: should be put at a central place
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def guess_zk_dir(inpt: Union[str, PurePath]) -> Optional[Path]:
    if Path(inpt).is_dir():
        return Path(inpt).resolve()
    else:
        dirs = get_zk_base_dirs_from_env()
        results = [d for d in dirs if inpt in str(d)]
        if len(results) == 0:
            logger.warning("Could not guess right zk directory.")
            return None
        elif len(results) == 1:
            logger.debug(
                f"Guessed zk directory from search term {inpt} to be "
                f"{results[0]}.")
            return Path(results[0])
        else:
            logger.warning("Too many results for zk directory.")
            return None


def cli():
    parser = argparse.ArgumentParser()
    cli_util.add_debug_args(parser)
    parser.add_argument(
        "-d",
        "--dir",
        help="Path to zettelkasten directory or. Search term for zettelkasten"
             " directory (e.g. part of path).",
        required=False
    )
    parser.add_argument(
        dest="name",
        help="Name",
    )
    add_action_option(parser)
    args = parser.parse_args()
    cli_util.default_arg_handling(args)
    if args.dir:
        args.dir = guess_zk_dir(args.dir)
        if not args.dir:
            logger.critical("Could not find unique zk directory. Exit.")
            sys.exit(117)
    else:
        args.dir = Path(os.getcwd())
    new_path = args.dir / f"{args.name}_{generate_zid()}.md"
    logger.debug(f"Touching {new_path.resolve()}")
    new_path.touch()
    logger.info(f"Created {new_path.resolve()}.")
    if not args.action:
        pyperclip.copy(str(new_path.resolve()))
        logger.info(f"Path has been copied to clipboard.")
    else:
        handle_action_on_path(args.action, new_path)
        pyperclip.copy(Note.get_nid(new_path))
        logger.info(f"ID has been copied to clipboard.")


if __name__ == "__main__":
    cli()
