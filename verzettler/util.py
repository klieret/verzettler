#!/usr/bin/env python3

# std
from typing import List, Optional
from pathlib import Path
import shlex
import os

# ours
from verzettler.log import logger


def get_zk_base_dirs_from_env() -> List[Path]:
    if "ZK_HOME" in os.environ:
        paths = [
            Path(path_str) for path_str in shlex.split(os.environ["ZK_HOME"])
        ]
        existing_paths = []
        for path in paths:
            if not path.is_dir():
                logger.warning(
                    f"Path '{path}' from ZK_HOME environment variable doesn't"
                    f"exist. Ignoring it."
                )
            else:
                existing_paths.append(path)
        return existing_paths


def get_jekyll_home_from_env() -> Optional[Path]:
    if "ZK_JEKYLL_HOME" in os.environ:
        path = Path(os.environ["ZK_JEKYLL_HOME"])
        path.mkdir(parents=True, exist_ok=True)
        return path


def pass_fct(*args, **kwargs):
    pass


def remove_duplicates(lst: List) -> List:
    return list(dict.fromkeys(lst))


def test_remove_duplicates():
    assert ["a"] == remove_duplicates(["a", "a", "a"])
    assert ["a", "b"] == remove_duplicates((["a", "b", "a", "a", "b"]))