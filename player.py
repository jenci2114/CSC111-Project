"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This Python module contains all Player classes,
where each subclass of Player represents a different
strategy the computer will use in Chinese Chess.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei
"""
from __future__ import annotations
import multiprocessing
import random
import os
from typing import Optional
import game_run
from chess_game import ChessGame, calculate_absolute_points
from game_tree import GameTree, xml_to_tree, tree_to_xml

PROCESSES = 9
EPSILON = 0.2


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
    """A Chinese Chess player that chooses random moves."""

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


class ExploringPlayer(Player):
    """A Chinese Chess player that uses alpha-beta algorithm to explore all possible moves
     and find a locally optimal move.( The explanation of alpha-beta algorithm will be
     explained below)

     If there is more than one optimal move, then randomly choose a move with the highest
     relative point.

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
        if previous_move is None:
            pass
        else:
            self._game_tree = GameTree(previous_move, game.is_red_move())

        # Non-multiprocessing version
        # best_score = self._alpha_beta(game, self._game_tree, self._depth, -1000000, 1000000)

        # Obtain subtrees with the best point
        best_score = self._alpha_beta_multi(game, self._depth, -1000000, 1000000)
        subtrees = self._game_tree.get_subtrees()
        candidate_subtrees = [s for s in subtrees if s.relative_points == best_score]

        if game.is_red_move():
            # Obtain subtrees with the best self win probability
            max_probability = max(s.red_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.red_win_probability == max_probability]

            # Obtain subtrees with the lowest opponent win probability
            min_probability = min(s.black_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.black_win_probability == min_probability]
        else:  # not game.is_red_move()
            # Obtain subtrees with the best self win probability
            max_probability = max(s.black_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.black_win_probability == max_probability]

            # Obtain subtrees with the lowest opponent win probability
            min_probability = min(s.red_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.red_win_probability == min_probability]

        # If there are still ties, choose one randomly
        chosen_move = random.choice(candidate_subtrees).move

        return chosen_move

    def _alpha_beta(self, game: ChessGame, tree: GameTree, depth: int,
                    alpha: int, beta: int) -> int:
        """The alpha-beta pruning algorithm that will be used when this player makes a move.

        To understand what is an alpha-beta algorithm, we first need to know what is a Minimax
        algorithm. In this algorithm, we have two players, which are Maximizer and Minimizer.
        Maximizer tries to get the highest score while Minimizer tries to get the lowest score.
        In our game tree, we we have to go all the way through the leaves to reach the terminal
        nodes. At the terminal node, we calculate the terminal values by the function "calculate_
        absolute_points". we will compare those value and backtrack the tree until the initial
        state occurs. We will illustrate this concept with the below example (the tree drawing):

        At the beginning, the highest score equals negative infinity (because player A has
        found no moves yet) while the lowest score equals positive infinity (because player
        B has found no moves yet).

        Now, first we find the value for the Minimizer, its initial value is positive infinity,
        so we will compare each value in terminal state with initial value of Minimizer and
        determines the higher nodes values. It will find the minimum among the all.

         In the next step, it's a turn for Maximizer, so it will compare all nodes value with
         negative infinity, and will find the 2rd layer node values.

        Now it's a turn for Minimizer, and it will again choose the minimum of all nodes value
        and find the minimum value for the root node. In this tree, there are only 4 layers,
        hence we reach immediately to the root node.

                                                  6                                Maximum
                                             /    |   \
                                          /       |      \
                                       /          |         \
                                    /             |            \
                                 /                |               \
                               3                  6                5               Minimum
                              /\                 | \              /\
                             /  \                |  \            /  X
                           /     \               |   \          /    \
                         5        3              6    7        5      ?            Maximum
                        / \        \            / \    \       |     | \
                      /    \        \         /    \    \      |     |  \
                    /       \        \      /       \    \     |     |   \
                  5         4         3    6         6    7    5     ?    ?        Minimum
                 /|        /| \       |    |       / |    |    |    | \    \
               /  |      /  |  X      |    |      /  X    |    |    |  \    \
              /   |     /   |   \     |    |     /   |    |    |    |   \    \
             5    6    7    4    ?    3    6    6    ?    7    5    ?    ?    ?    Maximum


        In alpha-beta pruning algorithm, alpha represents the highest score Maximizer searches for
        while beta represents the lowest score Minimizer searches for. At the beginning, Alpha
        equals negative infinity (because the Maximizer has found no moves yet) while beta equals
        positive infinity (because the Minimizer has found no moves yet). We will use the above
        tree as an example.

        Now, first we find the value for the Minimizer, its initial value is positive infinity,
        so we will first compare 5 (the leftmost node of the leftmost branch in that layer with
        initial value of Minimizer and determines the higher nodes values, which is 5 in this case.
        Then we can know that the Minimizer will be less than or equal to 5. When we search for
        another node of the branch, we find that 6 is larger than 5, so the minimizer will choose 5
        When we search for the branch right to the leftmost branch, the Minimizer first choose 7,
        and then choose 4 (by comparing 7 to 4). Since for the upper level, Maximizer will choose
        the greater value, and we already know that 5 is larger than 4, so no matter what is the
        rightmost node of the second branch, the Maximizer will choose 5 from the leftmost branch.
        Thus, we can prune the rightmost subtree of the second branch. By repeating above steps
        again and again, we will get the graph above.

        Through pruning the subtrees, we will get a result no differ from what we would get
        using Minimax; however, since we are not evaluating some of the nodes by pruning them,
        the alpha-beta algorithm runs faster than the Minimax algorithm.

        The ? subtrees don't need to be explored (when moves are evaluated from left to
        right), since it is known that the group of subtrees as a whole yields the value of an
        equivalent subtree or worse, and as such cannot influence the final result. The max and min
        levels represent the turn of the player and the adversary, respectively.

        Note: +- 1000000 will be used to represent +- infinity

        Preconditions:
            - depth >= 0
        """
        if game.get_winner() is not None:
            if game.get_winner() == 'Red':
                side = 1
                tree.red_win_probability = 1.0
                tree.black_win_probability = 0.0
            elif game.get_winner() == 'Black':
                side = -1
                tree.black_win_probability = 1.0
                tree.red_win_probability = 0.0
            else:  # draw
                side = 0
                tree.red_win_probability = 0.0
                tree.black_win_probability = 0.0
            value = calculate_absolute_points(game.get_board()) + depth * 5000 * side
            # if the game ends while there are still 'remaining' depths, add incentive
            # for the player to win game quickly/add disincentive for player to prevent the
            # other from winning quickly
            tree.relative_points = value
            return value
        elif depth == 0:
            value = calculate_absolute_points(game.get_board())
            tree.relative_points = value
            return value

        if game.is_red_move():
            value = -1000000
            for move in game.get_valid_moves():
                subtree = GameTree(move, False)
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
                subtree = GameTree(move, True)
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

        Note: Multiprocessing is the use of two or more central processing units (CPUs)
        within a single computer system.

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
            if i != PROCESSES - 2:  # if it is not the end of the process
                start, end = end, end + per_process
            else:  # until the last process
                start, end = end, end + last_process

        for p in processes:
            p.join()

        for i in range(len(moves)):
            subtree = xml_to_tree(f'temp/process{i}.xml')  # store the temp tree
            self._game_tree.add_subtree(subtree)
            os.remove(f'temp/process{i}.xml')  # after adding the subtree, remove the temp tree

        # similar to alpha-beta
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
        possible_moves = game.get_valid_moves()
        if game.is_red_move():
            value = -1000000
            for i in range(start, end):
                move = possible_moves[i]
                subtree = GameTree(move, False)
                game_after_move = game.copy_and_make_move(move)
                value = max(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                alpha = max(alpha, value)

                tree_to_xml(subtree, f'temp/process{i}.xml')

                if alpha >= beta:
                    break  # beta cutoff
        else:
            value = 1000000
            for i in range(start, end):
                move = possible_moves[i]
                subtree = GameTree(move, True)
                game_after_move = game.copy_and_make_move(move)
                value = min(value, self._alpha_beta(game_after_move, subtree, depth - 1,
                                                    alpha, beta))
                beta = min(beta, value)

                tree_to_xml(subtree, f'temp/process{i}.xml')

                if beta <= alpha:
                    break  # alpha cutoff

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        self._game_tree = GameTree()

    def get_tree(self) -> GameTree:
        """Return self._game_tree."""
        return self._game_tree

    def get_two_depth_tree(self) -> GameTree:
        """Return self._game_tree with only one depth of subtrees."""
        for subtree in self._game_tree.get_subtrees():
            subtree.clean_subtrees()
        return self._game_tree


class LearningPlayer(Player):
    """A Chinese Chess player that can play based on a game tree and also explore new moves.

    We use EPSILON to represent its exploring rate:
        - if the largest win probability of moves in subtrees > EPSILON, then the player will
          choose this move
        - else, the player will use the alpha-beta algorithm to explore a locally optimal move
          with depth of self._depth

    Note: This player will be used for training.

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
            - self._game_tree is not None
        """
        if previous_move is not None:
            # update the game tree with the previous move
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # no branches available so the player will explore new moves
            # then the player will perform the same as ExploringPlayer
            return self._change_to_explore(game, previous_move)
        else:  # check the win probability
            if self._game_tree.is_red_move:
                if self._game_tree.red_win_probability > EPSILON:
                    # the best move reaches our expectation and thus
                    # the player will find the best move in subtrees
                    subtrees = self._game_tree.get_subtrees()
                    # list of red win probabilities corresponding to subtrees
                    subtrees_win_prob_red = [sub.red_win_probability for sub in subtrees]
                    maximum_index = subtrees_win_prob_red.index(self._game_tree.red_win_probability)
                    max_subtree = subtrees[maximum_index]
                    # update the game tree
                    self._game_tree = max_subtree
                    return self._game_tree.move
                else:  # self._game_tree.red_win_probability <= EPSILON
                    # the player needs to explore locally optimal moves
                    # the player will perform the same as ExploringPlayer
                    return self._change_to_explore(game, previous_move)
            else:  # if playing as black
                # similar to the previous case
                if self._game_tree.black_win_probability > EPSILON:
                    subtrees = self._game_tree.get_subtrees()
                    subtrees_win_prob_black = [sub.black_win_probability for sub in subtrees]
                    maximum_index = subtrees_win_prob_black.index(
                        self._game_tree.black_win_probability)
                    max_subtree = subtrees[maximum_index]
                    self._game_tree = max_subtree
                    return self._game_tree.move
                else:
                    return self._change_to_explore(game, previous_move)

    def _change_to_explore(self, game: ChessGame, previous_move: Optional[str]) -> str:
        """A helper function for self.make_move, which is called when the player will
        perform the same as ExploringPlayer.

        Note: The depth for ExploringPlayer is the same as self._depth.
        """
        # initialize an exploring player
        explore = ExploringPlayer(self._depth)
        move = explore.make_move(game, previous_move)
        if self._game_tree is None:
            self._game_tree = explore.get_two_depth_tree()
        else:
            self._game_tree.merge_with(explore.get_two_depth_tree())
        return move

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = GameTree()

    def get_tree(self) -> GameTree:
        """Return self._game_tree."""
        return self._game_tree


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

    def __init__(self, xml_file: str, depth: int) -> None:
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
        if self._game_tree is not None:
            self._game_tree = self._game_tree.find_subtree_by_move(previous_move)

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            # there is no existing possible moves in self._game_tree
            # use exploring player
            explorer = ExploringPlayer(self._depth)
            move = explorer.make_move(game, previous_move)
            new_subtree = explorer.get_tree()
            # add the new tree explored two self._current_subtree
            self._current_subtree.add_subtree(new_subtree)
            # update self._current_subtree to trace the previous move
            self._current_subtree = new_subtree.find_subtree_by_move(move)
            return move
        else:  # there is possible moves to choose from self._game_tree
            new_subtree = GameTree(previous_move, False)
            subtrees = self._game_tree.get_subtrees()

            # Obtain subtrees with the lowest point
            min_point = min(s.relative_points for s in subtrees)
            candidate_subtrees = [s for s in subtrees if s.relative_points == min_point]

            # Obtain subtrees with the highest self win probability
            max_probability = max(s.black_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.black_win_probability == max_probability]

            # Obtain subtrees with the lowest opponent win probability
            min_probability = min(s.red_win_probability for s in candidate_subtrees)
            candidate_subtrees = [s for s in candidate_subtrees
                                  if s.red_win_probability == min_probability]

            # If there are still ties, choose one in random
            chosen_subtree = random.choice(candidate_subtrees)
            self._game_tree = chosen_subtree  # We know that this is a subtree of self._game_tree

            # Add the subtree for the previous move to self._current_subtree (denoted scs)
            self._current_subtree.add_subtree(new_subtree)
            # Assign scs to new_subtree, which is a subtree of the original scs
            self._current_subtree = new_subtree
            # Add the subtree for the chosen move to scs
            self._current_subtree.add_subtree(chosen_subtree)
            # Assign scs to chosen_subtree, which is a subtree of the original scs
            self._current_subtree = chosen_subtree
            return self._game_tree.move

    def store_tree(self) -> None:
        """Merge the tree generated with the tree given at the start of the game, then replace the
        file containing the original tree with the new, bigger tree.
        """
        print('Reloading tree...')
        self.reload_tree()
        print('Merging trees...')
        self._game_tree.merge_with(self._current_tree)
        print('Storing tree...')
        tree_to_xml(self._game_tree, self._xml_file)
        print('Success.')

    def reload_tree(self) -> None:
        """Reload the tree from the xml file as self._game_tree."""
        try:
            self._game_tree = xml_to_tree(self._xml_file)
        except FileNotFoundError:
            self._game_tree = None


if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1136', 'E9994', 'E9998', 'R0913', 'R0914'],
    #     'extra-imports': ['chess_game', 'game_tree', 'game_run', 'multiprocessing', 'random', 'os']
    # })
