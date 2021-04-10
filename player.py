"""Player"""

from typing import Optional
import random
from chess_game import ChessGame, _Piece, calculate_absolute_points
from game_tree import GameTree, load_game_tree, xml_to_tree, tree_to_xml
import multiprocessing
import random
import time
import os


GAMES = []
PROCESSES = 9


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
    """A Chinese Chess player that chooses a move based on the database, choosing moves
    based on win probability.

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
            black_win = [sub.black_win_probability for sub in subtrees]
            if self._game_tree.is_red_move:
                maximum = max(red_win)
                maximum_index = red_win.index(maximum)
                max_subtree = subtrees[maximum_index]
                self._game_tree = max_subtree
            else:  # if playing as black
                maximum = min(black_win)
                minimum_index = black_win.index(maximum)
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

    def __init__(self, depth: int, tree: GameTree = GameTree()) -> None:
        """Initialize this player.

        Preconditions:
            - depth >= 1
        """
        self._game_tree = tree
        self._depth = depth

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move given the current game.

        previous_move is the opponent player's most recent move, or None if no moves
        have been made.

        Preconditions:
            - There is at least one valid move for the given game
        """
        start_time = time.time()
        if previous_move is None:
            pass
        else:
            self._game_tree = GameTree(previous_move, game.is_red_move())

        # Non-multiprocessing version
        # best_score = self._alpha_beta(game, self._game_tree, self._depth, -1000000, 1000000)

        best_score = self._alpha_beta_multi(game, self._depth, -1000000, 1000000)
        best_moves = [s.move for s in self._game_tree.get_subtrees()
                      if s.relative_points == best_score]
        chosen_move = random.choice(best_moves)

        GAMES.append(ChessGame(game.get_board(), game.is_red_move()))
        print(f'Time taken to make this move: {time.time() - start_time} seconds')
        print('Respective points for each move:')
        print({s.move: s.relative_points for s in self._game_tree.get_subtrees()})
        print(f'Move chosen: {chosen_move}')
        return chosen_move

    def _alpha_beta(self, game: ChessGame, tree: GameTree, depth: int,
                    alpha: int, beta: int) -> int:
        """The alpha-beta pruning algorithm that will be used when this player makes a move.

        Note: +- 1000000 will be used to represent +- infinity
        """
        if depth == 0:
            value = calculate_absolute_points(game.get_board())
            tree.relative_points = value
            return value
        elif game.get_winner() is not None:
            if game.get_winner() == 'Red':
                side = 1
            elif game.get_winner() == 'Black':
                side = -1
            else:  # draw
                side = 0
            value = calculate_absolute_points(game.get_board()) + depth * 5000 * side
            tree.relative_points = value
            return value

        if game.is_red_move():
            value = -1000000
            for move in game.get_valid_moves():
                subtree = GameTree(move, True)
                game_after_move = game.copy_and_make_move(move)
                value = max(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                alpha = max(alpha, value)
                tree.add_subtree(subtree)
                if alpha >= beta:
                    break  # beta cutoff

            tree.relative_points = value
            return value
        else:  # Black's move
            value = 1000000
            for move in game.get_valid_moves():
                subtree = GameTree(move, False)
                game_after_move = game.copy_and_make_move(move)
                value = min(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                beta = min(beta, value)
                tree.add_subtree(subtree)
                if beta <= alpha:
                    break  # alpha cutoff

            tree.relative_points = value
            return value

    def _alpha_beta_multi(self, game: ChessGame, depth: int,
                          alpha: int, beta: int) -> int:
        """The alpha-beta pruning algorithm that is functionally identical to the
        above implementation, except this one uses multiprocessing.

        Warning: Do NOT recurse on this method, recurse on the non-multiprocessing method.

        Preconditions:
            - depth > 0
            - Game has not finished
        """
        processes = []
        moves = game.get_valid_moves()
        per_process, last_process = divmod(len(moves), PROCESSES - 1)
        start, end = 0, per_process

        for i in range(PROCESSES):
            process = multiprocessing.Process(target=self._alpha_beta_process,
                                              args=(game, depth, alpha, beta, start, end))
            processes.append(process)
            process.start()
            if i != PROCESSES - 2:
                start, end = end, end + per_process
            else:
                start, end = end, end + last_process

        for p in processes:
            p.join()

        for i in range(len(moves)):
            subtree = xml_to_tree(f'process{i}.xml')
            self._game_tree.add_subtree(subtree)
            os.remove(f'process{i}.xml')

        if game.is_red_move():
            value = max(s.relative_points for s in self._game_tree.get_subtrees())
        else:
            value = min(s.relative_points for s in self._game_tree.get_subtrees())
        self._game_tree.relative_points = value
        return value

    def _alpha_beta_process(self, game: ChessGame, depth: int,
                            alpha: int, beta: int, start: int, end: int) -> None:
        """This helper method will be called PROCESSES number of times, performing
        the alpha-beta pruning algorithm over multiple processes.

        Preconditions:
            - must be called by _alpha_beta_multi
        """
        if game.is_red_move():
            value = -1000000
            for i in range(start, end):
                move = game.get_valid_moves()[i]
                subtree = GameTree(move, True)
                game_after_move = game.copy_and_make_move(move)
                value = max(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                alpha = max(alpha, value)

                tree_to_xml(subtree, f'process{i}.xml')

                if alpha >= beta:
                    break  # beta cutoff
        else:
            value = 1000000
            for i in range(start, end):
                move = game.get_valid_moves()[i]
                subtree = GameTree(move, False)
                game_after_move = game.copy_and_make_move(move)
                value = min(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                beta = min(beta, value)

                tree_to_xml(subtree, f'process{i}.xml')

                if beta <= alpha:
                    break  # alpha cutoff

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        self._game_tree = GameTree()

    def get_tree(self) -> GameTree:
        """Return self._game_tree."""
        return self._game_tree


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
        if self._game_tree is not None and previous_move is not None:
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # no branches available so we explore new moves
            explore = ExploringPlayer(self._depth)
            return explore.make_move(game, previous_move)
        else:
            subtrees = self._game_tree.get_subtrees()
            red_win = [sub.red_win_probability for sub in subtrees]
            black_win = [sub.black_win_probability for sub in subtrees]
            if self._game_tree.is_red_move:
                maximum = max(red_win)
                if maximum > 0:
                    maximum_index = red_win.index(maximum)
                    max_subtree = subtrees[maximum_index]
                    self._game_tree = max_subtree
                    return self._game_tree.move
                else:
                    explore = ExploringPlayer(self._depth)
                    return explore.make_move(game, previous_move)
            else:  # if playing as black
                maximum = max(black_win)
                if maximum > 0:
                    maximum_index = black_win.index(maximum)
                    max_subtree = subtrees[maximum_index]
                    self._game_tree = max_subtree
                    return self._game_tree.move
                else:
                    explore = ExploringPlayer(self._depth)
                    return explore.make_move(game, previous_move)

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = GameTree()


class Human(Player):
    """A human Chinese Chess player."""

    def make_move(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """Make a move based on the input."""
        print('Please make your move: ')
        move = input()
        while move not in game.get_valid_moves():
            print('Invalid move.')
            print('Please make your move: ')
            move = input()

        return move

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        return  # Does nothing


class AIBlack(Player):
    """An AI chess player that always play as Black."""
    # Private Instance Attributes:
    #   - _depth: the number of turns the player will explore
    #   - _current_tree: the GameTree consisting of all moves searched by this player
    #   - _current_subtree: offspring of _current_tree that keeps track of the current game move

    # Private Representation Invariants:
    #   - self._current_tree is not None
    _depth: int
    _current_tree: GameTree
    _current_subtree: GameTree

    def __init__(self, xml_file: str, depth: int):
        """Initialize this player.

        Preconditions:
            - xml_file can be converted to a tree that has nodes for the Black side
        """
        self._xml_file = xml_file
        self._depth = depth
        self._current_tree = GameTree()
        self._current_subtree = self._current_tree

        self.reload_tree()

    def make_move(self, game: ChessGame, previous_move: str) -> str:
        """Make a move as the black player."""

        new_subtree = GameTree(previous_move, False)

        if self._game_tree is not None:
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            explorer = ExploringPlayer(self._depth)
            move = explorer.make_move(game, previous_move)
            new_subtree = explorer.get_tree()
            self._current_subtree.add_subtree(new_subtree)
            self._current_subtree = new_subtree

            return move
        else:
            subtrees = self._game_tree.get_subtrees()
            points = [sub.relative_points for sub in subtrees]
            maximum = max(points)
            maximum_index = points.index(maximum)
            max_subtree = subtrees[maximum_index]
            self._game_tree = max_subtree
            self._current_subtree.add_subtree(max_subtree)
            self._current_subtree = max_subtree
            return self._game_tree.move

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = None


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
