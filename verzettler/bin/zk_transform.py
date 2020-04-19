#!/usr/bin/env python3

# ours
from verzettler.cli_util import init_zk_from_cli
from verzettler.note_transformer import DefaultTransformer


def cli():
    zk, _ = init_zk_from_cli()
    t = DefaultTransformer(zk=zk)
    for z in zk.zettels:
        t.transform_write(z)


if __name__ == "__main__":
    cli()
