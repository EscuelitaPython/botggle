#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

""" Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update, ForceReply, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


DICE_TABLE = {}
for simple, squared in zip(range(65, 65 + 26), range(127280, 127280 + 26)):
    DICE_TABLE[chr(simple)] = chr(squared)
DICE_TABLE["CH"] = "Ch"


DICE_DISTRIBUTION = [
    ("A", 5)
    # FIXME: copiar lo del doc (no es lineal, va según dado!!!!)
]



# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
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

# para hablar con el usuario:
# (Pdb) update.effective_user.send_message("Hola cacerola")
# <telegram.message.Message object at 0x7f31001d7040>


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1930545249:AAFUO4cJVdjakgBcRgbExz-yZeYxDvNDn48")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("comienzo", start_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
