#!/usr/bin/env fades

# Copyright 2021 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

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
from telegram import Update, ForceReply, MessageEntity, ParseMode  # fades python-telegram-bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from botggle.board import Board
from botggle.game import Game, NotActiveError


# TOISSUE: mejorar rae_words.txt para incorporar cosas que faltan:
# - pode (podé, podar en pasado)
# - matad ("vosotros matad!")

# duración de la ronda (en segundos)
ROUND_TIMEUP = 30  # FIXME: corregir el default a 3 * 60

# duración del juego en puntos
SCORES_GAME_LIMIT = 50

# TOISSUE: que las dos vars de arriba sean configurables (si el juego no está activo) pasando
#  /config tiempo_ronda=N
#  /config puntaje_objetivo=N
#  /config rondas_objetivo=N
# (los ultimos dos se pisan mutuamente, el default es por puntaje)
# cuando el bot es invitado al canal dice cuales son sus defaults

# relaciona el username al player
PLAYER_BY_USERNAME = {}

# relaciona el chat al Game
GAME_BY_CHAT = {}


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
    # TOISSUE: contestar una ayuda como corresponde
    update.message.reply_text('Help!')


def game_words(update: Update, context: CallbackContext) -> None:
    """Recibe las palabras de cada player."""
    username = update.effective_user.username
    text = update.message.text
    player = PLAYER_BY_USERNAME.get(username)
    if player is None:
        print(f"==== ignoramos al usuario {username} por hablar fuera de orden")
        return

    try:
        player.game.add_text(username, text)
    except NotActiveError:
        player.chat.send_message(f"La palabra {text!r} llegó tarde")

    # TOISSUE: luego de N palabras, tirarle de nuevo el tablero así no se le va demasiado arriba


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

    chat = update.effective_chat
    if chat in GAME_BY_CHAT:
        update.message.reply_text(
            "ERROR: ya hay un juego creado en este chat; hacer /terminar para cancelar el viejo")
        return

    game = Game(chat)
    GAME_BY_CHAT[chat] = game
    for username in usernames:
        player = game.add_player(username)
        PLAYER_BY_USERNAME[username] = player

    print(f"Nuevo juego creado para el chat {chat.title!r} con los jugadores {usernames}.")
    print("======= full scores", game.full_scores)
    update.message.reply_text(
        "Juego arrancado, esperando que los jugadores digan /listo **por privado**.",
        parse_mode=ParseMode.MARKDOWN)
    # TOISSUE: este bold de acá arriba no anda :/

    # FIXME: acá podríamos decirle a cada jugador que le invitaron a jugar en el chat "tal" y que
    # tiene que decir /listo para arrancar -- esto va a funcionar si alguna vez el usuario le dio
    # /start al bot, y si no, no :shrug:


def time_up(context):
    """Se acabó el tiempo de la ronda."""
    print("===== time up", context)
    payload = context.job.context
    game = payload['game']
    game.stop_round()

    # avisamos a todes por privado que listo
    for player in game.players:
        player.chat.send_message("Se acabó el tiempo")

    # avisamos en el público que terminó la ronda
    game.chat.send_message("¡Se terminó la ronda!")

    # mostrar resumen de cómo va el partido
    user_words = game.evaluate_words()
    round_scores = game.summarize_scores(user_words)

    # TOISSUE: mostrar esto lindo
    game.chat.send_message(f"Como le fue a cada une: {user_words}")
    # ejemplo de mostrado 1:
    # Diego: coma, punto (repetidas: zaraza; no en el diccionario: punno)
    # Facundo: cumo, panto (repetidas: zaraza)
    # Leandro: pinto (no en el tablero: xuxo; no en el diccionario: panta)
    # Ej 2
    # Leandro: casa (3), comienzo (7), coso (emoji de repetido), cruzo (⛔️) - Total 10.

    # TOISSUE: mostrar esto lindo
    game.chat.send_message(f"Progreso del juego: {round_scores} {game.full_scores}")

    # avanzamos el juego
    if max(game.full_scores.values(), default=0) < SCORES_GAME_LIMIT:
        for player in game.players:
            player.chat.send_message("Ya podemos arrancar la próxima ronda, escribí /listo")
        game.next_round()
        return

    print("========== ganó FULANO!!!")
    # FIXME: mostrar bien quien ganó, y terminar el juego (onda game.finish()???)
    # NEXTWEEK -- y charlar sobre qué pasa al ejecutar dos juegos en distintos canales
    # -- y validar que un jugador NO pueda estar en dos juegos al mismo tiempo

    # limpiamos las globales
    del GAME_BY_CHAT[game.chat]
    for player in game.players:
        del PLAYER_BY_USERNAME[player.username]


def ready_command(update: Update, context: CallbackContext) -> None:
    """Soporte para comando /listo."""
    # FIXME: si lo dijeron por el público, resaltar que es POR PRIVADO (para poder hablarle al jug)
    username = update.effective_user.username
    print(f"El usuario {username} dijo listo")

    # obtenemos el jugador y lo ponemos "listo"
    try:
        player = PLAYER_BY_USERNAME[username]
    except KeyError:
        update.message.reply_text("No hay un juego activo o no te invitaron :(")
        return
    player.ready = True
    player.chat = update.effective_user
    update.message.reply_text("Ok")

    # revisamos si tenemos que esperar a más jugadores
    game = player.game
    remaining = [p.username for p in game.players if not p.ready]

    if remaining:
        game.chat.send_message(f"{username} dijo ready, estamos esperando a {remaining}")
        return

    # arrancamos! avisamos, creamos un nuevo tablero para la ronda y se lo pasamos a game
    game.chat.send_message(f"{username} dijo ready, todes listes, ¡arrancamos!")
    board = Board()
    game.start_round(board)

    # creamos un tablero y lo mandamos al público y a todes les jugadores
    renderized = board.render()
    game.chat.send_message(renderized)
    for player in game.players:
        player.chat.send_message(renderized)

    context.job_queue.run_once(time_up, ROUND_TIMEUP, context={'game': game})


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
    # FIXME: implementar un "terminar" para cancelar el juego
    # TOISSUE: hacer un comando /g o /grilla que muestre la grilla
    # FIXME: hacer un comando /status que diga si hay un juego creado o no, y con qué jugadores

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
    credentials_filepath = sys.argv[1]  # TOISSUE: manejar correctamente los params de ejecución
    auth = infoauth.load(credentials_filepath)
    token = auth["token"]
    main(token)
