#!/usr/bin/env python3

# std
from typing import List
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


def pass_fct(*args, **kwargs):
    pass
