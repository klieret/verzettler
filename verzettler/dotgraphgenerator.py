#!/usr/bin/env python3

# std
from typing import List

# ours
from verzettler.note import Note
from verzettler.log import logger



class DotGraphGenerator(object):
    def __init__(self, zk):
        self.prologue = [
            "digraph zettelkasten {",
            "\tnode [shape=box];"
            "\tedge [splits=true];"  # todo: not working yet
        ]
        self.epilogue = [
            "}"
        ]
        self.zk = zk

    def graph_from_notes(self, nids: List[str]):
        lines = []
        lines.extend(self.prologue)
        drawn_links = []
        notes = self.zk._nids2notes(nids)
        for note in notes:
            lines.append(self.format_note(note))
            for link in note.links:
                if link not in nids:
                    continue

                if link not in self:
                    logger.error(f"Didn't find note with id {link}.")
                    continue
                if (note.nid, link) in drawn_links:
                    continue
                if note.nid not in self.zk._nid2note[link].links:
                    lines.append(f'\t{note.nid} -> {link} [color="black"];')
                    drawn_links.append((note.nid, link))
                else:
                    lines.append(f'\t{note.nid} -> {link} [color="black" dir="both"];')
                    drawn_links.extend(
                        [(note.nid, link), (link, note.nid)]
                    )
        lines.extend(self.prologue)
        return "\n".join(lines)

    def get_color(self, note: Note):
        return "blue"

    def get_fontsize(self, note: Note):
        return 14

    def format_note(self, note: Note):
        return f'\t{note.nid} [' \
            f'label="{note.title}" ' \
            f'labelURL="http://127.0.0.1:5000/open/{note.nid}" ' \
            f'color="{self.get_color(note)}"' \
            f'fontsize={self.get_fontsize(note)}' \
            f'];'

