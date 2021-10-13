# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""Tests for the game module."""

from botggle.game import Game, TransitionError, NotActiveError

import pytest


# -- pruebas del ciclo de vida

# NEXTWEEK ** 2: hacer que estos tests funcionesnnnnnn

def test_lifecycle_init():
    game = Game([], "chat")
    assert game._state == Game.State.WAITING


def test_lifecycle_start_after_init():
    game = Game([], "chat")
    game.round_words['foo'].append('bar')
    game.start_round()
    assert game._state == Game.State.ACTIVE
    assert len(game.round_words) == 0


def test_lifecycle_start_when_active():
    game = Game([], "chat")
    game.start_round()
    with pytest.raises(TransitionError):
        game.start_round()


def test_lifecycle_start_when_stopped():
    game = Game([], "chat")
    game.start_round()
    game.stop_round()
    with pytest.raises(TransitionError):
        game.start_round()


def test_lifecycle_next_round_when_stopped():
    game = Game([], "chat")
    game.start_round()
    game.stop_round()
    game.next_round()
    assert game._state == Game.State.WAITING


def test_lifecycle_next_round_when_active():
    game = Game([], "chat")
    game.start_round()
    with pytest.raises(TransitionError):
        game.next_round()


def test_lifecycle_next_round_when_waiting():
    game = Game([], "chat")
    with pytest.raises(TransitionError):
        game.next_round()


def test_lifecycle_stop_round_when_active():
    game = Game([], "chat")
    game.start_round()
    game.stop_round()
    assert game._state == Game.State.STOPPED


def test_lifecycle_stop_round_when_waiting():
    game = Game([], "chat")
    with pytest.raises(TransitionError):
        game.stop_round()


def test_lifecycle_stop_round_when_stopped():
    game = Game([], "chat")
    game.start_round()
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
    game.start_round()
    game.add_text("jdoe", "fruta")
    assert game.round_words == {'jdoe': {'fruta'}}


def test_addtext_twice_sameword():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", "fruta")
    game.add_text("jdoe", "fruta")
    assert game.round_words == {'jdoe': {'fruta'}}


def test_addtext_twice_differentword():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", "fruta1")
    game.add_text("jdoe", "fruta2")
    assert game.round_words == {'jdoe': {'fruta1', 'fruta2'}}


def test_addtext_twice_differentuser():
    game = Game([], "chat")
    game.start_round()
    game.add_text("john", "fruta")
    game.add_text("jane", "fruta")
    assert game.round_words == {'john': {'fruta'}, 'jane': {'fruta'}}


def test_addtext_twice_all_different():
    game = Game([], "chat")
    game.start_round()
    game.add_text("john", "fruta1")
    game.add_text("jane", "fruta2")
    assert game.round_words == {'john': {'fruta1'}, 'jane': {'fruta2'}}


def test_addtext_with_spaces():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", " foo   bar   ")
    assert game.round_words == {'jdoe': {'foo', 'bar'}}


def test_addtext_with_newlines():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", """
        foo
        bar
    """)
    assert game.round_words == {'jdoe': {'foo', 'bar'}}


@pytest.mark.parametrize("char", [',', '-', ';', "'", '"', ':', '[', ']', ',,'])
def test_addtext_with_rare_chars(char):
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", f"{char}foo{char} bar{char}baz{char}{char}")
    assert game.round_words == {'jdoe': {'foo', 'bar', 'baz'}}


def test_addtext_all_chars_mixed():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", """
        foo,-
        bar;
           baz
        +baz
    """)
    assert game.round_words == {'jdoe': {'foo', 'bar', 'baz'}}


def test_addtext_with_tilde():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", " fooá, fooé fooí-fooó; fooú,fooo")
    assert game.round_words == {'jdoe': {'fooa', 'fooe', 'fooi', 'fooo', 'foou'}}


def test_addtext_with_other_letters():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", " moño aäa ")
    assert game.round_words == {'jdoe': {'moño', 'aäa'}}


def test_addtext_with_other_letters():
    game = Game([], "chat")
    game.start_round()
    game.add_text("jdoe", " moño aäa ")
    assert game.round_words == {'jdoe': {'moño', 'aäa'}}

# NEXTWEEK falta un test acá

    # agregar palabras en mayúscula


# NEXTWEEK faltan los tests de estas otras dos funciones

# -- pruebas de evaluar palabras


# -- pruebas de resumir puntajes
