#!/usr/bin/env python3

# std
import os
from typing import List, Union, Optional, Iterable
from pathlib import Path, PurePath

# ours
from verzettler.zettel import Zettel


class Zettelkasten(object):

    def __init__(self, zettels: Optional[List[Zettel]] = None):
        self.zid2zettel = {}

        if zettels is not None:
            self.add_zettels(zettels)

    @property
    def zettels(self):
        return list(self.zid2zettel.values())

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

    def dot_graph(self) -> str:
        lines = [
            "digraph zettelkasten {",
            "\tnode [shape=box];"
        ]
        drawn_links = []
        for zettel in self.zettels:
            lines.append(
                f'\t{zettel.zid} ['
                f'label="{zettel.title}" '
                f'labelURL="file://{zettel.path}"'
                f'];'
            )
            for link in zettel.links:
                if (zettel.zid, link) in drawn_links:
                    continue
                if zettel.zid not in self.zid2zettel[link].links:
                    lines.append(f"\t{zettel.zid} -> {link};")
                    drawn_links.append((zettel.zid, link))
                else:
                    lines.append(f"\t{zettel.zid} -> {link} [dir=both];")
                    drawn_links.extend(
                        [(zettel.zid, link), (link, zettel.zid)]
                    )

        lines.append("}")
        return "\n".join(lines)

    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettelkasten({len(self.zid2zettel)})"
