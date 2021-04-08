"""Player"""

from typing import Optional
import random
from chess_game import ChessGame, _Piece, calculate_absolute_points
from game_tree import GameTree, load_game_tree, xml_to_tree


class Player:
    """An abstract class representing a Chinese Chess AI.

    This class can be subclassed to implement different strategies for playing chess.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    #   - _xml_file: the xml file that stores the game tree
    _game_tree: Optional[GameTree]
    _xml_file: str

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        raise NotImplementedError

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
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

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        return  # Does nothing


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

    def __init__(self, xml_file: str = '') -> None:
        """Initialize this player.

        Preconditions:
            - xml file contains a game tree at the initial state (root is '*')
        """
        self._xml_file = xml_file
        self.reload_tree()

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
            # no branches available so we search for possible moves and make a random move
            possible_moves = game.get_valid_moves()
            self._game_tree = None
            return random.choice(possible_moves)
        else:
            subtrees = self._game_tree.get_subtrees()
            self._game_tree = random.choice(subtrees)
            return self._game_tree.move

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = None


class GreedyTreePlayer(Player):
    """A Chinese Chess player that chooses a move based on the database,
    using Minimax algorithm.

    If the player is red, then it will choose a move that has highest winning
    probability for red.

    If the player is black, then it will choose a move that has lowest winning
    probability for red.
    """

    def __init__(self, xml_file: str) -> None:
        """Initialize this player.

        Preconditions:
            - xml file contains a game tree at the initial state (root is '*')
        """
        self._xml_file = xml_file
        self.reload_tree()

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

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = None


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
        self._game_tree = GameTree()
        self._depth = depth

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        if previous_move is None:
            pass
        else:
            self._game_tree = GameTree(previous_move, True)

        self._alpha_beta(game, self._game_tree, self._depth,
                         -1000000, 1000000, game.is_red_move())
        best_moves = sorted(self._game_tree.get_subtrees(),
                            key=lambda x: x.relative_points, reverse=True)
        return best_moves[0].move

    def _alpha_beta(self, game: ChessGame, tree: GameTree, depth: int, alpha: int, beta: int,
                    self_is_red: bool) -> int:
        """The alpha-beta pruning algorithm that will be used when this player makes a move.

        Note: +- 1000000 will be used to represent +- infinity
        """
        if depth == 0 or game.get_winner() is not None:
            value = calculate_absolute_points(game.get_board())
            tree.relative_points = value
            return value

        if self_is_red == game.is_red_move():
            value = -1000000
            for move in game.get_valid_moves():
                subtree = GameTree(move, self_is_red)
                game_after_move = game.copy_and_make_move(move)
                value = max(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta, self_is_red))
                alpha = max(alpha, value)
                tree.add_subtree(subtree)
                if alpha >= beta:
                    break  # beta cutoff

            tree.relative_points = value
            return value
        else:  # Opponent's move
            value = 1000000
            for move in game.get_valid_moves():
                subtree = GameTree(move, not self_is_red)
                game_after_move = game.copy_and_make_move(move)
                value = min(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta, self_is_red))
                beta = min(beta, value)
                tree.add_subtree(subtree)
                if beta <= alpha:
                    break  # alpha cutoff

            tree.relative_points = value
            return value

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        self._game_tree = GameTree()


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
    _depth: int

    def __init__(self, depth: int, xml_file: str) -> None:
        """Initialize this player.

        Preconditions:
            - depth >= 1
            - xml file contains a game tree at the initial state (root is '*')
        """
        self._depth = depth
        self._xml_file = xml_file
        self.reload_tree()

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        # TODO: implement the method

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = GameTree()


if __name__ == '__main__':
    # To avoid RecursionError
    import sys
    sys.setrecursionlimit(10000)

    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1136'],
    # })
