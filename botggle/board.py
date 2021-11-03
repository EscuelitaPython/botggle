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
                row.append(random.choice(dice).lower())
            distribution.append(row)
        return distribution

    def _build_graph(self):
        """Armar el grafo con palabras.

        No nos importa el costo de armar este grafo, porque se hace una sola vez, está pensado
        en que sea rápido buscar.

        Por ejemplo, para un tablero como

            a  b  c  b
            e  f  g  h
            i  j  a  l
            m  n  o  p

        ...nos iría quedando un grafo así:

            (a, 0) -> [(e, 4), (f, 5), (b, 1)]
            (b, 1) -> [(a, 0), (e, 4), ...,
            ...
        """
        result = {}
        for x_k in range(4):
            for y_k in range(4):
                key = LocatedChar(self.distribution[x_k][y_k], (x_k * 4) + y_k)
                around = set()
                positions = [
                    (x_k - 1, y_k),
                    (x_k + 1, y_k),
                    (x_k, y_k - 1),
                    (x_k, y_k + 1),
                    (x_k - 1, y_k - 1),
                    (x_k + 1, y_k + 1),
                    (x_k - 1, y_k + 1),
                    (x_k + 1, y_k - 1),
                ]
                for x_a, y_a in positions:
                    if (0 <= x_a <= 3) and (0 <= y_a <= 3):
                        around.add(LocatedChar(self.distribution[x_a][y_a], (x_a * 4) + y_a))
                result[key] = around
        return result

    def render(self):
        """Prepara un mensaje para mandar el tablero a un chat."""
        # NEXTWEEK hacer eso
        return str(self.distribution)  # FIXME: armarlo para que salga

    def exists(self, word: str) -> bool:
        """Return if the word exists in the board."""
        # FIXME: este algoritmo se rompe para palabras que tengan "CH" y que pasen por un
        # dado con "CH" (no dos con "C" y "H")
        # FIXME: tambien pensar en las palabras con Q y U
        def search(word, to_search, chain):
            """Función recursiva para encontrar los próx. dados para seguir hilando la palabra."""
            if len(word) == 0:
                return True

            useful_dices = [lc for lc in to_search if lc.char == word[0]]
            for dice in useful_dices:
                if any(dice == chain_dice for chain_dice in chain[1:]):
                    # algún dado de los anteriores (menos el primero) es igual al que sería el
                    # próximo, entonces en realidad el próximo no es útil
                    continue

                if chain and dice == chain[0] and len(word) > 1:
                    # Por qué el 1:
                    #   si el largo es 0: nunca llegamos acá porque tenemos el corte al pcipio
                    #   si el largo es 1: el próximo dado (el que tenemos acá como "util") es el
                    #       último, y está bien que se repita con el primero
                    #   si el largo es mayor a uno: el próximo dado, que se repite con el primero,
                    #       no sería el último, y eso está mal
                    continue

                chain_with_current_dice = chain + [dice]
                if search(word[1:], self._word_graph[dice], chain_with_current_dice):
                    return True
            return False

        return search(word, self._word_graph.keys(), [])
