#!/usr/bin/env python3

# std
import argparse
import subprocess
from pathlib import Path
import readline

# 3rd

# ours
from verzettler.cli_util import get_zk_dirs_from_cli


def cli():
    def add_additional_argparse_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            dest="search",
            help="Search term",
        )

    args = get_zk_dirs_from_cli(
        additional_argparse_setup=add_additional_argparse_arguments
    )

    sb_params = ["find", ]
    for d in args.input:
        sb_params.append(str(d))
    sb_params.extend(["-type", "f", "-not", "-wholename", "*/.git*", "-name", f"*{args.search}*"])

    opt = subprocess.check_output(
        sb_params,
        universal_newlines=True,
    ).strip()
    if not opt.replace("\n", ""):
        print("", end="")
    else:
        results = [Path(path_str) for path_str in opt.split("\n")]
        if len(results) == 1:
            print(results[0])
        else:
            for i, r in enumerate(results):
                print(f"{i: 3}", r.name)

            def completer(text, state):
                options = [r.name for r in results if text in r.name]
                if state < len(options):
                    return options[state]
                else:
                    return None

            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
            selection = input("Your selection: ")
            if selection.isnumeric():
                print(results[int(selection)])
            else:
                selection = [r for r in results if r.name == selection]
                assert len(selection) == 1
                print(selection[0])

if __name__ == "__main__":
    cli()
