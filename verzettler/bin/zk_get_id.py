#!/usr/bin/env python3

# std
from typing import List
import argparse

# ours
from verzettler.note import Note
import verzettler.cli_util as cli_util


def get_id(string: str) -> str:
    res = Note.id_regex.findall(string)
    if len(res) == 0:
        return "none"
    elif len(res) == 1:
        return res[0]
    else:
        return "many"


def get_ids(strings: List[str]) -> List[str]:
    return [get_id(string) for string in strings]


def printl(strlst: List[str]) -> None:
    for string in strlst:
        print(string)


def cli():
    parser = argparse.ArgumentParser()
    cli_util.add_zk_dirs_arg(parser)
    cli_util.add_debug_args(parser)
    parser.add_argument(
        dest="strings",
        nargs="+"
    )
    args = parser.parse_args()
    cli_util.default_arg_handling(args)
    printl(get_ids(args.strings))


if __name__ == "__main__":
    cli()
