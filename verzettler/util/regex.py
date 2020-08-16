#!/usr/bin/env python3

""" Utility functions for regular expressions """

# std
import re
from typing import List

_url_regex = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
)


def find_urls(string: str) -> List[str]:
    """ Finds all URLs in given string.
    Source: https://www.geeksforgeeks.org/python-check-url-string/

    Args:
        string:

    Returns:
        List of all URLs
    """
    url = _url_regex.findall(string)
    return [x[0] for x in url]


def test_find_urls():
    assert find_urls("https://www.google.com asdfasdf") == [
        "https://www.google.com"
    ]
    assert find_urls("") == []
    assert find_urls("asdf asdf") == []
    assert find_urls("www.github.com www.gitlab.com") == [
        "www.github.com",
        "www.gitlab.com",
    ]
