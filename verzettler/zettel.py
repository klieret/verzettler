#!/usr/bin/env python3

# std
import re
from typing import Optional, Union, Set
from pathlib import Path, PurePath
import io
import subprocess
import json

# 3rd
import panflute


def list_container_to_string(lc):
    return "".join(panflute.stringify(elem) for elem in lc)


class Zettel(object):

    id_regex = re.compile("[0-9]{14}")
    zid_link_regex = re.compile(r"\[\[[0-9]{14}\]\]")
    tag_regex = re.compile(r"#\S*")

    def __init__(self, path: Path, zettelkasten=None):
        self.path = path
        self.zid = self.get_zid(path)  # type: str

        self.links = set()  # type: Set[str]
        self.existing_backlinks = set()  # type: Set[str]
        self.title = ""
        self.tags = set()  # type: Set[str]

        self.depth = None  # type: Optional[int]

        self.pf_doc = None  # type: Optional[panflute.Doc]

        self.zettelkasten = zettelkasten

        self.analyze_file()

    # Class methods
    # =========================================================================

    @classmethod
    def get_zid(cls, path: Union[str, PurePath]) -> str:
        """ Zettel ID"""
        path = PurePath(path)
        matches = cls.id_regex.findall(path.name)
        if matches:
            return matches[0]
        else:
            return path.name

    # Analyze file
    # =========================================================================

    def _pf_filter_sections(self, elem: panflute.Element, doc: panflute.Doc) \
            -> panflute.Element:

        if isinstance(elem, panflute.Header):
            doc.verzettler_section = doc.verzettler_section[:elem.level - 1]
            doc.verzettler_section.append(
                list_container_to_string(elem.content))
            if elem.level == 1:
                self.title = list_container_to_string(elem.content)

        return elem

    def pf_filter_analyze(self, elem: panflute.Element, doc: panflute.Doc) \
            -> panflute.Element:

        elem = self._pf_filter_sections(elem, doc)

        if isinstance(elem, panflute.Str):
            self.tags |= set(self.tag_regex.findall(elem.text))

            # noinspection PyUnresolvedReferences
            if len(doc.verzettler_section) < 2 or \
                    "backlinks" != doc.verzettler_section[1].lower():
                self.links |= set(self.id_regex.findall(elem.text))
            else:
                self.existing_backlinks |= set(self.id_regex.findall(elem.text))

        return elem

    def pf_filter_transform(self, elem: panflute.Element, doc: panflute.Doc) \
        -> panflute.Element:

        elem = self._pf_filter_sections(elem, doc)

        if isinstance(elem, panflute.Str):
            if self.zid_link_regex.match(elem.text):
                print(elem.text)

        return elem

    def analyze_file(self) -> None:
        # json_str = pypandoc.convert_file(str(self.path), 'json', format='md')
        json_str = subprocess.run(
            [
                "pandoc",
                "-t",
                "json",
                str(self.path),
            ],
            capture_output=True
        ).stdout.decode("utf-8")
        inf = io.StringIO(json_str)
        self.pf_doc = panflute.load(inf)

        self.pf_doc.verzettler_section = []

        self.links = set()
        self.existing_backlinks = set()
        self.tags = set()
        #
        self.pf_doc = self.pf_doc.walk(self.pf_filter_analyze)

    def transform_file(self) -> None:
        self.pf_doc = self.pf_doc.walk(self.pf_filter_transform)

    def write(self) -> None:
        altered_json = json.dumps(self.pf_doc.to_json())
        altered_md = subprocess.run(
            ["pandoc", "-f", "json", "-t", "markdown", "--atx-header", "--wrap", "none"],
            input=altered_json, encoding="utf8", capture_output=True
        ).stdout
        with self.path.open("w") as outf:
            outf.write(altered_md)



    # Magic
    # =========================================================================

    def __repr__(self):
        return f"Zettel({self.get_zid})"
