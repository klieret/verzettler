#!/usr/bin/env python3

# std
from unittest import TestCase
from pathlib import Path

# ours
from verzettler.note import Note


class TestNote(TestCase):
    def setUp(self):
        self.playground = Path(__file__).resolve().parent / "playground"

    def test_id_regex(self):
        test2zid = {
            "something_20200416143522.md": "20200416143522",
            "something_20200416143522_else.md": "20200416143522",
            "ml_asdf_20200313225167.md": "20200313225167",
            "20200313225167.md": "20200313225167",
        }
        for test, zid in test2zid.items():
            with self.subTest(test=test):
                print(test)
                self.assertEqual(
                    zid,
                    Note.id_regex.findall(test)[0]
                )

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