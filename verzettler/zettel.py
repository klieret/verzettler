#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set
from pathlib import Path, PurePath
import os.path


class Zettel(object):

    id_regex = re.compile("[0-9]{14}")
    id_link_regex = re.compile(r"\[\[[0-9]{14}\]\]")
    tag_regex = re.compile(r"#\S*")
    autogen_link_regex = re.compile(r" *\[[^\]]*\]\([^)\"]* \"autogen\"\)")

    def __init__(self, path: Path, zettelkasten=None):
        self.path = path
        self.zid = self.get_zid(path)  # type: str

        self.links = []  # type: List[str]
        self.existing_backlinks = []  # type: List[str]
        self.title = ""
        self.tags = set()  # type: Set[str]

        self.depth = None  # type: Optional[int]

        self.zettelkasten = zettelkasten

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

    def transform_file(self) -> None:
        out_lines = []
        with self.path.open() as inf:
            for line in inf.readlines():
                line = self.autogen_link_regex.sub("", line)
                links = self.id_link_regex.findall(line)
                for link in links:
                    zid = self.id_regex.findall(link)
                    assert len(zid) == 1
                    zid = zid[0]
                    rel_path = Path(
                        os.path.relpath(
                            str(self.zettelkasten[zid].path),
                            str(self.path.parent))
                    )
                    link_title = self.zettelkasten[zid].title
                    new_links = f"[[{zid}]] [{link_title}]({rel_path} \"autogen\")"
                    line = line.replace(link, new_links)
                out_lines.append(line)
        with self.path.open("w") as outf:
            outf.writelines(out_lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.get_zid})"
