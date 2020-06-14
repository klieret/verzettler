#!/usr/bin/env python3

# std
import collections

# ours
from verzettler.zettelkasten import Zettelkasten
from verzettler.bokeh_utils import int_hist


# def depth_histogram(zk: Zettelkasten):
#     data = zk.get_nnotes_by_depth()


def make_link_histogram(zk: Zettelkasten):
    data = [len(note.links) for note in zk.notes]
    bins = [i - 0.5 for i in range(20)]
    plot = int_hist(
        data,
        bins=bins,
        title="Links per note",
        x_axis_label="Links per note",
        x_tooltip="Links per note"
    )

    return plot


def make_backlink_histogram(zk: Zettelkasten):
    backlinks = collections.defaultdict(int)
    for note in zk.notes:
        for link in note.links:
            backlinks[link] += 1
    data = list(backlinks.values())
    bins = [i - 0.5 for i in range(20)]
    plot = int_hist(
        data,
        bins=bins,
        title="Backlinks per note",
        x_axis_label="Backlinks per note",
        x_tooltip="Backlinks per note"
    )

    return plot
