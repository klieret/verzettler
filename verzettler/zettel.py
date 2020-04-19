#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set
from pathlib import Path, PurePath

# ours
from verzettler.markdown_reader import MarkdownReader



class Zettel(object):

    id_regex = re.compile("(?<=[^0-9])[0-9]{14}(?=[^0-9])")
    id_link_regex = re.compile(r"\[\[[0-9]{14}\]\]")
    tag_regex = re.compile(r"#\S*")
    autogen_link_regex = re.compile(r" *\[[^\]]*\]\([^)\"]* \"autogen\"\)")
    markdown_link_regex = re.compile(r"\[([^\]]*)\]\(([^)]*).md(\s\".*\")*\)")
    section_regex = re.compile(r"(#+)\s+(.+)")

    def __init__(self, path: Path):
        self.path = path
        self.zid = self.get_zid(path)  # type: str

        self.links = []  # type: List[str]
        self.title = ""
        self.tags = set()  # type: Set[str]

        # Gets set by ZK  # todo: remove
        self.depth = None  # type: Optional[int]

        self._analyze_file()

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

    # Parsing and formatting helper functions
    # =========================================================================

    def _read_tags(self, line: str) -> Set[str]:
        return set(
            t[1:] for t in set(self.tag_regex.findall(line))
        )

    # Analyze file
    # =========================================================================

    def _analyze_file(self) -> None:
        """ Should be called only once! """

        md_reader = MarkdownReader.from_file(self.path)
        for md_line in md_reader.lines:
            if len(md_line.current_section) == 1:
                if self.title and self.title != md_line.current_section[0]:
                    # todo: form
                    print(f"{self.path} Warning: Multiple titles. ")
                self.title = md_line.current_section[0]
            if not md_line.is_code_block and md_line.text.lower().strip().startswith("tags: "):
                if self.tags:
                    # todo: form
                    print(f"{self.path} Warning: Tags were already set.")
                self.tags = self._read_tags(md_line.text)
            if len(md_line.current_section) >= 2 and \
                    md_line.current_section[1].lower().strip() == "backlinks":
                pass
            else:
                self.links.extend(self.id_regex.findall(md_line.text))

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.zid})"
