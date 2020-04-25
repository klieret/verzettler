#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import PurePath, Path

# ours
from verzettler.note import Note
from verzettler.markdown_reader import MarkdownReader


class NoteConverter(ABC):
    """ Takes a note and transforms underlying markdown file
    """

    @abstractmethod
    def convert(self, note: Note) -> str:
        pass

    def convert_write(self, note: Note, path: Optional[PurePath] = None):
        if path:
            path = Path(path)
        else:
            path = note.path
        with path.open("w") as outf:
            outf.write(self.convert(note))


class JekyllConverter(NoteConverter):

    def convert(self, note: Note) -> str:
        out_lines = [
            "---\n",
            "layout: page\n",
            f"title: \"{note.title}\"\n",
            "exclude: true\n",  # do not add to menu
            "---\n",
        ]
        md_reader = MarkdownReader.from_file(note.path)
        for i, md_line in enumerate(md_reader.lines):
            remove_line = False
            if not md_line.is_code_block:
                if md_line.text.startswith("# "):
                    # Already set the title with meta info
                    remove_line = True

            # Replace raw zids, leave only links
            md_line.text = note.id_link_regex_no_group.sub("", md_line.text)

            # Replace links to md with links to html
            md_line.text = note.markdown_link_regex.sub(
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

