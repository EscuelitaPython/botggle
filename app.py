#!/usr/bin/env fades

# Copyright 2021-2022 Escuelita Python
# License: GPL-3
# More info: https://github.com/EscuelitaPython/botggle

"""Un juego como el Boggle para jugar en grupo via Telegram."""

import sys

import infoauth  # fades
from telegram import Update, MessageEntity, ParseMode  # fades python-telegram-bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from botggle.board import Board
from botggle.game import Game, NotActiveError
from botggle.messages import get_user_round_result

# duración de la ronda (en segundos)
ROUND_TIMEUP = 2 * 60

# duración del juego en puntos
SCORES_GAME_LIMIT = 50

# relaciona el username al player
PLAYER_BY_USERNAME = {}

# relaciona el chat al Game
GAME_BY_CHAT = {}


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    print(f"Bot invited to some chat by {user.username} ({user.full_name!r})")
    update.message.reply_text(f'Gracias {user.full_name} por invitarme a jugar :)')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def game_words(update: Update, context: CallbackContext) -> None:
    """Recibe las palabras de cada player."""
    username = update.effective_user.username
    text = update.message.text
    print("======= palabra", username, repr(text))
    player = PLAYER_BY_USERNAME.get(username)
    if player is None:
        print(f"==== ignoramos al usuario {username} por hablar fuera de orden")
        return

    try:
        player.game.add_text(username, text)
    except NotActiveError:
        player.chat.send_message(f"La palabra {text!r} llegó tarde")


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

    usernames_of_all_games = set()
    for game in GAME_BY_CHAT.values():
        usernames_of_all_games.update(p.username for p in game.players)
    in_other_games = set(usernames) & usernames_of_all_games
    if in_other_games:
        update.message.reply_text(
            f"ERROR: estes jugadores ya están en otro juego en otro chat: {in_other_games}")
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

    round_text_result = ["Como le fue a cada une:"]
    for username, resultwords in sorted(user_words.items()):
        text_result = get_user_round_result(resultwords)
        round_text_result.append(f"- {username}: {text_result}")
    game.chat.send_message("\n".join(round_text_result))

    game.chat.send_message(f"Progreso del juego: {round_scores} {game.full_scores}")

    # avanzamos el juego
    if max(game.full_scores.values(), default=0) < SCORES_GAME_LIMIT:
        for player in game.players:
            player.chat.send_message("Ya podemos arrancar la próxima ronda, escribí /listo")
        game.next_round()
        return

    max_score = max(game.full_scores.values())
    winners = [username for username, score in game.full_scores.items() if score == max_score]
    game.chat.send_message(f"Juego terminado!! Ganó {winners}")

    # limpiamos las globales
    del GAME_BY_CHAT[game.chat]
    for player in game.players:
        del PLAYER_BY_USERNAME[player.username]


def ready_command(update: Update, context: CallbackContext) -> None:
    """Soporte para comando /listo."""
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
    credentials_filepath = sys.argv[1]
    auth = infoauth.load(credentials_filepath)
    token = auth["token"]
    main(token)
