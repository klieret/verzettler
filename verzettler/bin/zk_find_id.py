#!/usr/bin/env python3

# std
import argparse

# 3rd
import pyperclip

# ours
import verzettler.cli_util as cli_util
from verzettler.bin.zk_open import get_search_results
from verzettler.bin.zk_get_id import get_id


def cli():
    parser = argparse.ArgumentParser()
    cli_util.add_zk_dirs_arg(parser)
    cli_util.add_debug_args(parser)
    parser.add_argument(
        dest="search",
        help="Search term",
    )
    args = parser.parse_args()
    cli_util.default_arg_handling(args)
    results = get_search_results(
        search_dirs=args.input, search_term=args.search
    )
    selection = cli_util.get_path_selection(results, search=args.search)
    if not selection:
        return
    else:
        zid = get_id(selection.name)
        pyperclip.copy(zid)
        print(zid)


if __name__ == "__main__":
    cli()
