#!/usr/bin/env python3

# ours
from verzettler.cli_util import init_zk_from_cli


def cli():
    zk, _ = init_zk_from_cli()
    zk.transform_all()


if __name__ == "__main__":
    cli()
