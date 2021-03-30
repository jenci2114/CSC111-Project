"""Player"""

from typing import Optional
import random
from chess_game import ChessGame
from game_tree import GameTree, load_game_tree


class Player:
    """An abstract class representing a Minichess AI.

    This class can be subclassed to implement different strategies for playing chess.
    """

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        raise NotImplementedError


class RandomPlayer(Player):
    """A Chinese Chess AI whose strategy is always picking a random move."""

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        possible_moves = game.get_valid_moves()
        return random.choice(possible_moves)


class RandomTreePlayer(Player):
    """A Chinese player that plays randomly based on a given GameTree.

    This player uses a game tree to make moves, descending into the tree as the game is played.
    On its turn:

        1. First it updates its game tree to its subtree corresponding to the move made by
           its opponent. If no subtree is found, its game tree is set to None.
        2. Then, if its game tree is not None, it picks its next move randomly from among
           the subtrees of its game tree, and then reassigns its game tree to that subtree.
           But if its game tree is None or has no subtrees, the player picks its next move randomly,
           and then sets its game tree to None.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    _game_tree: Optional[GameTree]

    def __init__(self, game_tree: GameTree) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree represents a game tree at the initial state (root is '*')
        """
        self._game_tree = game_tree

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game

        >>> tree = load_game_tree('data/small_sample.csv')
        >>>
        """
        if self._game_tree is not None and previous_move is not None:
            found = 0

            for subtree in self._game_tree.get_subtrees():
                if subtree.move == previous_move:
                    self._game_tree = subtree
                    found = 1  # subtree is found
                    break

            if found == 0:  # no subtree is found
                self._game_tree = None

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # no choice for move so we make a random move
            possible_moves = game.get_valid_moves()
            self._game_tree = None
            return random.choice(possible_moves)
        else:
            subtrees = self._game_tree.get_subtrees()
            self._game_tree = random.choice(subtrees)
            return self._game_tree.move
