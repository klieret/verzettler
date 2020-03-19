#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set, Iterable, Set
from pathlib import Path, PurePath
import os.path

# ours
from verzettler.markdown_reader import MarkdownReader

def identity(arg):
    return arg


class Zettel(object):

    id_regex = re.compile("(?<=[^0-9])[0-9]{14}(?=[^0-9])")
    id_link_regex = re.compile(r"\[\[[0-9]{14}\]\]")
    tag_regex = re.compile(r"#\S*")
    autogen_link_regex = re.compile(r" *\[[^\]]*\]\([^)\"]* \"autogen\"\)")
    section_regex = re.compile(r"(#+)\s+(.+)")

    def __init__(self, path: Path, zettelkasten=None):
        self.path = path
        self.zid = self.get_zid(path)  # type: str

        self.links = []  # type: List[str]
        self._existing_backlinks = []  # type: List[str]
        self.title = ""
        self.tags = set()  # type: Set[str]

        # Gets set by ZK
        self.depth = None  # type: Optional[int]
        # Gets set by ZK
        self.backlinks = None  # type: Optional[Set[str]]

        self.zettelkasten = zettelkasten

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

    @staticmethod
    def _format_tags(tags: Iterable[str]) -> str:
        return "Tags: " + " ".join("#"+tag for tag in sorted(list(tags))) + "\n"

    def _read_tags(self, line: str) -> Set[str]:
        return set(
            t[1:] for t in set(self.tag_regex.findall(line))
        )

    def _format_link(self, zid: str) -> str:
        rel_path = Path(
            os.path.relpath(
                str(self.zettelkasten[zid].path),
                str(self.path.parent))
        )
        link_title = self.zettelkasten[zid].title
        return f"[[{zid}]] [{link_title}]({rel_path} \"autogen\")"

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
                self._existing_backlinks.extend(self.id_regex.findall(md_line.text))
            else:
                self.links.extend(self.id_regex.findall(md_line.text))

    # Modify file
    # =========================================================================

    def transform_file(self, tag_transformer=identity) -> None:
        out_lines = []

        md_reader = MarkdownReader.from_file(self.path)
        for i, md_line in enumerate(md_reader.lines):
            remove_line = False

            # Fixing
            if md_line.is_code_block and "tags: " in md_line.text.lower():
                if i >= 1 and not md_reader.lines[i-1].text.strip():
                    out_lines = out_lines[:-1]
                continue

            # Change style of headers
            if not md_line.is_code_block and md_line.text.startswith("==="):
                out_lines = out_lines[:-1]
                md_line.text = "# " + md_reader.lines[i-1].text
            if not md_line.is_code_block and md_line.text.startswith("---"):
                out_lines = out_lines[:-1]
                md_line.text = "## " + md_reader.lines[i-1].text

            # Modifying tags if haven't been given before
            if not self.tags:
                if i >= 1 and md_reader.lines[i-1].text.startswith("# ") \
                        and not md_line.is_code_block:
                    tags = tag_transformer(set())
                    if tags:
                        out_lines.extend([
                            "\n",
                            self._format_tags(tags),
                        ])

            # Modifying tags if already given
            if "tags: " in md_line.text.lower() and not md_line.is_code_block:
                tags = tag_transformer(self._read_tags(md_line.text))
                if not tags:
                    # Remove line
                    continue
                md_line.text = self._format_tags(tags)

            # Replacing/extending links

            # Remove old autogenerated links
            md_line.text = self.autogen_link_regex.sub("", md_line.text)

            # Add new links
            links = self.id_link_regex.findall(md_line.text)
            for link in links:
                zid = self.id_regex.findall(link)
                assert len(zid) == 1
                zid = zid[0]
                new_links = self._format_link(zid)
                md_line.text = md_line.text.replace(link, new_links)

            # Remove old backlinks section
            if len(md_line.current_section) == 2 and \
                    md_line.current_section[-1].lower() == "backlinks":
                remove_line = True

            # Add lines
            if not remove_line:
                out_lines.append(md_line.text)

            # Add new blacklinks section to file
            if md_line.is_last_line and self.backlinks:
                if len(out_lines) >= 1 and out_lines[-1] == "\n":
                    pass
                elif len(out_lines) >= 1 and out_lines[-1].endswith("\n"):
                    out_lines.extend(["\n"])
                elif len(out_lines) >= 1 and not out_lines[-1].endswith("\n"):
                    out_lines.extend(["\n", "\n"])
                out_lines.extend(["## Backlinks\n", "\n"])
                for backlink in sorted(list(self.backlinks)):
                    out_lines.append(f"* {self._format_link(backlink)}\n")

        with self.path.open("w") as outf:
            outf.writelines(out_lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.zid})"
