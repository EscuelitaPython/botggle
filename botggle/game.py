# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""The Game class and a couple of helpers."""

import enum
import itertools
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Set

SCORES_TABLE = {
    3: 1,
    4: 2,
    5: 4,
    6: 7,
    7: 11,
    8: 16,
    9: 22,
    10: 29,
    11: 37,
    12: 46,
    13: 56,
    14: 67,
}
MIN_WORD_LENGTH = min(SCORES_TABLE)
MAX_WORD_LENGTH = max(SCORES_TABLE)
MAX_WORD_SCORE = 79


# load the RAE words
with open("rae_words.txt") as fh:
    rae_words = {line.strip() for line in fh}


class TransitionError(Exception):
    """Transición inválida en la máquina de estados de Game."""


class NotActiveError(Exception):
    """Se intentó alguna acción que sólo podía hacerse en estado ACTIVE."""


class Player:
    def __init__(self, username, game):
        self.username = username
        self.ready = False
        self.game = game
        self.chat = None


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

    def __init__(self, chat):
        self.players = []
        self.full_scores = {}
        self._state = self.State.WAITING
        self.round_words = defaultdict(set)
        self.board = None

        # no lo usamos internamente, pero lo guardamos acá porque es el
        # grupo público donde el juego fue arrancado
        self.chat = chat

    def add_player(self, username):
        """Carga une jugadore en el juego."""
        player = Player(username, self)
        self.players.append(player)
        self.full_scores[player.username] = 0
        return player

    def start_round(self, board):
        """Arranca la ronda."""
        if self._state != self.State.WAITING:
            raise TransitionError("Start sin estar en WAITING")
        self.board = board
        self.round_words = defaultdict(set)
        self._state = self.State.ACTIVE

    def next_round(self):
        """Vuelve a esperar a todes les jugadores antes de la próxima ronda."""
        if self._state != self.State.STOPPED:
            raise TransitionError("Next round sin estar en STOPPED")
        self._state = self.State.WAITING
        for player in self.players:
            player.ready = False

    def stop_round(self):
        """Termina la ronda (para dejar de recibir palabras)."""
        if self._state != self.State.ACTIVE:
            raise TransitionError("Stop round sin estar en ACTIVE")
        self._state = self.State.STOPPED

    def add_text(self, username, text):
        """Agrega una o más palabras a le usuarie si la ronda no está frenada."""
        if self._state != self.State.ACTIVE:
            raise NotActiveError(f"Se intentó agregar texto cuando el estado es {self._state}")

        text = text.lower()
        text = text.translate(self._cleaning_table)
        for word in text.split():
            self.round_words[username].add(word)

    def evaluate_words(self):
        """Evalúa qué palabras son válidas y marca las repetidas."""
        full_result = {}
        for username, words in self.round_words.items():
            full_result[username] = result_words = ResultWords()

            for word in words:
                if word not in rae_words:
                    # la palabra no está en el diccionario
                    result_words.not_in_language.add(word)
                elif not self.board.exists(word):
                    # la palabra no está en el tablero
                    result_words.not_in_board.add(word)
                else:
                    result_words.valid.add(word)

        for rword1, rword2 in itertools.combinations(full_result.values(), 2):
            repes = rword1.valid & rword2.valid
            rword1.repeated.update(repes)
            rword2.repeated.update(repes)

        for rword in full_result.values():
            rword.valid -= rword.repeated

        return full_result

    def _calculate_scores(self, result_words):
        """Devuelve el puntaje total para una lista de palabras válidas."""
        score = 0
        for word in result_words.valid:
            if len(word) > MAX_WORD_LENGTH:
                score += MAX_WORD_SCORE
            else:
                score += SCORES_TABLE.get(len(word), 0)
        return score

    def summarize_scores(self, user_words):
        """Cierra la ronda, evalúa las palabras y hace el resumen de los scores."""
        round_result = {}
        for username, result_words in user_words.items():
            round_score = self._calculate_scores(result_words)
            round_result[username] = round_score
            self.full_scores[username] += round_score
        return round_result
