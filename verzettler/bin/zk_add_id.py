#!/usr/bin/env python3

# std
import argparse
from pathlib import Path, PurePath
import shutil

# ours
import verzettler.cli_util as cli_util
from verzettler.bin.zk_get_id import get_id
from verzettler.bin.zk_touch import generate_zid
from verzettler.log import logger


def add_id(path: PurePath) -> PurePath:
    zid = get_id(path.name)
    if zid == "none":
        zid = generate_zid()
        if path.name.endswith(".md"):
            name = path.name[:-3] + zid + ".md"
        else:
            name = path.name + zid + ".md"
        return path.parent / name
    elif zid == "many":
        logger.critical(
            f"Already found MULTIPLE ids in {path}. " f"Leaving unchanged"
        )
        return path
    else:
        logger.warning(f"Already found ID in {path}. " f"Leaving unchanged.")


def cli():
    parser = argparse.ArgumentParser()
    cli_util.add_zk_dirs_arg(parser)
    cli_util.add_debug_args(parser)
    parser.add_argument(dest="file",)
    args = parser.parse_args()
    new_path = add_id(args.file)
    shutil.move(args.file, str(new_path))


if __name__ == "__main__":
    cli()
