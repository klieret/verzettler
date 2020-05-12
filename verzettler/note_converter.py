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

    def __init__(self, zk):
        self.zk = zk

    def convert(self, note: Note) -> str:
        out_lines = [
            "---\n",
            "layout: page\n",
            f"title: \"{note.title}\"\n",
            "exclude: true\n",  # do not add to menu
            f"tags: {list(note.tags)}\n"
            "---\n",
        ]
        md_reader = MarkdownReader.from_file(note.path)
        for i, md_line in enumerate(md_reader.lines):

            if i == 1:
                out_lines.append(
                    f"[Open in typora](/open/typora/{note.nid})\n\n"
                )

            remove_line = False
            if not md_line.is_code_block:
                if md_line.text.startswith("# "):
                    # Already set the title with meta info
                    remove_line = True

            # Mark external links with a '*'
            md_line.text = note.external_link_regex.sub(
                r"[!\1](\2)",
                md_line.text
            )

            # Remove old markdown links
            md_line.text = note.autogen_link_regex.sub(
                "",
                md_line.text,
            )

            # Replace raw zids, leave only links
            nids = note.id_link_regex.findall(md_line.text)
            for nid in nids:
                n = self.zk[nid]
                title = n.title
                nid = n.nid
                md_line.text = md_line.text.replace(f"[[{nid}]]", f"[{title}](/open/{nid})")



            if not remove_line:
                out_lines.append(md_line.text)

        return "".join(out_lines)

# def to_html(self):
#     try:
#         subprocess.run(
#             ["pandoc", "-t", "html", "-s", "-c", ""]
#         )

