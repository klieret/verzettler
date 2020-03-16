#!/usr/bin/env python3

# std
import re
from typing import List, Optional, Union, Set, Iterable, Set
from pathlib import Path, PurePath
import os.path


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

    def analyze_file(self) -> None:
        self.links = []
        self.existing_backlinks = []
        backlinks_section = False
        with self.path.open() as inf:
            for line in inf.readlines():
                if line.startswith("# ") and not self.title:
                    # Careful, because '# something' can also appear in a
                    # code block
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
        is_code_block = False
        current_section = []
        with self.path.open() as inf:
            lastline = None
            for line in inf.readlines():
                if line.startswith("```"):
                    is_code_block = not is_code_block

                # Fixing
                if is_code_block and "tags: " in line.lower():
                    if not lastline.strip():
                        out_lines = out_lines[:-1]
                    continue

                # Change style of headers
                if not is_code_block and line.startswith("==="):
                    out_lines = out_lines[:-1]
                    line = "# " + lastline
                if not is_code_block and line.startswith("---"):
                    out_lines = out_lines[:-1]
                    line = "## " + lastline

                # Set current section
                sm = self.section_regex.match(line)
                if not is_code_block and sm:
                    level = len(sm.group(1))-1
                    text = sm.group(2)
                    current_section = current_section[:level]
                    current_section.append(text)

                # Modifying tags if haven't been given before
                if not self.tags:
                    if lastline is not None and lastline.startswith("# ") and not is_code_block:
                        tags = tag_transformer(set())
                        if tags:
                            out_lines.extend([
                                "\n",
                                self._format_tags(tags),
                            ])

                # Modifying tags if already given
                if "tags: " in line.lower() and not is_code_block:
                    tags = tag_transformer(self._read_tags(line))
                    if not tags:
                        # Remove line
                        continue
                    line = self._format_tags(tags)

                # Replacing/extending links

                # Remove old autogenerated links
                line = self.autogen_link_regex.sub("", line)

                # Add new links
                links = self.id_link_regex.findall(line)
                for link in links:
                    zid = self.id_regex.findall(link)
                    assert len(zid) == 1
                    zid = zid[0]
                    new_links = self._format_link(zid)
                    line = line.replace(link, new_links)

                out_lines.append(line)
                lastline = line
        with self.path.open("w") as outf:
            outf.writelines(out_lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.zid})"
