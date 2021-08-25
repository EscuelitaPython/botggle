#!/usr/bin/env fades

""" Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import enum
import random
import sys
from collections import defaultdict

import infoauth  # fades
from telegram import Update, ForceReply, MessageEntity, ParseMode  # fades python-telegram-bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


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

# relaciona el username al player
PLAYER_BY_USERNAME = {}

# relaciona el chat al Game
GAME_BY_CHAT = {}


class Board:

    def __init__(self):
        # mezclamos los dados
        random.shuffle(DICES)

        self.distribution = []
        dices = iter(DICES)
        for i in range(4):
            row = []
            for j in range(4):
                dice = next(dices)
                row.append(random.choose(dice))
            self.distribution.append(row)

    def render(self):
        """Prepara un mensaje para mandar el tablero a un chat."""


class Player:
    def __init__(self, username, game):
        self.username = username
        self.ready = False
        self.game = game
        self.chat = None


class Game:

    State = enum.Enum("State", "WAITING ACTIVE FINISHED")

    def __init__(self, players, chat):
        self.players = players
        self.chat = chat
        self._state = self.State.WAITING

    def start(self):
        """Arranca la ronda."""
        self.round_words = defaultdict(list)
        self._state = self.State.ACTIVE

    def next_round(self):
        """Vuelve a esperar a todes les jugadores antes de la próxima ronda."""
        self._state = self.State.WAITING





def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    print("Bot invited to some chat by", user.username)
    update.message.reply_markdown_v2(
        f'Gracias {user.mention_markdown_v2()} por invitarme a jugar :)',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    # FIXME: contestar una ayuda como corresponde
    update.message.reply_text('Help!')


def game_words(update: Update, context: CallbackContext) -> None:
    """Recibe las palabras de cada player."""
    username = update.effective_user.username
    word = update.message.text
    player = PLAYER_BY_USERNAME[username]
    player.game.round_words[username].append(word)
    print("========== agregamos palabra", username, repr(word))

    # FIXME: luego de N palabras, tirarle de nuevo el tablero así no se le va demasiado arriba
    # update.message.reply_text()


def start_command(update: Update, context: CallbackContext) -> None:
    """Start the game."""
    entities = update.message.parse_entities()
    usernames = []
    for entity, text in entities.items():
        if entity.type == MessageEntity.MENTION:
            if text[0] == "@":
                text = text[1:]
            usernames.append(text)
    usernames.append(update.effective_user.username)
    print("====== usernames", usernames)

    players = []
    chat = update.effective_chat
    if chat in GAME_BY_CHAT:
        update.message.reply_text(
            "ERROR: ya hay un juego creado en este chat; hacer /terminar para cancelar el viejo")

    game = Game(players, chat)
    GAME_BY_CHAT[chat] = game
    for username in usernames:
        player = Player(username, game)
        players.append(player)
        PLAYER_BY_USERNAME[username] = player
    print(f"Nuevo juego creado para el chat {chat.title!r} con los jugadores {usernames}.")
    update.message.reply_text(
        "Juego arrancado, esperando que los jugadores digan /listo **por privado**.",
        parse_mode=ParseMode.MARKDOWN)
    # FIXME: este bold de acá arriba no anda :/

    # FIXME: acá podríamos decirle a cada jugador que le invitaron a jugar en el chat "tal" y que
    # tiene que decir /listo para arrancar -- esto va a funcionar si alguna vez el usuario le dio
    # /start al bot, y si no, no :shrug:


def time_up(*a, **k):
    """Se acabó el tiempo de la ronda."""
    print("===== time up", a, k)
    # necesitamos el juego!

    # avisamos a todes por privado que listo
    # avisamos en el público que listo
    # hacemos "resumen" de cómo vamos (revisar el doc)
    game.next_round()




def ready_command(update: Update, context: CallbackContext) -> None:
    """Soporte para comando /listo."""
    # FIXME: si lo dijeron por el público, resaltar que es POR PRIVADO (para poder hablarle al jug)
    username = update.effective_user.username

    # obtenemos el jugador y lo ponemos "listo"
    player = PLAYER_BY_USERNAME[username]
    player.ready = True
    player.chat = update.effective_user
    update.message.reply_text("Ok")

    # revisamos si tenemos que esperar a más jugadores
    game = player.game
    remaining = [p.username for p in game.players if not p.ready]
    print("========= esperando", remaining)

    if remaining:
        game.chat.send_message(f"{username} dijo ready, estamos esperando a {remaining}")
        return

    # arrancamos!
    game.chat.send_message(f"{username} dijo ready, todes listes, ¡arrancamos!")
    game.start()
    print("========== arrrrrrrrrancamosssssS")

    # creamos un tablero y lo mandamos al público y a todes les jugadores
    board = Board()
    print("======= nuevo tablero", board.distribution)
    renderized = board.render()
    game.chat.send_message(renderized)
    for player in game.players:
        # FIXME: revisar si esto anda
        player.chat.send_message(renderized)

    # NEXTWEEK
    # FIXME: marcar tiempo límite
    telegram.call_later(120, time_up)


def main(token: str) -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("comienzo", start_command))
    dispatcher.add_handler(CommandHandler("listo", ready_command))

    # para todas las palabras que tira un jugador por privado
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, game_words))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    print("Bot conectado, esperando para jugar.")
    updater.idle()


if __name__ == '__main__':
    credentials_filepath = sys.argv[1]  # FIXME: manejar correctamente los parámetros de ejecución
    auth = infoauth.load(credentials_filepath)
    token = auth["token"]
    main(token)