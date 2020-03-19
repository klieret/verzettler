#!/usr/bin/env python3

# std
import argparse
import sys

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_zk_base_dirs_from_env
from verzettler.log import logger


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input directories of the zettelkastens. If left blank, will try"
             " to set from ZK_HOME environment variable. "
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
    zk.transform_all()


if __name__ == "__main__":
    cli()
