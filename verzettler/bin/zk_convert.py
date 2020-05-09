#!/usr/bin/env python3

# std
# from typing import Tuple, Any

# ours
from verzettler.cli_util import init_zk_from_cli
from verzettler.note_converter import JekyllConverter
from verzettler.zettelkasten import Zettelkasten
from verzettler.util import get_jekyll_home_from_env


def cli():
    zk, _ = init_zk_from_cli()  # type: Zettelkasten
    t = JekyllConverter()
    jekyll_dir = get_jekyll_home_from_env() / "pages"
    if jekyll_dir is None:
        raise ValueError("Need to set jekyll dir in environment variables")
    zk.apply_converter(t, output_basedir=jekyll_dir)


if __name__ == "__main__":
    cli()
