"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This Python module contains functions to run games for AI training purposes.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei
"""

from __future__ import annotations
from chess_game import ChessGame
import player


def run_games(n: int, red: player.Player, black: player.Player, visualize: bool = False) -> None:
    """Run n games using the given Players.

    visualize: print the board after each move

    Preconditions:
        - n >= 1
    """
    # This dictionary stores the initial state of the outcome
    stats = {'Red': 0, 'Black': 0, 'Draw': 0}
    results = []
    for i in range(1, n + 1):
        red.reload_tree()
        black.reload_tree()  # After each trial of game, reload the both trees from the xml

        winner, _ = run_game(red, black, visualize)
        stats[winner] += 1
        results.append(winner)

        # Print the ordinal number of the current game and its corresponding winner
        print(f'Game {i} winner: {winner}')

    for outcome in stats:
        # Print each outcome and their corresponding number of runs
        print(f'{outcome}: {stats[outcome]}/{n} ({100.0 * stats[outcome] / n:.2f}%)')


def run_game(red: player.Player, black: player.Player, visualize: bool = False) \
        -> tuple[str, list[str]]:
    """Run a Chinese Chess game between the two given players.

    Return the winner and list of moves made in the game.
    """
    game = ChessGame()

    move_sequence = []  # Use a blank list to store each move
    previous_move = None  # previous_move is the opponent player's most recent move
    current_player = red  # The red flag always goes first(It is part of rules of Chinese chess)
    while game.get_winner() is None:  # When id game is not finished, literates the while loop

        # After the current_player make the move, store it as the previous move
        previous_move = current_player.make_move(game, previous_move)
        # Change the game state
        game.make_move(previous_move)
        # Store each move in the game
        move_sequence.append(previous_move)

        if visualize:
            print(game)
        # Change between the current player and opponent player after each move
        if current_player is red:
            current_player = black
        else:  # if current_player is black
            current_player = red

    return game.get_winner(), move_sequence
