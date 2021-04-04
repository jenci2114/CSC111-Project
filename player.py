"""Player"""

from typing import Optional
import random
from chess_game import ChessGame
from game_tree import GameTree, load_game_tree


class Player:
    """An abstract class representing a Chinese Chess AI.

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
    """A Chinese Chess player that plays randomly based on a given GameTree.

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
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # no branches available so we search for possible moves and make a random move
            possible_moves = game.get_valid_moves()
            self._game_tree = None
            return random.choice(possible_moves)
        else:
            subtrees = self._game_tree.get_subtrees()
            self._game_tree = random.choice(subtrees)
            return self._game_tree.move


class GreedyTreePlayer(Player):
    """A Chinese Chess player that chooses a move based on the database,
    using Minimax algorithm.

    If the player is red, then it will choose a move that has highest winning
    probability for red.

    If the player is black, then it will choose a move that has lowest winning
    probability for red.

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
        """
        if self._game_tree is not None and previous_move is not None:
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # no branches available so we make a random move
            possible_moves = game.get_valid_moves()
            self._game_tree = None
            return random.choice(possible_moves)
        else:
            subtrees = self._game_tree.get_subtrees()
            red_win = [sub.red_win_probability for sub in subtrees]
            if self._game_tree.is_red_move:
                maximum = max(red_win)
                maximum_index = red_win.index(maximum)
                max_subtree = subtrees[maximum_index]
                self._game_tree = max_subtree
            else:  # if playing as black
                minimum = min(red_win)
                minimum_index = red_win.index(minimum)
                min_subtree = subtrees[minimum_index]
                self._game_tree = min_subtree

            return self._game_tree.move


class ExploringPlayer(Player):
    """A Chinese Chess player that uses alpha-beta algorithm to explore all possible moves
     and find a locally optimal move.

     Note: This player does not need an existing tree to select a moves from.
     Instead, it will explore all recent moves and choose a locally optimal.

    """
    # Private Instance Attributes:
    #   - _depth: the number of turns the player will explore
    _depth: int

    def __init__(self, depth: int) -> None:
        """Initialize this player.

        Preconditions:
            - depth >= 1
        """
        self._depth = depth

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        # TODO: implement the method


class LearningPlayer(Player):
    """A Chinese Chess player that uses alpha-beta algorithm to explore some possible moves
     based on its experience and find a locally optimal move. It's a player which has some
     previous experience in Chinese Chess but has its own idea to explore a better strategy.

     The new moves this player will explore are...

     Note: This player should not be totally new to Chinese Chess. It has some previous
     experience in Chinese Chess, and therefore its game tree should not be empty.

    """
    # Private Instance Attributes:
    #   - _depth: the number of turns the player will explore
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    _depth: int
    _game_tree: GameTree

    def __init__(self, depth: int, game_tree: GameTree) -> None:
        """Initialize this player.

        Preconditions:
            - depth >= 1
            - game_tree represents a game tree at the initial state (root is '*')
        """
        self._depth = depth

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        # TODO: implement the method


if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1136'],
    # })
