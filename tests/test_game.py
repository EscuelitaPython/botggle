# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""Tests for the game module."""

from botggle.game import Game, TransitionError

import pytest


# -- pruebas del ciclo de vida

# NEXTWEEK ** 2: hacer que estos tests funcionesnnnnnn

def test_lifecycle_init():
    game = Game([], "chat")
    assert game._state == Game.State.WAITING


def test_lifecycle_start_after_init():
    game = Game([], "chat")
    game.start_round()
    assert game._state == Game.State.ACTIVE


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
    game.start()
    game.stop_round()
    assert game._state == Game.State.STOPPED


def test_lifecycle_stop_round_when_waiting():
    game = Game([], "chat")
    with pytest.raises(TransitionError):
        game.stop_round()


def test_lifecycle_stop_round_when_stopped():
    game = Game([], "chat")
    game.start()
    game.stop_round()
    with pytest.raises(TransitionError):
        game.end_round()


# -- pruebas de agregar texto


# -- pruebas de evaluar palabras


# -- pruebas de resumir puntajes
