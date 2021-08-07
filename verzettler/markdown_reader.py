#!/usr/bin/env ptyhon3

# std
from typing import List, Union
from pathlib import Path, PurePath
import re


class MarkdownLine(object):
    def __init__(
        self,
        text,
        is_code_block,
        current_section,
        is_last_line,
    ):
        self.text = text
        self.is_code_block = is_code_block
        self.current_section = current_section
        self.is_last_line = is_last_line


class MarkdownReader(object):
    _section_regex = re.compile(r"(#+)\s+(.+)")

    def __init__(self, lines: List[MarkdownLine]):
        self.lines = lines

    @classmethod
    def from_file(cls, path: Union[str, PurePath]) -> "MarkdownReader":
        path = Path(path)
        with path.open() as inf:
            lines = inf.readlines()
        return MarkdownReader.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: List[str]) -> "MarkdownReader":
        md_lines = []
        is_code_block = False
        current_section = []
        for i, line in enumerate(lines):
            is_last_line = i == len(lines) - 1

            # ATX style headings
            sm = cls._section_regex.match(line)
            if not is_code_block and sm:
                level = len(sm.group(1)) - 1
                text = sm.group(2).strip()
                current_section = current_section[:level]
                current_section.append(text)

            # Underline headings
            if (
                not is_last_line
                and set(lines[i + 1]) == {"="}
                and len(lines[i + 1]) >= 3
            ):
                current_section = [line]
            elif (
                not is_last_line
                and set(lines[i + 1]) == {"-"}
                and len(lines[i + 1]) >= 3
                and len(current_section) >= 1
            ):
                current_section = [current_section[0], line]

            md_lines.append(
                MarkdownLine(
                    text=line,
                    is_code_block=is_code_block,
                    current_section=current_section,
                    is_last_line=is_last_line,
                )
            )

            # Result should apply to next iteration only, since ``` is part of
            # the block.
            if line.startswith("```"):
                is_code_block = not is_code_block

        return MarkdownReader(md_lines)

    def __iter__(self):
        return iter(self.lines)
