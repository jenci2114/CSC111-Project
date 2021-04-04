"""..."""

from __future__ import annotations
from chess_game import ChessGame
from player import Player

import copy


def run_games(n: int, red: Player, black: Player, visualize: bool = False) -> None:
    """Run n games using the given Players.

    visualize: print the board after each move

    Preconditions:
        - n >= 1
    """
    stats = {'Red': 0, 'Black': 0, 'Draw': 0}
    results = []
    for i in range(0, n):
        red_copy = copy.deepcopy(red)
        black_copy = copy.deepcopy(black)

        winner, _ = run_game(red_copy, black_copy, visualize)
        stats[winner] += 1
        results.append(winner)

        print(f'Game {i} winner: {winner}')

    for outcome in stats:
        print(f'{outcome}: {stats[outcome]}/{n} ({100.0 * stats[outcome] / n:.2f}%)')


def run_game(red: Player, black: Player, visualize: bool = False) -> tuple[str, list[str]]:
    """Run a Chinese Chess game between the two given players.

    Return the winner and list of moves made in the game.
    """
    game = ChessGame()

    move_sequence = []
    previous_move = None
    current_player = red
    while game.get_winner() is None:
        previous_move = current_player.make_move(game, previous_move)
        game.make_move(previous_move)
        move_sequence.append(previous_move)

        if visualize:
            print(game)

        if current_player is red:
            current_player = black
        else:  # if current_player is black
            current_player = red

    return game.get_winner(), move_sequence
