#!/usr/bin/env python3

# std
from unittest import TestCase
from pathlib import Path

# ours
from verzettler.zettelkasten import Zettelkasten


class TestZettelkasten(TestCase):
    def setUp(self):
        self.playground = Path(__file__).resolve().parent / "playground"
        self.zk = Zettelkasten()
        self.zk.add_notes_from_directory(self.playground)

    def test_tags(self):
        self.assertEqual({"tag1", "tag2"}, set(self.zk.tags))

    def test_len(self):
        self.assertEqual(
            len(self.zk),
            len(
                [f for f in self.playground.iterdir() if f.name.endswith(".md")]
            ),
        )

    def test_getitem(self):
        self.assertEqual(
            self.zk["00000000000000"].path,
            self.playground / "00000000000000_zid.md",
        )

    def test_get_backlinks(self):
        self.assertEqual(
            set(self.zk.get_backlinks("00000000000003")), {"00000000000002"}
        )

    def test_search(self):
        self.assertEqual(
            [self.zk["00000000000000"]], self.zk.search("00000000000000")
        )
