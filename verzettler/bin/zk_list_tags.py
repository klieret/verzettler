#!/usr/bin/env python3

# ours
from verzettler.cli_util import init_zk_from_cli


def cli():
    zk, _ = init_zk_from_cli()
    tags = sorted(list(zk.tags))
    for t in tags:
        print(t)


if __name__ == "__main__":
    cli()
