#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional, List

# 3rd
from colour import Color

# ours
from verzettler.note import Note

class NodeColorPicker(ABC):

    @abstractmethod
    def pick(self, note: Note):
        pass


class CategoryNodeColorPicker(NodeColorPicker):

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

    def pick(self, note: Note):
        categories = [t for t in note.tags if t.startswith("c_")]
        if len(categories) != 1:
            # unfortunately vis.js doesn't support multiple colors
            return "white"
        else:
            return ":".join([self.category2color[c] for c in categories])


class ConstantNodeColorPicker(NodeColorPicker):

    def __init__(self, color= "#8dd3c7"):
        self.color = color

    def pick(self, note: Note):
        return self.color


# fixme
class DepthNodeColorPicker(NodeColorPicker):

    def __init__(self, zettelkasten: "Zettelkasten", start_color="#f67280", end_color="#fff7f8"):
        self.colors = list(
            Color(start_color).range_to(Color(end_color), zettelkasten.depth)
        )

    def pick(self, note: Note) -> str:
        if note.depth:
            return self.colors[note.depth - 1]
        else:
            return self.colors[0]
