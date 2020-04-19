#!/usr/bin/env python3

# std
import os
from typing import List, Union, Optional, Iterable, Set, Dict
from pathlib import Path, PurePath

# 3rd
import networkx as nx

# ours
from verzettler.zettel import Zettel
from verzettler.log import logger
from verzettler.nodecolorpicker import ConstantNodeColorPicker, NodeColorPicker


class Zettelkasten(object):

    def __init__(self, zettels: Optional[List[Zettel]] = None):
        self.mother = "00000000000000"
        self._zid2zettel = {}  # type: Dict[str, Zettel]
        self._graph = nx.DiGraph()
        if zettels is not None:
            self.add_zettels(zettels)

        self._finalized = False  # todo: remove

    # Properties
    # =========================================================================

    @property
    def zettels(self):
        return list(self._zid2zettel.values())

    @property
    def tags(self) -> Set[str]:
        tags = set()
        for z in self.zettels:
            tags |= z.tags
        return tags

    @property
    def categories(self) -> Set[str]:
        return set(t for t in self.tags if t.startswith("c_"))

    # todo: should be done with networkx
    @property
    def depth(self) -> int:
        maxdepth = 0
        for z in self.zettels:
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

    def get_by_path(self, path: Union[str, PurePath]) -> Zettel:
        path = Path(path)
        # fixme
        res = [z for z in self.zettels if z.path.name == path.name]
        assert len(res) == 1, (path.name, res)
        return res[0]

    # Extending collection
    # =========================================================================

    def add_zettels(self, zettels: Iterable[Zettel]) -> None:
        self._finalized = False
        for zettel in zettels:
            zettel.zettelkasten = self
            self._zid2zettel[zettel.zid] = zettel
            self._graph.add_node(zettel.zid)
            for link in zettel.links:
                self._graph.add_edge(zettel.zid, link)

    def add_zettels_from_directory(
            self,
            directory: Union[PurePath, str]
    ) -> None:
        self._finalized = False
        directory = Path(directory)
        for root, dirs, files in os.walk(str(directory), topdown=True):
            dirs[:] = [d for d in dirs if d not in [".git"]]
            self.add_zettels(
                [
                    Zettel(Path(root) / file)
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
        for zettel in self.zettels:
            lines.append(
                f'\t{zettel.zid} ['
                f'label="{zettel.title} ({zettel.depth})" '
                f'labelURL="file://{zettel.path.resolve()}" '
                f'color="{color_picker.pick(zettel)}"'
                f'];'
            )
            for link in zettel.links:
                if link not in self:
                    logger.error(f"Didn't find zettel with zid {link}.")
                    continue
                if (zettel.zid, link) in drawn_links:
                    continue
                if zettel.zid not in self._zid2zettel[link].links:
                    lines.append(f'\t{zettel.zid} -> {link} [color="black"];')
                    drawn_links.append((zettel.zid, link))
                else:
                    lines.append(f'\t{zettel.zid} -> {link} [color="black" dir="both"];')
                    drawn_links.extend(
                        [(zettel.zid, link), (link, zettel.zid)]
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
