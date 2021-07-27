#!/usr/bin/env python3

# std
from pathlib import Path
import argparse
from typing import Set

# ours
from verzettler.cli_util import init_zk_from_cli


def cli():
    def add_additional_argparse_arguments(parser: argparse.ArgumentParser):
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
            "-n",
            "--notes",
            nargs="+",
            help="The note that should be transformed.",
        )

    zk, args = init_zk_from_cli(
        additional_argparse_setup=add_additional_argparse_arguments
    )

    def tag_transformer(tags: Set[str]) -> Set[str]:
        tags = tags.copy()
        tags |= set(args.add)
        tags -= set(args.remove)
        return tags

    for path in args.notes:
        path = Path(path).resolve()
        z = zk.get_by_path(path)
        # fixme
        z.transform_file(tag_transformer=tag_transformer)


if __name__ == "__main__":
    cli()
