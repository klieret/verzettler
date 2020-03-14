#!/usr/bin/env python3

# std
import argparse

# ours
from verzettler.zettelkasten import Zettelkasten


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="Input directories of the zettelkastens."
    )
    args = parser.parse_args()
    zk = Zettelkasten()
    for inpt_dir in args.input:
        zk.add_zettels_from_directory(inpt_dir)
    zk.transform_all()


if __name__ == "__main__":
    cli()
