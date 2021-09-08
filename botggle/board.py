# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""Board functionality."""

import dataclasses
import random

GLYPHS = {}
for simple, squared in zip(range(65, 65 + 26), range(127280, 127280 + 26)):
    GLYPHS[chr(simple)] = chr(squared)
GLYPHS["CH"] = "Ch"

DICES = [
    ("G", "O", "L", "D", "O", "B"),
    ("F", "U", "A", "A", "B", "R"),
    ("B", "T", "A", "I", "N", "A"),
    ("B", "U", "O", "A", "E", "I"),
    ("C", "M", "R", "E", "A", "E"),
    ("V", "U", "Q", "D", "CH", "B"),
    ("T", "A", "I", "O", "L", "G"),
    ("M", "I", "B", "N", "E", "E"),
    ("A", "X", "H", "N", "S", "J"),
    ("CH", "O", "O", "E", "E", "U"),
    ("J", "I", "R", "F", "S", "E"),
    ("R", "Z", "S", "P", "L", "T"),
    ("T", "M", "O", "F", "I", "U"),
    ("R", "E", "S", "D", "A", "H"),
    ("V", "U", "E", "C", "P", "O"),
    ("T", "A", "P", "S", "C", "A"),
]


@dataclasses.dataclass(frozen=True)
class LocatedChar:
    char: str
    position: int


class Board:
    """A boggle board."""

    def __init__(self):
        self.distribution = self._get_distribution()

        # armamos el grafo
        self._word_graph = self._build_graph()

    def _get_distribution(self):
        # mezclamos los dados
        random.shuffle(DICES)

        distribution = []
        dices = iter(DICES)
        for i in range(4):
            row = []
            for j in range(4):
                dice = next(dices)
                row.append(random.choice(dice))
            distribution.append(row)
        return distribution

    def _build_graph(self):
        """Armar el grafo con palabras."""

    def render(self):
        """Prepara un mensaje para mandar el tablero a un chat."""
        return str(self.distribution)  # FIXME: do it :)

    def exists(self, word: str) -> bool:
        """Return if the word exists in the board."""



#    a  b  c  b
#    e  f  g  h
#    i  j  a  l
#    m  n  o  p
#
#for x in range(4):
#    for y in range(4):
#        (x * 4) + y
#
#
#Generar esta lista de grafos puede ser lento.
#Buscar acá tiene que ser rápido.
#(a, 0) -> [(e, 5), (f, 6), (b, 1)]
#(b, 1) -> [(a, 1), (e, 5), ...f, c, g),
#...
#(a,  15)
#
#
#
