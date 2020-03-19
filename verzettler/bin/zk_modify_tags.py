#!/usr/bin/env python3

# std
from pathlib import Path
import argparse
from typing import Set
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
    parser.add_argument(
        "-r",
        "--remove",
        nargs="+",
        help="Remove tags",
        default=set(),
    )
    parser.add_argument(
        "-a",
        "--add",
        nargs="+",
        help="Add tags",
        default=set(),
    )
    parser.add_argument(
        "-z",
        "--zettel",
        nargs="+",
        help="The zettel that should be transformed.",
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

    def tag_transformer(tags: Set[str]) -> Set[str]:
        tags = tags.copy()
        tags |= set(args.add)
        tags -= set(args.remove)
        return tags

    for path in args.zettel:
        path = Path(path).resolve()
        z = zk.get_by_path(path)
        z.transform_file(tag_transformer=tag_transformer)


if __name__ == "__main__":
    cli()
