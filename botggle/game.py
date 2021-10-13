# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""The Game class and a couple of helpers."""

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set


# load the RAE words
with open("rae_words.txt") as fh:
    rae_words = {line.strip() for line in fh}


class TransitionError(Exception):
    """Transición inválida en la máquina de estados de Game."""


class NotActiveError(Exception):
    """Se intentó alguna acción que sólo podía hacerse en estado ACTIVE."""


@dataclass
class ResultWords:
    valid: Set[str] = field(default_factory=set)
    repeated: Set[str] = field(default_factory=set)
    not_in_language: Set[str] = field(default_factory=set)
    not_in_board: Set[str] = field(default_factory=set)


class Game:
    """Representa un juego completo, que se compone por varias rondas."""

    State = enum.Enum("State", "WAITING ACTIVE STOPPED")
    _cleaning_table = str.maketrans(
        """.,;:'"-_=+[]{}áéíóú""",
        """              aeiou""",
    )

    def __init__(self, players, chat):
        self.players = players
        self._state = self.State.WAITING
        self.full_scores = defaultdict(int)
        self.round_words = defaultdict(set)

        # no lo usamos internamente, pero lo guardamos acá porque es el
        # grupo público donde el juego fue arrancado
        self.chat = chat

    def start_round(self):
        """Arranca la ronda."""
        if self._state != self.State.WAITING:
            raise TransitionError("Start sin estar en WAITING")
        self.round_words = defaultdict(set)
        self._state = self.State.ACTIVE

    def next_round(self):
        """Vuelve a esperar a todes les jugadores antes de la próxima ronda."""
        if self._state != self.State.STOPPED:
            raise TransitionError("Next round sin estar en STOPPED")
        self._state = self.State.WAITING

    def stop_round(self):
        """Termina la ronda (para dejar de recibir palabras)."""
        if self._state != self.State.ACTIVE:
            raise TransitionError("Stop round sin estar en ACTIVE")
        self._state = self.State.STOPPED

    def add_text(self, username, text):
        """Agrega una o más palabras a le usuarie si la ronda no está frenada."""
        if self._state != self.State.ACTIVE:
            raise NotActiveError(f"Se intentó agregar texto cuando el estado es {self._state}")

        text = text.translate(self._cleaning_table)
        for word in text.split():
            self.round_words[username].add(word)

    def evaluate_words(self):
        """Evalúa qué palabras son válidas y marca las repetidas."""
        print("=========== evaluarrrrrrrrr", self.round_words)
        # NEXTWEEK armar tests para esto
        full_result = {}
        for username, words in self.round_words.items():
            full_result[username] = result_words = ResultWords()

            for word in words:
                if word not in rae_words:
                    # la palabra no está en el diccionario
                    result_words.not_in_language.add(word)
                elif not self.game.board.exists(word):
                    # la palabra no está en el tablero
                    result_words.not_in_board.add(word)
                else:
                    result_words.valid.add(word)
            print("=========== result words for user", username, result_words)

        # FIXME: falta agarrar todas las valid, ver cuales están repetidas, y para cada jugador
        # fixear su ".valid" y su ".repetated" para expresar esto

        return full_result

    def summarize_scores(self, user_words):
        """Cierra la ronda, evalúa las palabras y hace el resumen de los scores."""
        # NEXTWEEK armar tests para esto
        round_result = self._calculate_scores(user_words)
        for player_name, round_score in round_result:
            self.full_scores[player_name] += round_score
        return round_result