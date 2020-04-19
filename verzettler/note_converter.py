#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import PurePath, Path

# ours
from verzettler.zettel import Zettel
from verzettler.markdown_reader import MarkdownReader


class NoteConverter(ABC):
    """ Takes a zettel and transforms underlying markdown file
    """

    @abstractmethod
    def convert(self, zettel: Zettel) -> str:
        pass

    def convert_write(self, zettel: Zettel, path: Optional[PurePath] = None):
        if path:
            path = Path(path)
        else:
            path = zettel.path
        with path.open("w") as outf:
            outf.write(self.convert(zettel))


class JekyllConverter(NoteConverter):

    def convert(self, zettel: Zettel) -> str:
        out_lines = [
            "---\n",
            "layout: page\n",
            f"title: \"{zettel.title}\"\n",
            "exclude: true\n",  # do not add to menu
            "---\n",
        ]
        md_reader = MarkdownReader.from_file(zettel.path)
        for i, md_line in enumerate(md_reader.lines):
            remove_line = False
            if not md_line.is_code_block:
                if md_line.text.startswith("# "):
                    # Already set the title with meta info
                    remove_line = True

            # Replace raw zids, leave only links
            md_line.text = zettel.id_link_regex.sub("", md_line.text)

            # Replace links to md with links to html
            md_line.text = zettel.markdown_link_regex.sub(
                r"[\1](\2.html)",
                md_line.text
            )

            if not remove_line:
                out_lines.append(md_line.text)

        return "".join(out_lines)

# def to_html(self):
#     try:
#         subprocess.run(
#             ["pandoc", "-t", "html", "-s", "-c", ""]
#         )

