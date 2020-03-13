#!/usr/bin/env python3

# std
import sys

# ours
from verzettler.zettelkasten import Zettelkasten


def add_backlinks():
    pass


if __name__ == "__main__":
    zk = Zettelkasten()
    zk.add_zettels_from_directory(sys.argv[1])

