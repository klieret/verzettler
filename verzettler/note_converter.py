#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import PurePath, Path
import random
import subprocess

# 3rd
import networkx as nx

# ours
from verzettler.note import Note
from verzettler.markdown_reader import MarkdownReader
from verzettler.log import logger


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


_dotgraph_html = """
<div id="mynetwork" style="height: 500px;"></div>

<script type="text/javascript">
  let container = document.getElementById('mynetwork');
  let dot = `{dotgraph}`;
  let data = vis.parseDOTNetwork(dot);
  let options = {}
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
    selected_nodes = {note.nid}  # self.zk._graph.get_k_neighbors(note.nid)
    try:
        selected_nodes |= set(
            nx.dijkstra_path(zk._graph, zk.root, note.nid))
        for connection in nx.all_simple_paths(zk._graph, zk.root,
                                              note.nid):
            selected_nodes |= set(connection)
    except nx.exception.NetworkXNoPath:
        logger.warning(f"No path from {zk.root} to {note.nid}")
    selected_nodes |= set(zk._graph.predecessors(note.nid))
    selected_nodes |= set(
        nx.descendants_at_distance(zk._graph, note.nid, distance=1))
    optional_nodes = set()
    for dist in range(2, 3):
        optional_nodes |= set(
            nx.descendants_at_distance(zk._graph, note.nid, distance=dist))
    for predecessor in zk._graph.predecessors(note.nid):
        optional_nodes |= set(zk._graph.successors(predecessor))
    optional_nodes -= selected_nodes
    if len(selected_nodes) < 30:
        selected_nodes |= set(random.choices(
            list(optional_nodes),
            k=min(len(optional_nodes), 30 - len(selected_nodes))
        ))

    # for i in range(1, maxdepth):
    #     selected_nodes |= nbd[i]
    out_lines = []
    if len(selected_nodes) < 50:
        out_lines.append(
            '<script src="/assets/vis-network.min.js"></script>\n', )
        dotstr = zk.dot_graph(only_nodes=selected_nodes,
                                   variable_size=False)
        out_lines.append(_dotgraph_html.replace("{dotgraph}", dotstr))
    return out_lines


class JekyllConverter(NoteConverter):

    #.replace("'", "\\'").replace("\n", "' + \n'")

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

                # Jekyll somehow eats my
                # '*' characters, causing problems with LaTeX.
                md_line.text = md_line.text.replace(r"^*", r"^\ast")
                md_line.text = md_line.text.replace(r"^{**", r"^{\ast\ast")
                md_line.text = md_line.text.replace(r"^{*", r"^{\ast")

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
                try:
                    n = self.zk[nid]
                    title = n.title
                    md_line.text = md_line.text.replace(f"[[{nid}]]", f"[{title}](/open/{nid})")
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
                try:
                    n = self.zk[nid]
                    title = n.title
                    md_line.text = md_line.text.replace(f"[[{nid}]]",
                                                        f"[{title}](/open/{nid})")
                except KeyError:
                    logger.error(f"Couldn't find note {nid}")

            if not remove_line:
                out_lines.append(md_line.text)

        out_lines.extend(dotgraph_html(self.zk, note))

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
            cmd_parts.extend([
                "--self-contained",
                f"--css={css_path}",
                "--metadata",
                f"pagetitle=\"{note.title}\"",
            ])
        try:
            ret = subprocess.run(
                cmd_parts,
                capture_output=True,
                universal_newlines=True,
                input=self.preproc_markdown(note=note)
            )
        except subprocess.CalledProcessError:
            raise
        return ret.stdout
