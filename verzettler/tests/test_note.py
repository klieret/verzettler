#!/usr/bin/env python3

# std
from unittest import TestCase
from pathlib import Path
from typing import Dict, List
import re

# ours
from verzettler.note import Note


class TestNote(TestCase):
    def setUp(self):
        self.playground = Path(__file__).resolve().parent / "playground"

    def _test_regex_findall_dict(
            self,
            regex: re.Pattern,
            dct: Dict[str, List[str]]
    ):
        for test, matches in dct.items():
            with self.subTest(test=test):
                self.assertEqual(
                    matches,
                    regex.findall(test)
                )

    def _test_regex_findall_single_match_dict(
            self,
            regex: re.Pattern,
            dct: Dict[str, str]
    ):
        return self._test_regex_findall_dict(
            regex=regex,
            dct={key: [value] for key, value in dct.items()}
        )

    def test_id_regex(self):
        test2zid = {
            "something_20200416143522.md": "20200416143522",
            "something_20200416143522_else.md": "20200416143522",
            "ml_asdf_20200313225167.md": "20200313225167",
            "20200313225167.md": "20200313225167",
        }
        self._test_regex_findall_single_match_dict(Note.id_regex, test2zid)

    def test_link_id_regex(self):
        test2zid = {
            "something [[20200416143522]]": "20200416143522",
            "something [[20200416143522]] else": "20200416143522",
            "[[20200313225167]]": "20200313225167",
        }
        self._test_regex_findall_single_match_dict(Note.id_regex, test2zid)

    def test_external_link_regex(self):
        dct = {
            '[a](asdf.md "autogen")': [],
            '[a](asdf.md)': [],
            '[a](https://a/b/c/x.html)': [("a", "https://a/b/c/x.html")],
            '[a](https://a/b/c/x.html "something")': [("a", 'https://a/b/c/x.html "something"')]
        }
        self._test_regex_findall_dict(Note.external_link_regex, dct)


    def get_note_by_fname(self, fname):
        return Note(self.playground / fname)

    def test_init_note(self):
        n = self.get_note_by_fname("00000000000000_zid.md")
        print(n, n.nid)
        print("------------ here")
        self.assertEqual(
            "00000000000000", n.nid
        )

    def test_get_links(self):
        n = self.get_note_by_fname("00000000000002_links_01.md")
        self.assertEqual(
            {"00000000000003", "00000000000004", "00000000000005"},
            set(n.links),
        )

    def test_get_tags(self):
        n = self.get_note_by_fname("00000000000001_tags.md")
        self.assertEqual(
            {"tag1", "tag2"},
            set(n.tags)
        )

    def test_get_title(self):
        n = self.get_note_by_fname("00000000000006_title.md")
        self.assertEqual(
            "This is a title",
            n.title
        )