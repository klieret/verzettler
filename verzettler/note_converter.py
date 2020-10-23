#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import PurePath, Path
import random
import subprocess
import collections
import re

# 3rd
import networkx as nx

# ours
from verzettler.note import Note
from verzettler.markdown_reader import MarkdownReader
from verzettler.log import logger
from verzettler.dotgraphgenerator import DotGraphGenerator
from verzettler.util.regex import find_urls


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


# nodes.widthConstraint: 50,

_dotgraph_html = """
<div id="mynetwork" style="width: 100%; height: {height};"></div>

<script type="text/javascript">
  let container = document.getElementById('mynetwork');
  let dot = `{dotgraph}`;
  let data = vis.parseDOTNetwork(dot);
  let options = {
    clickToUse: true,
  }
  let network = new vis.Network(container, data, options);
  network.on( 'click', function(properties) {
    let id = properties.nodes[0];
    let clickedNode = network.body.nodes[id];
    let url = clickedNode.options.labelURL;
    window.open(url);
  });
</script>
"""


def dotgraph_html(zk, note: Note):
    # nbd = self.zk.get_notes_by_depth(root=note.nid)
    # maxdepth = min(2, len(nbd))

    categories = collections.defaultdict(set)
    selected_nodes = {note.nid}  # self.zk._graph.get_k_neighbors(note.nid)
    categories["self"].add(note.nid)
    try:
        # selected_nodes |= set(nx.dijkstra_path(zk._graph, zk.root, note.nid))
        paths_from_root = set()
        for connection in nx.all_simple_paths(zk._graph, zk.root, note.nid):
            paths_from_root |= set(connection)
        categories["rootpath"] |= paths_from_root
        selected_nodes |= paths_from_root
    except nx.exception.NetworkXNoPath:
        logger.warning(f"No path from {zk.root} to {note.nid}")
    predecessors = set(zk._graph.predecessors(note.nid))
    categories["predecessors"] |= predecessors
    selected_nodes |= predecessors
    descendants = set(
        nx.descendants_at_distance(zk._graph, note.nid, distance=1)
    )
    categories["descendants"] |= descendants
    selected_nodes |= descendants
    optional_nodes = set()
    for dist in range(2, 3):
        desc = set(
            nx.descendants_at_distance(zk._graph, note.nid, distance=dist)
        )
        categories["descendants"] |= desc
        optional_nodes |= desc
    for predecessor in zk._graph.predecessors(note.nid):
        sibl = set(zk._graph.successors(predecessor))
        categories["siblings"] |= sibl
        optional_nodes |= sibl
    optional_nodes -= selected_nodes
    if len(selected_nodes) < 30:
        selected_nodes |= set(
            random.choices(
                list(optional_nodes),
                k=min(len(optional_nodes), 30 - len(selected_nodes)),
            )
        )

    def pick_color(note: Note):
        nid = note.nid
        if nid in categories["self"]:
            # red
            return "#fb8072"
        elif nid in categories["predecessors"]:
            # green
            return "#ccebc5"
        elif nid in categories["descendants"]:
            # yellow
            return "#ffed6f"
        elif nid in categories["siblings"]:
            # pink
            return "#fccde5"
        elif nid in categories["rootpath"]:
            # grayish
            return "#d9d9d9"
        else:
            return "red"

    out_lines = []
    if len(selected_nodes) < 50:
        out_lines.append(
            '<script src="/static/js/vis-network.min.js"></script>\n'
        )
        dgg = DotGraphGenerator(zk=zk)
        dgg.get_color = pick_color
        dotstr = dgg.graph_from_notes(selected_nodes)
        out_lines.append(
            _dotgraph_html.replace("{dotgraph}", dotstr).replace(
                "{height}", f"{400 + 20*len(selected_nodes)}px"
            )
        )
    return out_lines


class JekyllConverter(NoteConverter):

    # .replace("'", "\\'").replace("\n", "' + \n'")

    def __init__(self, zk):
        self.zk = zk

    def convert(self, note: Note) -> str:
        out_lines = [
            "---\n",
            "layout: page\n",
            f'title: "{note.title}"\n',
            "exclude: true\n",  # do not add to menu
            f"tags: {list(note.tags)}\n" "---\n",
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

                # Jekyll somehow eats my
                # '*' characters, causing problems with LaTeX.
                md_line.text = md_line.text.replace(r"^*", r"^\ast")
                md_line.text = md_line.text.replace(r"^{**", r"^{\ast\ast")
                md_line.text = md_line.text.replace(r"^{*", r"^{\ast")

            # Mark external links with a '*'
            md_line.text = note.external_link_regex.sub(
                r"[!\1](\2)", md_line.text
            )

            # Remove old markdown links
            md_line.text = note.autogen_link_regex.sub("", md_line.text,)

            # Replace raw zids, leave only links
            nids = note.id_link_regex.findall(md_line.text)
            for nid in nids:
                try:
                    n = self.zk[nid]
                    title = n.title
                    md_line.text = md_line.text.replace(
                        f"[[{nid}]]", f"[{title}](/open/{nid})"
                    )
                except KeyError:
                    logger.error(f"Couldn't find note {nid}")

            if not remove_line:
                out_lines.append(md_line.text)

        out_lines.extend(dotgraph_html(self.zk, note))

        return "".join(out_lines)


class PandocConverter(NoteConverter):
    def __init__(self, zk, self_contained=True):
        """

        Args:
            zk:
            self_contained: If true, let pandoc produce a full HTML page with
                CSS already included.
        """
        self.zk = zk
        self.self_contained = self_contained

    def preproc_markdown(self, note: Note) -> str:
        out_lines = []
        md_reader = MarkdownReader.from_file(note.path)
        for i, md_line in enumerate(md_reader.lines):

            if i == 1:
                out_lines.append(
                    f"[Open in typora](/open/typora/{note.nid})\n\n"
                )

            remove_line = False
            if not md_line.is_code_block:
                if md_line.text.startswith("# ") and not self.self_contained:
                    # Already set the title with meta info
                    remove_line = True

                for url in find_urls(md_line.text):
                    if not re.findall(fr"\[.*\]\({url}\)", md_line.text):
                        md_line.text = md_line.text.replace(
                            url, f"[{url}]({url})"
                        )

                # Mark external links with a '*'
                md_line.text = note.external_link_regex.sub(
                    r'<a href="\2" class="external">\1</a>', md_line.text
                )

                # Remove old markdown links
                md_line.text = note.autogen_link_regex.sub("", md_line.text,)

                # Replace raw zids, leave only links
                nids = note.id_link_regex.findall(md_line.text)
                for nid in nids:
                    try:
                        n = self.zk[nid]
                        title = n.title
                        md_line.text = md_line.text.replace(
                            f"[[{nid}]]", f"[{title}](/open/{nid})"
                        )
                    except KeyError:
                        logger.error(f"Couldn't find note {nid}")

            if not remove_line:
                out_lines.append(md_line.text)

        # out_lines.extend(["\n\n"] + dotgraph_html(self.zk, note))

        return "".join(out_lines)

    def convert(self, note: Note) -> str:
        css_path = Path(__file__).resolve().parent / "html_resources" / "1.css"
        cmd_parts = [
            "pandoc",
            "-t",
            "html",
            "--mathjax",
            "--highlight-style=pygments",
        ]
        if self.self_contained:
            cmd_parts.extend(
                [
                    "--self-contained",
                    f"--css={css_path}",
                    "--metadata",
                    f'pagetitle="{note.title}"',
                ]
            )
        try:
            ret = subprocess.run(
                cmd_parts,
                capture_output=True,
                universal_newlines=True,
                input=self.preproc_markdown(note=note),
            )
        except subprocess.CalledProcessError:
            raise
        return ret.stdout
