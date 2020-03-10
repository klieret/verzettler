#!/usr/bin/env python3

# std
import os
from abc import ABC, abstractmethod
from typing import List, Union, Optional, Iterable, Set
from pathlib import Path, PurePath

# ours
from verzettler.zettel import Zettel


class ColorPicker(ABC):

    @abstractmethod
    def pick(self, zettel: Zettel):
        pass


class CategoryColorPicker(ColorPicker):

    def __init__(
            self,
            zettelkasten: "Zettelkasten",
            colors: Optional[List[str]] = None
    ):

        self.zettelkasten = zettelkasten
        if colors is None:
            colors = [
                "#8dd3c7",
                "#ffffb3",
                "#bebada",
                "#fb8072",
                "#80b1d3",
                "#fdb462",
                "#b3de69",
                "#fccde5",
                "#d9d9d9",
                "#bc80bd",
                "#ccebc5",
                "#ffed6f",
            ]

        self.category2color = {
            c: colors[i % len(colors)]
            for i, c in enumerate(self.zettelkasten.categories)
        }

    def pick(self, zettel: Zettel):
        categories = [t for t in zettel.tags if t.startswith("c_")]
        if len(categories) != 1:
            # unfortunately vis.js doesn't support multiple colors
            return "white"
        else:
            return ":".join([self.category2color[c] for c in categories])


class ConstantColorPicker(ColorPicker):

    def __init__(self, color= "#8dd3c7"):
        self.color = color

    def pick(self, zettel: Zettel):
        return self.color


class Zettelkasten(object):

    def __init__(self, zettels: Optional[List[Zettel]] = None):
        self.zid2zettel = {}

        if zettels is not None:
            self.add_zettels(zettels)

    # Properties
    # =========================================================================

    @property
    def zettels(self):
        return list(self.zid2zettel.values())

    @property
    def tags(self) -> Set[str]:
        tags = set()
        for z in self.zettels:
            tags |= z.tags
        return tags

    @property
    def categories(self) -> Set[str]:
        return set(t for t in self.tags if t.startswith("c_"))

    # Extending collection
    # =========================================================================

    def add_zettels(self, zettels: Iterable[Zettel]) -> None:
        for zettel in zettels:
            self.zid2zettel[zettel.zid] = zettel

    def add_zettels_from_directory(
            self,
            directory: Union[PurePath, str]
    ) -> None:
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

    def dot_graph(self, color_picker: Optional[ColorPicker] = None) -> str:
        lines = [
            "digraph zettelkasten {",
            "\tnode [shape=box];"
        ]

        if color_picker is None:
            color_picker = ConstantColorPicker()

        drawn_links = []
        for zettel in self.zettels:
            lines.append(
                f'\t{zettel.zid} ['
                f'label="{zettel.title}" '
                f'labelURL="file://{zettel.path}" '
                f'color={color_picker.pick(zettel)}'
                f'];'
            )
            for link in zettel.links:
                if (zettel.zid, link) in drawn_links:
                    continue
                if zettel.zid not in self.zid2zettel[link].links:
                    lines.append(f"\t{zettel.zid} -> {link} [color=black];")
                    drawn_links.append((zettel.zid, link))
                else:
                    lines.append(f"\t{zettel.zid} -> {link} [color=black dir=both];")
                    drawn_links.extend(
                        [(zettel.zid, link), (link, zettel.zid)]
                    )

        lines.append("}")
        return "\n".join(lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettelkasten({len(self.zid2zettel)})"
