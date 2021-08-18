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

import sys

import infoauth  # fades
from telegram import Update, ForceReply, MessageEntity  # fades python-telegram-bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


DICE_TABLE = {}
for simple, squared in zip(range(65, 65 + 26), range(127280, 127280 + 26)):
    DICE_TABLE[chr(simple)] = chr(squared)
DICE_TABLE["CH"] = "Ch"

DICE_DISTRIBUTION = [
    ("A", 5)
    # FIXME: copiar lo del doc (no es lineal, va según dado!!!!)
]

# relaciona el mention al player
PLAYER_BY_MENTION = {}

# relaciona el chat al Game
GAME_BY_CHAT = {}


class Player:
    def __init__(self, mention, game):
        self.mention = mention
        self.ready = False
        self.game = game


class Game:
    def __init__(self, players, chat):
        self.players = players
        self.chat = chat


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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    # FIXME: esto lo vamos a modificar luego para recibir las palabras de les jugadores
    print(f"==== echo from={update.effective_user.username} {update.message.text!r}")
    update.message.reply_text(update.message.text)


def start_command(update: Update, context: CallbackContext) -> None:
    """Start the game."""
    entities = update.message.parse_entities()
    mentions = []
    for entity, text in entities.items():
        if entity.type == MessageEntity.MENTION:
            mentions.append(text)
    mentions.append(update.effective_user.username)  # FIXME: acá tenemos mezclados con y sin @
    print("====== mentions", mentions)

    players = []
    chat = update.effective_chat
    if chat in GAME_BY_CHAT:
        update.message.reply_text(
            "ERROR: ya hay un juego creado en este chat; hacer /terminar para cancelar el viejo")

    game = Game(players, chat)
    GAME_BY_CHAT[chat] = game
    for mention in mentions:
        player = Player(mention, game)
        players.append(player)
        PLAYER_BY_MENTION[mention] = player
    print(f"Nuevo juego creado para el chat {chat.title!r} con los jugadores {mentions}.")
    update.message.reply_text(
        "Juego arrancado, esperando que los jugadores digan /listo **por privado**.")

    # FIXME: acá podríamos decirle a cada jugador que le invitaron a jugar en el chat "tal" y que
    # tiene que decir /listo para arrancar -- esto va a funcionar si alguna vez el usuario le dio
    # /start al bot, y si no, no :shrug:


def ready_command(update: Update, context: CallbackContext) -> None:
    """Soporte para comando /listo."""
    # FIXME: si lo dijeron por el público, resaltar que es POR PRIVADO (para poder hablarle al jug)
    breakpoint()  # NEXTWEEK

# para hablar con el usuario:
# (Pdb) update.effective_user.send_message("Hola cacerola")
# <telegram.message.Message object at 0x7f31001d7040>


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

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

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
