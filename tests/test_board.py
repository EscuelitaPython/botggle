"""Tests for the board module."""

from botggle.board import Board, LocatedChar as LC


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
        LC('e', 3): {LC('c', 2), LC('g', 6), LC('h', 7)},
        # FIXME: necesitamos terminar esto!!!
        # NEXTWEEK
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
