#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set, Iterable, Set
from pathlib import Path, PurePath
import os.path


def identity(arg):
    return arg


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

    # Parsing and formatting
    # =========================================================================

    @staticmethod
    def _format_tags(tags: Iterable[str]) -> str:
        return "Tags: " + " ".join("#"+tag for tag in tags)

    def _read_tags(self, line: str) -> Set[str]:
        return set(
            t[1:] for t in set(self.tag_regex.findall(line))
        )

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
                    self.tags = self._read_tags(line)
                elif line.startswith("##") and "backlinks" in line.lower():
                    backlinks_section = True
                if backlinks_section:
                    self.existing_backlinks.extend(self.id_regex.findall(line))
                else:
                    self.links.extend(self.id_regex.findall(line))

    # Modify file
    # =========================================================================

    def transform_file(self, tag_transformer=identity) -> None:
        out_lines = []
        with self.path.open() as inf:
            lastline = None
            for line in inf.readlines():

                # Modifying tags if haven't been given before
                if not self.tags:
                    if lastline is not None and lastline.startswith("# "):
                        out_lines.extend([
                            "",
                            self._format_tags(tag_transformer(set())),
                            ""
                        ])

                # Modifying tags if already given
                if "tags: " in line.lower():
                    tags = tag_transformer(self._read_tags(line))
                    line = self._format_tags(tags)

                # Replacing/extending links
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
                lastline = line
        with self.path.open("w") as outf:
            outf.writelines(out_lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.get_zid})"
