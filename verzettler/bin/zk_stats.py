#!/usr/bin/env python3

# std

# ours
from verzettler.cli_util import init_zk_from_cli


def cli():
    zk, _ = init_zk_from_cli()
    print(zk.stats_string())


if __name__ == "__main__":
    cli()
