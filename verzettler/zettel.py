#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set
from pathlib import Path, PurePath


class Zettel(object):

    id_regex = re.compile("[0-9]{14}")
    tag_regex = re.compile(r"#\S*")

    def __init__(self, path: Path):
        self.path = path
        self.zid = self.get_zid(path)  # type: str

        self.links = []  # type: List[str]
        self.existing_backlinks = []  # type: List[str]
        self.title = ""
        self.tags = set()  # type: Set[str]

        self.depth = None  # type: Optional[int]

        self.analyze_file()

    # Class methods
    # =========================================================================

    @classmethod
    def get_zid(cls, path: Union[str, PurePath]) -> str:
        """ Zettel ID"""
        path = PurePath(path)
        matches = cls.id_regex.findall(path.name)
        if matches:
            return matches[0]
        else:
            return path.name

    # Analyze file
    # =========================================================================

    def analyze_file(self) -> None:
        """ Links from file """
        self.links = []
        self.existing_backlinks = []
        backlinks_section = False
        with self.path.open() as inf:
            for line in inf.readlines():
                if line.startswith("# "):
                    self.title = line.split("# ")[1].strip()
                elif "tags: " in line.lower():
                    self.tags = set(
                        t[1:] for t in set(self.tag_regex.findall(line))
                    )
                elif line.startswith("##") and "backlinks" in line.lower():
                    backlinks_section = True
                if backlinks_section:
                    self.existing_backlinks.extend(self.id_regex.findall(line))
                else:
                    self.links.extend(self.id_regex.findall(line))

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.get_zid})"
