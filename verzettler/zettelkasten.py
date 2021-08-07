#!/usr/bin/env python3

# std
import re
import os
from typing import List, Union, Optional, Iterable, Set, Dict, Any
from pathlib import Path, PurePath
from functools import lru_cache
import collections

# 3rd
import networkx as nx

# ours
from verzettler.note import Note
from verzettler.log import logger
from verzettler.note_converter import NoteConverter
from verzettler.util.paths import remove_duplicates

# Methods as functions defined here for better caching

_sentinel = object()


def _iterator_empty(iterator):
    return next(iterator, _sentinel) is _sentinel


@lru_cache(maxsize=100)
def _get_orphans(g: nx.DiGraph):
    return [node for node in g.nodes if _iterator_empty(g.predecessors(node))]


@lru_cache(maxsize=100)
def _get_tags(notes: Iterable[Note]) -> Set[str]:
    tags = set()
    for z in notes:
        tags |= z.tags
    return tags


@lru_cache(maxsize=100)
def _count_tags(notes: Iterable[Note]) -> Dict[str, int]:
    tag_counts = collections.defaultdict(int)
    for n in notes:
        for tag in n.tags:
            tag_counts[tag] += 1
    return tag_counts


def _get_depth(g: nx.DiGraph, root, node: Any, errvalue=0):
    try:
        return nx.dijkstra_path_length(g, root, node)
    except nx.NetworkXNoPath:
        return errvalue


@lru_cache(maxsize=100)
def _get_notes_by_depth(g: nx.DiGraph, root) -> Dict[int, Set[Any]]:
    nbd = collections.defaultdict(set)
    for node in g.nodes:
        nbd[_get_depth(g=g, root=root, node=node)].add(node)
    return nbd


@lru_cache(maxsize=1000)
def _get_k_neighbors(g: nx.DiGraph, root, k=1):
    return [
        node
        for node in g.nodes
        if 1 <= _get_depth(g, root=root, node=node) <= k
    ]


@lru_cache(maxsize=100)
def _get_root(g: nx.DiGraph) -> str:
    return min(g.nodes)


class Zettelkasten(object):
    def __init__(self, zettels: Optional[List[Note]] = None):
        self._nid2note = {}  # type: Dict[str, Note]
        self._graph = nx.DiGraph()
        if zettels is not None:
            self.add_notes(zettels)

    # Properties
    # =========================================================================

    @property
    def root(self):
        return _get_root(self._graph)

    @property
    def notes(self):
        return list(self._nid2note.values())

    @property
    def tags(self) -> Set[str]:
        return _get_tags(self._nid2note.values())

    @property
    def tag_counts(self) -> Dict[str, int]:
        return _count_tags(self._nid2note.values())

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
    # Mostly a facade around networkx
    # =========================================================================

    def _nids2notes(self, nids: Iterable[str]) -> Set[Note]:
        # todo: warn if problems
        return set(self[nid] for nid in nids if nid in self)

    def get_backlinks(self, nid):
        return list(self._graph.predecessors(nid))

    def get_depth(self, nid) -> int:
        return _get_depth(g=self._graph, node=nid, root=self.root)

    def get_orphans(self) -> Set[Note]:
        return set(
            self[nid]
            for nid in _get_orphans(self._graph)
            if not nid == self.root
        )

    def get_notes_by_depth(self, root=None):
        """

        Args:
            root: If none: Master document

        Returns:

        """
        if root is None:
            root = self.root
        return {
            depth: self._nids2notes(nids)
            for depth, nids in _get_notes_by_depth(
                g=self._graph, root=root
            ).items()
        }

    def get_nnotes_by_depth(self, root=None):
        if root is None:
            root = self.root
        return {
            depth: len(nids)
            for depth, nids in _get_notes_by_depth(
                g=self._graph, root=root
            ).items()
        }

    def get_neighbors(self, nid, k=1):
        return self._nids2notes(_get_k_neighbors(g=self._graph, k=k, root=nid))

    def get_ndescendants(self, nid):
        return len(nx.descendants(self._graph, nid))

    # Getting things
    # =========================================================================

    def get_by_path(self, path: Union[str, PurePath]) -> Note:
        path = Path(path)
        # fixme
        res = [z for z in self.notes if z.path.name == path.name]
        assert len(res) == 1, (path.name, res)
        return res[0]

    def search(self, search: str) -> List[Note]:
        """Search. By default we will search in titles and in names.

        Args:
            search:

        Returns:

        """
        # Important to keep search results in order

        if Note.id_regex.match(search):
            return [self._nid2note[search]]

        n_search = search.replace(" ", "_")
        t_search = search.replace("_", " ")

        if set(search) & {"*", "^", "$"}:
            name_search_regexp = re.compile(n_search)
            title_search_regexp = re.compile(t_search)
            return remove_duplicates(
                [
                    note
                    for note in self.notes
                    if name_search_regexp.match(note.path.name)
                    or title_search_regexp.match(note.title)
                ]
            )

        # Keep the order
        results = []
        results.extend(
            [
                note
                for note in self.notes
                if Note.id_regex.sub("", note.path.stem)
                .replace("_", " ")
                .strip()
                == t_search
                or note.title == t_search
            ]
        )
        results.extend(
            [
                note
                for note in self.notes
                if note.path.stem.startswith(n_search)
                or note.title.startswith(t_search)
            ]
        )
        results.extend(
            [
                note
                for note in self.notes
                if n_search in note.path.stem or t_search in note.title
            ]
        )

        print([r.path.name for r in remove_duplicates(results)])

        return remove_duplicates(results)

    # Extending collection
    # =========================================================================

    def add_notes(self, notes: Iterable[Note]) -> None:
        for note in notes:
            note.zettelkasten = self
            self._nid2note[note.nid] = note
            self._graph.add_node(note.nid)
            for link in note.links:
                self._graph.add_edge(note.nid, link)

    def add_notes_from_directory(self, directory: Union[PurePath, str]) -> None:
        directory = Path(directory)
        for root, dirs, files in os.walk(str(directory), topdown=True):
            dirs[:] = [d for d in dirs if d not in [".git"]]
            notes = [
                Note(Path(root) / file)
                for file in files
                if file.endswith(".md")
            ]
            if notes:
                self.add_notes(notes)
                logger.info(f"Added {len(notes)} notes from {root}")

    # MISC
    # =========================================================================

    def reload_note(self, nid: str):
        del self._nid2note[nid]
        self._graph.remove_node(nid)
        self.add_notes([Note(self[nid].path)])

    def stats_string(self) -> str:
        lines = [
            f"Number of notes: {len(self._nid2note)}",
            f"Number of tags: {len(self.tags)}",
            f"Number of orphans: {len(self.get_orphans())} ",
            f"Number of links: {self._graph.size()}",
        ]
        return "\n".join(lines)

    def apply_converter(
        self, converter: NoteConverter, output_basedir: Union[str, PurePath]
    ):
        """Apply converter to all notes in Zettelkasten. The target path for
        each note will be output_basedir/filename.

        Args:
            converter:
            output_basedir:

        Returns:

        """
        output_basedir = Path(output_basedir)
        output_basedir.parent.mkdir(exist_ok=True, parents=True)
        for note in self.notes:
            new_path = output_basedir / note.path.name
            converter.convert_write(note, path=new_path)

    # Magic
    # =========================================================================

    # todo: provide get method that allows to only warn if not found or something
    def __getitem__(self, item):
        return self._nid2note[item]

    def __contains__(self, item):
        return item in self._nid2note

    def __repr__(self):
        return f"Zettelkasten({len(self._nid2note)})"

    def __len__(self):
        return len(self._nid2note)
