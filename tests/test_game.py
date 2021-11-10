# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""Tests for the game module."""

import botggle.game
from botggle.board import Board
from botggle.game import Game, TransitionError, NotActiveError, ResultWords, Player

import pytest


# -- pruebas del ciclo de vida


def test_lifecycle_init():
    game = Game([], "chat")
    assert game._state == Game.State.WAITING


def test_lifecycle_start_after_init():
    game = Game([], "chat")
    game.round_words['foo'].add('bar')
    game.start_round(Board())
    assert game._state == Game.State.ACTIVE
    assert len(game.round_words) == 0


def test_lifecycle_start_when_active():
    game = Game([], "chat")
    game.start_round(Board())
    with pytest.raises(TransitionError):
        game.start_round(Board())


def test_lifecycle_start_when_stopped():
    game = Game([], "chat")
    game.start_round(Board())
    game.stop_round()
    with pytest.raises(TransitionError):
        game.start_round(Board())


def test_lifecycle_next_round_when_stopped():
    p1 = Player("maria", "fakegame")
    p1.ready = False
    p2 = Player("juan", "fakegame")
    p2.ready = True
    game = Game([p1, p2], "chat")
    game.start_round(Board())
    game.stop_round()
    game.next_round()
    assert game._state == Game.State.WAITING
    assert all(not p.ready for p in game.players)


def test_lifecycle_next_round_when_active():
    game = Game([], "chat")
    game.start_round(Board())
    with pytest.raises(TransitionError):
        game.next_round()


def test_lifecycle_next_round_when_waiting():
    game = Game([], "chat")
    with pytest.raises(TransitionError):
        game.next_round()


def test_lifecycle_stop_round_when_active():
    game = Game([], "chat")
    game.start_round(Board())
    game.stop_round()
    assert game._state == Game.State.STOPPED


def test_lifecycle_stop_round_when_waiting():
    game = Game([], "chat")
    with pytest.raises(TransitionError):
        game.stop_round()


def test_lifecycle_stop_round_when_stopped():
    game = Game([], "chat")
    game.start_round(Board())
    game.stop_round()
    with pytest.raises(TransitionError):
        game.stop_round()


# -- pruebas de agregar texto

def test_addtext_when_not_active():
    game = Game([], "chat")
    assert game._state != Game.State.ACTIVE
    with pytest.raises(NotActiveError):
        game.add_text("jdoe", "fruta")
    assert len(game.round_words) == 0


def test_addtext_simple():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", "fruta")
    assert game.round_words == {'jdoe': {'fruta'}}


def test_addtext_twice_sameword():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", "fruta")
    game.add_text("jdoe", "fruta")
    assert game.round_words == {'jdoe': {'fruta'}}


def test_addtext_twice_differentword():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", "fruta1")
    game.add_text("jdoe", "fruta2")
    assert game.round_words == {'jdoe': {'fruta1', 'fruta2'}}


def test_addtext_twice_differentuser():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("john", "fruta")
    game.add_text("jane", "fruta")
    assert game.round_words == {'john': {'fruta'}, 'jane': {'fruta'}}


def test_addtext_twice_all_different():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("john", "fruta1")
    game.add_text("jane", "fruta2")
    assert game.round_words == {'john': {'fruta1'}, 'jane': {'fruta2'}}


def test_addtext_with_spaces():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", " foo   bar   ")
    assert game.round_words == {'jdoe': {'foo', 'bar'}}


def test_addtext_with_newlines():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", """
        foo
        bar
    """)
    assert game.round_words == {'jdoe': {'foo', 'bar'}}


@pytest.mark.parametrize("char", [',', '-', ';', "'", '"', ':', '[', ']', ',,'])
def test_addtext_with_rare_chars(char):
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", f"{char}foo{char} bar{char}baz{char}{char}")
    assert game.round_words == {'jdoe': {'foo', 'bar', 'baz'}}


def test_addtext_all_chars_mixed():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", """
        foo,-
        bar;
           baz
        +baz
    """)
    assert game.round_words == {'jdoe': {'foo', 'bar', 'baz'}}


def test_addtext_with_tilde():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", " fooá, fooé fooí-fooó; fooú,fooo")
    assert game.round_words == {'jdoe': {'fooa', 'fooe', 'fooi', 'fooo', 'foou'}}


def test_addtext_with_other_letters():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", " moño aäa ")
    assert game.round_words == {'jdoe': {'moño', 'aäa'}}


def test_addtext_with_uppercase():
    game = Game([], "chat")
    game.start_round(Board())
    game.add_text("jdoe", " foo Bar BAZ, MOÑO, CAMIÓN")
    assert game.round_words == {'jdoe': {'foo', 'bar', 'baz', 'moño', 'camion'}}


# -- pruebas de evaluar palabras


def test_evaluate_ok(monkeypatch):
    monkeypatch.setattr(botggle.game, 'rae_words', {'foo', 'bar', 'baz'})

    board = Board()
    board.exists = lambda word: True

    game = Game([], "chat")
    game.start_round(board)
    game.round_words = {'jdoe': {'foo', 'bar'}, 'pepe': {'baz'}}

    result = game.evaluate_words()
    expected_jdoe = ResultWords(
        valid={'foo', 'bar'}, repeated=set(), not_in_language=set(), not_in_board=set())
    expected_pepe = ResultWords(
        valid={'baz'}, repeated=set(), not_in_language=set(), not_in_board=set())
    assert result == {'jdoe': expected_jdoe, 'pepe': expected_pepe}


def test_evaluate_not_in_rae(monkeypatch):
    monkeypatch.setattr(botggle.game, 'rae_words', {'bar'})

    board = Board()
    board.exists = lambda word: True

    game = Game([], "chat")
    game.start_round(board)
    game.round_words = {'jdoe': {'foo', 'bar'}}

    result = game.evaluate_words()
    expected = ResultWords(
        valid={'bar'}, repeated=set(), not_in_language={'foo'}, not_in_board=set())
    assert result == {'jdoe': expected}


def test_evaluate_not_in_board(monkeypatch):
    monkeypatch.setattr(botggle.game, 'rae_words', {'foo', 'bar'})

    board = Board()
    board.exists = lambda word: word in {'bar'}

    game = Game([], "chat")
    game.start_round(board)
    game.round_words = {'jdoe': {'foo', 'bar'}}

    result = game.evaluate_words()
    expected = ResultWords(
        valid={'bar'}, repeated=set(), not_in_language=set(), not_in_board={'foo'})
    assert result == {'jdoe': expected}


def test_evaluate_repeated_valid(monkeypatch):
    monkeypatch.setattr(botggle.game, 'rae_words', {'foo', 'bar', 'baz', 'wee', 'xxx'})

    board = Board()
    board.exists = lambda word: True

    game = Game([], "chat")
    game.start_round(board)
    game.round_words = {
        'jdoe': {'foo', 'bar'},
        'pepe': {'foo', 'baz', 'wee'},
        'mara': {'xxx', 'baz'},
        'juan': {'foo'},
    }

    result = game.evaluate_words()
    expected_jdoe = ResultWords(
        valid={'bar'}, repeated={'foo'}, not_in_language=set(), not_in_board=set())
    expected_pepe = ResultWords(
        valid={'wee'}, repeated={'foo', 'baz'}, not_in_language=set(), not_in_board=set())
    expected_mara = ResultWords(
        valid={'xxx'}, repeated={'baz'}, not_in_language=set(), not_in_board=set())
    expected_juan = ResultWords(
        valid=set(), repeated={'foo'}, not_in_language=set(), not_in_board=set())
    assert result == {
        'jdoe': expected_jdoe, 'pepe': expected_pepe, 'mara': expected_mara, 'juan': expected_juan}


# -- pruebas de resumir puntajes

def test_summarize_simple(monkeypatch):
    players = [Player("juan", "fakegame")]
    game = Game(players, "chat")
    game._calculate_scores = lambda *a: 5

    rw = ResultWords(
        valid={"foo"}, repeated=set(), not_in_language=set(), not_in_board=set())
    user_words = {"juan": rw}

    scores = game.summarize_scores(user_words)
    assert scores == {"juan": 5}
    assert game.full_scores == {"juan": 5}

    scores = game.summarize_scores(user_words)
    assert scores == {"juan": 5}
    assert game.full_scores == {"juan": 10}


def test_summarize_double():
    players = [Player("juan", "fakegame"), Player("mara", "fakegame")]
    game = Game(players, "chat")
    game._calculate_scores = lambda *a: 5

    rw = ResultWords(
        valid={"foo"}, repeated=set(), not_in_language=set(), not_in_board=set())

    user_words = {"juan": rw}
    scores = game.summarize_scores(user_words)
    assert scores == {"juan": 5}
    assert game.full_scores == {"juan": 5, "mara": 0}

    user_words = {"mara": rw, "juan": rw}
    scores = game.summarize_scores(user_words)
    assert scores == {"mara": 5, "juan": 5}
    assert game.full_scores == {"juan": 10, "mara": 5}


@pytest.mark.parametrize("length", [0, 1, 2])
def test_scores_too_short(length):
    rw = ResultWords(
        valid={"x" * length}, repeated=set(), not_in_language=set(), not_in_board=set())
    game = Game([], "chat")
    score = game._calculate_scores(rw)
    assert score == 0


def test_scores_not_valid():
    rw = ResultWords(
        valid=set(), repeated={"foobar"}, not_in_language={"foobar"}, not_in_board={"foobar"})
    game = Game([], "chat")
    score = game._calculate_scores(rw)
    assert score == 0


def test_scores_too_long():
    rw = ResultWords(
        valid={"x" * 123}, repeated=set(), not_in_language=set(), not_in_board=set())
    game = Game([], "chat")
    score = game._calculate_scores(rw)
    assert score == 79


def test_scores_intermediate(monkeypatch):
    monkeypatch.setattr(botggle.game, "SCORES_TABLE", {6: 123})
    rw = ResultWords(
        valid={"foobar"}, repeated=set(), not_in_language=set(), not_in_board=set())
    game = Game([], "chat")
    score = game._calculate_scores(rw)
    assert score == 123


def test_scores_accumulates(monkeypatch):
    monkeypatch.setattr(botggle.game, "SCORES_TABLE", {6: 123, 3: 15})
    rw = ResultWords(
        valid={"foobar", "yes"}, repeated=set(), not_in_language=set(), not_in_board=set())
    game = Game([], "chat")
    score = game._calculate_scores(rw)
    assert score == 138
