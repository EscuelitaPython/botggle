"""Tests for the board module."""

from botggle.board import Board, LocatedChar as LC

import pytest


def test_graph_simple(monkeypatch):
    distribution = [
        list("abcd"),
        list("efgh"),
        list("ijkl"),
        list("mnop"),
    ]
    monkeypatch.setattr(Board, "_get_distribution", lambda self: distribution)

    b = Board()
    expected = {
        LC('a', 0): {LC('b', 1), LC('e', 4), LC('f', 5)},
        LC('b', 1): {LC('a', 0), LC('e', 4), LC('f', 5), LC('c', 2), LC('g', 6)},
        LC('c', 2): {LC('b', 1), LC('f', 5), LC('h', 7), LC('d', 3), LC('g', 6)},
        LC('d', 3): {LC('c', 2), LC('g', 6), LC('h', 7)},
        LC('e', 4): {LC('a', 0), LC('b', 1), LC('f', 5), LC('i', 8), LC('j', 9)},
        LC('f', 5): {
            LC('a', 0), LC('b', 1), LC('c', 2), LC('e', 4),
            LC('g', 6), LC('i', 8), LC('j', 9), LC('k', 10)},
        LC('g', 6): {
            LC('b', 1), LC('c', 2), LC('d', 3), LC('f', 5),
            LC('h', 7), LC('j', 9), LC('k', 10), LC('l', 11)},
        LC('h', 7): {LC('c', 2), LC('d', 3), LC('g', 6), LC('k', 10), LC('l', 11)},
        LC('i', 8): {LC('e', 4), LC('f', 5), LC('j', 9), LC('m', 12), LC('n', 13)},
        LC('j', 9): {
            LC('e', 4), LC('f', 5), LC('g', 6), LC('i', 8),
            LC('k', 10), LC('m', 12), LC('n', 13), LC('o', 14)},
        LC('k', 10): {
            LC('f', 5), LC('g', 6), LC('h', 7), LC('j', 9),
            LC('l', 11), LC('n', 13), LC('o', 14), LC('p', 15)},
        LC('l', 11): {LC('g', 6), LC('h', 7), LC('k', 10), LC('o', 14), LC('p', 15)},
        LC('m', 12): {LC('i', 8), LC('j', 9), LC('n', 13)},
        LC('n', 13): {LC('i', 8), LC('j', 9), LC('k', 10), LC('m', 12), LC('o', 14)},
        LC('o', 14): {LC('j', 9), LC('k', 10), LC('l', 11), LC('n', 13), LC('p', 15)},
        LC('p', 15): {LC('k', 10), LC('l', 11), LC('o', 14)},
    }
    assert b._word_graph == expected


def test_exists_simple_missing(monkeypatch):
    distribution = [
        list("abcd"),
        list("xyzq"),
        list("hhhh"),
        list("jjjj"),
    ]
    monkeypatch.setattr(Board, "_get_distribution", lambda self: distribution)

    b = Board()
    result = b.exists("hola")
    assert result is False


@pytest.mark.parametrize("word,expected", [
    ("hola", True),
    ("hold", False),
    ("hol", True),
    ("holas", False),
    ("ablx", True),
    ("ablxa", True),
    ("ablxab", False),  # NEXTWEEK
    ("ablxb", False),  # NEXTWEEK
    ("ablxba", False),  # NEXTWEEK
    ("cdab", False),
    ("ababababababababab", False),  # NEXTWEEK
])
def test_exists_case_1(monkeypatch, word, expected):
    distribution = [
        list("abcd"),
        list("xlzq"),
        list("hohh"),
        list("jjjj"),
    ]
    monkeypatch.setattr(Board, "_get_distribution", lambda self: distribution)

    b = Board()
    result = b.exists(word)
    assert result is expected
