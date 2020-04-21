#!/usr/bin/env python3

# std
import os
from typing import List, Union, Optional, Iterable, Set, Dict
from pathlib import Path, PurePath

# 3rd
import networkx as nx

# ours
from verzettler.note import Note
from verzettler.log import logger
from verzettler.nodecolorpicker import ConstantNodeColorPicker, NodeColorPicker


class Zettelkasten(object):

    def __init__(self, zettels: Optional[List[Note]] = None):
        self.mother = "00000000000000"
        self._zid2zettel = {}  # type: Dict[str, Note]
        self._graph = nx.DiGraph()
        if zettels is not None:
            self.add_zettels(zettels)

        self._finalized = False  # todo: remove

    # Properties
    # =========================================================================

    @property
    def notes(self):
        return list(self._zid2zettel.values())

    @property
    def tags(self) -> Set[str]:
        tags = set()
        for z in self.notes:
            tags |= z.tags
        return tags

    @property
    def categories(self) -> Set[str]:
        return set(t for t in self.tags if t.startswith("c_"))

    # todo: should be done with networkx
    @property
    def depth(self) -> int:
        maxdepth = 0
        for z in self.notes:
            if z.depth is not None:
                maxdepth = max(z.depth, maxdepth)
        return maxdepth

    # Graph functions
    # =========================================================================

    def get_backlinks(self, zid):
        return list(self._graph.predecessors(zid))

    def get_depth(self, zid) -> int:
        try:
            return nx.dijkstra_path_length(self._graph, self.mother, zid)
        except nx.NetworkXError:
            return 0

    # Getting things
    # =========================================================================

    def get_by_path(self, path: Union[str, PurePath]) -> Note:
        path = Path(path)
        # fixme
        res = [z for z in self.notes if z.path.name == path.name]
        assert len(res) == 1, (path.name, res)
        return res[0]

    # Extending collection
    # =========================================================================

    def add_zettels(self, notes: Iterable[Note]) -> None:
        self._finalized = False
        for note in notes:
            note.zettelkasten = self
            self._zid2zettel[note.nid] = note
            self._graph.add_node(note.nid)
            for link in note.links:
                self._graph.add_edge(note.nid, link)

    def add_notes_from_directory(
            self,
            directory: Union[PurePath, str]
    ) -> None:
        self._finalized = False
        directory = Path(directory)
        for root, dirs, files in os.walk(str(directory), topdown=True):
            dirs[:] = [d for d in dirs if d not in [".git"]]
            self.add_zettels(
                [
                    Note(Path(root) / file)
                    for file in files
                    if file.endswith(".md")
                ]
            )

    # MISC
    # =========================================================================

    def dot_graph(self, color_picker: Optional[NodeColorPicker] = None) -> str:
        lines = [
            "digraph zettelkasten {",
            "\tnode [shape=box];"
        ]

        if color_picker is None:
            color_picker = ConstantNodeColorPicker()

        drawn_links = []
        for note in self.notes:
            lines.append(
                f'\t{note.nid} ['
                f'label="{note.title} ({note.depth})" '
                f'labelURL="file://{note.path.resolve()}" '
                f'color="{color_picker.pick(note)}"'
                f'];'
            )
            for link in note.links:
                if link not in self:
                    logger.error(f"Didn't find note with id {link}.")
                    continue
                if (note.nid, link) in drawn_links:
                    continue
                if note.nid not in self._zid2zettel[link].links:
                    lines.append(f'\t{note.nid} -> {link} [color="black"];')
                    drawn_links.append((note.nid, link))
                else:
                    lines.append(f'\t{note.nid} -> {link} [color="black" dir="both"];')
                    drawn_links.extend(
                        [(note.nid, link), (link, note.nid)]
                    )

        lines.append("}")
        return "\n".join(lines)

    def stats_string(self) -> str:
        lines = [
            f"Total number of notes: {len(self._zid2zettel)}",
            f"Total number of tags: {len(self.tags)}",
        ]
        return "\n".join(lines)

    # Magic
    # =========================================================================

    # todo: provide get method that allows to only warn if not found or something
    def __getitem__(self, item):
        return self._zid2zettel[item]

    def __contains__(self, item):
        return item in self._zid2zettel

    def __repr__(self):
        return f"Zettelkasten({len(self._zid2zettel)})"
