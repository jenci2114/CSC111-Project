"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This Python module contains the GameTree class, which stores
various attributes for Chinese Chess moves. Also, this module
contains functions that convert between the aforementioned
GameTree class and xml files, where xml files are used to store
preexisting GameTrees.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei
"""


from __future__ import annotations
from typing import Optional
import csv
import xml.etree.cElementTree as ET
import math

import chess_game
from chess_game import ChessGame

GAME_START_MOVE = '*'
ESTIMATION = 0.8


class GameTree:
    """A decision tree for chess moves.

    Each node in the tree stores a chess move and a boolean representing whether
    the current player (who will make the next move) is Red or Black.

    Instance Attributes:
        - move: the current chess move (expressed in wxf notation), or '*' if this tree
                represents the start of a game
        - is_red_move: True if Red is to make the next move after this, False otherwise
        - relative_points: related to absolute points as defined in calculate_absolute_points in
                           chess_game.py. For more information, see GameTree.reevaluate.
        - red_win_probability: the probability that Red will win from the current state
                               of the game. For more information, see
                               GameTree._update_win_probabilities
        - black_win_probability: the probability that Black will win from the current state
                                 of the game. For more information, see
                                 GameTree._update_win_probabilities

    Note: red_win_probability is calculated from Red's view and black_win_probability
    is calculated from Black's view. 1.0 means red/black can win for sure and 0.0
    means inconclusive.

    Representation Invariants:
        - self.move == GAME_START_MOVE or self.move is a valid chess move
        - self.move != GAME_START_MOVE or self.is_red_move == True
        - 0 <= red_win_probability <= 1
        - 0 <= black_win_probability <= 1
    """
    move: str
    is_red_move: bool
    relative_points: int
    red_win_probability: float
    black_win_probability: float

    # Private Instance Attributes:
    #  - _subtrees:
    #      the subtrees of this tree, which represent the game trees after a possible
    #      move by the current player
    _subtrees: list[GameTree]

    def __init__(self, move: str = GAME_START_MOVE,
                 is_red_move: bool = True, relative_points: int = 0,
                 red_win_probability: float = 0.0, black_win_probability: float = 0.0) -> None:
        """Initialize a new game tree.

        >>> game = GameTree()
        >>> game.move == GAME_START_MOVE
        True
        >>> game.is_red_move
        True
        """
        self.move = move
        self.is_red_move = is_red_move
        self.red_win_probability = red_win_probability
        self.black_win_probability = black_win_probability
        self.relative_points = relative_points
        self._subtrees = []

    def get_subtrees(self) -> list[GameTree]:
        """Return the subtrees of this game tree."""
        return self._subtrees

    def find_subtree_by_move(self, move: str) -> Optional[GameTree]:
        """Return the subtree corresponding to the given move.

        Return None if no subtree corresponds to that move.
        """
        for subtree in self._subtrees:
            if subtree.move == move:
                return subtree

        return None

    def add_subtree(self, subtree: GameTree) -> None:
        """Add a subtree to this game tree."""
        self._subtrees.append(subtree)
        self._update_win_probabilities()

    def clean_subtrees(self) -> None:
        """Remove all the subtrees of self.

        >>> tree = GameTree()
        >>> tree.insert_move_sequence(['a', 'b', 'c', 'd'], [1, 2, 3, 4])
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        >>> tree.clean_subtrees()
        >>> print(tree)
        * -> Red's move
        <BLANKLINE>
        """
        self._subtrees = []

    def clean_depth_subtrees(self, depth: int) -> None:
        """Remove all the subtrees after depth of <depth>.

        Precondition:
            - depth >= 1

        >>> tree = GameTree()
        >>> tree.insert_move_sequence(['a', 'b', 'c', 'd'], [1, 2, 3, 4])
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        >>> tree.clean_depth_subtrees(3)
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
        <BLANKLINE>
        """
        if depth == 1:  # Depth reached remove all subtrees
            self.clean_subtrees()
        else:  # Depth not reached. Recurse downwards.
            for subtree in self._subtrees:
                subtree.clean_depth_subtrees(depth - 1)

    def get_height(self, curr_depth: int = 1) -> int:
        """Return the height of this tree.

        Preconditions:
            - Must be a tree of depth at least 1
        """
        if self._subtrees == []:  # Base case: we have a leaf. Return the current depth.
            return curr_depth
        else:  # Recursive step: return the greatest depth among the subtrees
            return max(sub.get_height(curr_depth + 1) for sub in self._subtrees)

    def __str__(self) -> str:
        """Return a string representation of this tree.
        >>> tree = GameTree()
        >>> tree.insert_move_sequence(['a', 'b', 'c', 'd'], [1, 2, 3, 4])
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        """
        return self._str_indented(0)

    def _str_indented(self, depth: int) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_red_move:
            turn_desc = "Red's move"
        else:
            turn_desc = "Black's move"

        # Indicate the current move -> who's turn is it next
        move_desc = f'{self.move} -> {turn_desc}\n'
        s = '  ' * depth + move_desc  # Indentation for depth
        if self._subtrees == []:  # Base case: print the string representation
            return s
        else:  # Recursive step: also print the string representations of the subtrees
            for subtree in self._subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def insert_move_sequence(self, moves: list[str], points: list[int],
                             red_win_probability: float = 0.0,
                             black_win_probability: float = 0.0) -> None:
        """Insert the given sequence of moves into this tree.

        Parameters:
            - moves: a list of moves in a game, with several red-black turns
            - points: a lisyt of the relative points of the game, corresponding to the games
                      after each move in moves

        The inserted moves form a chain of descendants, where:
            - moves[0] is a child of this tree's root
            - moves[1] is a child of moves[0]
            - moves[2] is a child of moves[1]
            - etc.

        Precondictions:
            - len(moves) == len(points)
            - moves represents a all moves in a complete game

        >>> tree = GameTree()
        >>> tree.insert_move_sequence(['a', 'b', 'c', 'd'], [1, 2, 3, 4])
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        >>> tree.insert_move_sequence(['a', 'b', 'x', 'y', 'z'], [1, 2, 3, 4, 5])
        >>> print(tree)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
              x -> Black's move
                y -> Red's move
                  z -> Black's move
        <BLANKLINE>
        """
        self.insert_move_index(0, moves, points, red_win_probability, black_win_probability)

    def insert_move_index(self, curr_index: int, moves: list[str], points: list[int],
                          red_win_probability: float, black_win_probability: float,) -> None:
        """A help method for insert_move_sequence.

        Preconditions:
            - curr_index <= len(moves)
        """
        if curr_index == len(moves):  # base case
            return
        else:
            curr_move = moves[curr_index]
            relative_point = points[curr_index]
            for subtree in self._subtrees:
                if subtree.move == curr_move:
                    # curr_move exists in subtrees, check the next move in moves
                    subtree.insert_move_index(curr_index + 1, moves, points,
                                              red_win_probability, black_win_probability)
                    # trees may be updated after we call insert_move_index method
                    # so we need to update win probability
                    self._update_win_probabilities()
                    # an early return
                    return

            # there is no early return after the for loop and we need to create a new subtree
            if self.is_red_move:
                # should be Black next
                self.add_subtree(GameTree(move=curr_move,
                                          is_red_move=False,
                                          relative_points=relative_point,
                                          red_win_probability=red_win_probability,
                                          black_win_probability=black_win_probability))
            else:
                # should be Red next
                self.add_subtree(GameTree(move=curr_move,
                                          is_red_move=True,
                                          relative_points=relative_point,
                                          red_win_probability=red_win_probability,
                                          black_win_probability=black_win_probability))
            # recurse on the next move in moves
            self._subtrees[-1].insert_move_index(curr_index + 1, moves, points,
                                                 red_win_probability, black_win_probability)
            # trees may be updated after we call insert_move_index method
            self._update_win_probabilities()

    def _update_win_probabilities(self) -> None:
        """Update the red and black win probabilities of this tree.

        self.red_win_probability is calculated from Red's view, which is defined as:
            - if self is a leaf, don't change the red win probability
              (leave the current value alone)
            - if self is not a leaf and self.is_red_move is True, the red win probability
              is equal to the MAXIMUM of the red win probabilities of its subtrees
            - if self is not a leaf and self.is_red_move is False, the red win probability
              is equal to the AVERAGE of the top ESTIMATION red win probabilities of its subtrees

        self.black_win_probability is calculated from Black's view, which is defined as:
            - if self is a leaf, don't change the red win probability
              (leave the current value alone)
            - if self is not a leaf and self.is_red_move is False, the black win probability
              is equal to the MAXIMUM of the black win probabilities of its subtrees
            - if self is not a leaf and self.is_red_move is Ture, the black win probability
              is equal to the AVERAGE of the top ESTIMATION black win probabilities of its subtrees

        Note: ESTIMATION is a parameter representing how the player thinks of the opponent.
              For example, ESTIMATION of 0.5 means the player thinks the opponent will choose
              moves with top 50% win probability. The smaller ESTIMATION is, the stronger the
              player considers the opponent as.

        """
        if self._subtrees == []:  # this is a leaf
            return
        else:
            # lists of win probabilities corresponding to subtrees
            subtrees_win_prob_red = [subtree.red_win_probability for subtree in self._subtrees]
            subtrees_win_prob_black = [subtree.black_win_probability for subtree in self._subtrees]
            if self.is_red_move:
                self.red_win_probability = max(subtrees_win_prob_red)
                # Averages the top ESTIMATION of the opponent's moves
                half_len = math.ceil(len(subtrees_win_prob_black) * ESTIMATION)
                top_chances = sorted(subtrees_win_prob_black, reverse=True)[:half_len]
                self.black_win_probability = sum(top_chances) / half_len
            else:
                self.black_win_probability = max(subtrees_win_prob_black)
                # Averages the top ESTIMATION of the opponent's moves
                half_len = math.ceil(len(subtrees_win_prob_red) * ESTIMATION)
                top_chances = sorted(subtrees_win_prob_red, reverse=True)[:half_len]
                self.red_win_probability = sum(top_chances) / half_len
        return

    def purge(self) -> None:
        """Remove duplicate subtrees (if there is any)."""
        moves_so_far = []  # accumulator
        for subtree in self._subtrees:
            if subtree.move in moves_so_far:  # this is a duplicate, so:
                self._subtrees.remove(subtree)  # remove the subtree
                # and merge with the subtree with the same move
                self.find_subtree_by_move(subtree.move).merge_with(subtree)
            else:  # No duplicates yet, store the move in the accumulator
                moves_so_far.append(subtree.move)

    def reevaluate(self) -> None:
        """Re-evaluate the relative points and win-probabilities of this tree.

        For the function that calculates the absolute points for one board, see chess_game.py.

        The relative points of a certain GameTree is defined by:
            - The absolute points of the board after the move, if the subtree is a leaf
            - The highest relative points among its subtrees, if red (the maximizer) is to move next
            - The least relative points among its subtrees, if black (the minimizer) is to move next

        This method will recurse all the way to the leaves to obtain the points and the
        probabilities, then pass it back to each of the parents, going over the entire tree.
        """
        self.purge()  # First purge any duplicates
        if self._subtrees == []:  # Base case, self is a leaf
            return  # we already have the points and win possibilities
        else:  # Recursive step
            for subtree in self._subtrees:
                subtree.reevaluate()  # Recurse and re-evaluate the subtrees

                # At this point, all subtrees of the loop variable subtree is reevaluated.
                if subtree._subtrees != []:  # not a leaf, then we calculate based on its subtrees
                    subtree._update_win_probabilities()
                    if subtree.is_red_move:
                        subtree.relative_points = max(s.relative_points for s in subtree._subtrees)
                    else:
                        subtree.relative_points = min(s.relative_points for s in subtree._subtrees)

    def merge_with(self, other_tree: GameTree) -> None:
        """Recursively merge the current tree with other_tree. Note that this is a
        *mutating* method and that the original tree will be replaced by the merged tree.

        Preconditions:
            - other_tree stores valid Chinese chess moves.
            - other_tree has the same parents and root with self

        >>> tree1 = GameTree()
        >>> tree1.insert_move_sequence(['a', 'b', 'c', 'd'], [1, 2, 3, 4])
        >>> print(tree1)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        >>> tree2 = GameTree()
        >>> tree2.insert_move_sequence(['a', 'x', 'y', 'z'], [1, 5, 6, 7])
        >>> print(tree2)
        * -> Red's move
          a -> Black's move
            x -> Red's move
              y -> Black's move
                z -> Red's move
        <BLANKLINE>
        >>> tree1.merge_with(tree2)
        >>> print(tree1)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
            x -> Red's move
              y -> Black's move
                z -> Red's move
        <BLANKLINE>
        """
        assert self.move == other_tree.move  # They must have the same root moves
        subtrees_moves = [sub.move for sub in self._subtrees]
        for subtree in other_tree.get_subtrees():
            if subtree.move in subtrees_moves:  # we already have the move, so
                # recurse down into their subtrees
                index = subtrees_moves.index(subtree.move)
                self._subtrees[index].merge_with(subtree)
            else:  # we don't have the move yet, so add it
                self.add_subtree(subtree)

        # Now the two trees are merged. Re-evaluate the large tree so that its
        # attributes are consistent (with all the leaf values)
        self.reevaluate()


def load_game_tree(games_file: str) -> GameTree:
    """Create a game tree based on games_file.

    A small smaple of games_file:
    gameID,turn,side,move
    57380690,1,red,C2.5
    57380690,2,red,H2+3
    57380690,3,red,R1.2
    57380690,1,black,h2+3
    57380690,2,black,c8.6
    57380690,3,black,h8+7

    Assume there is no draw and the last person to make a move in moves is the winner.

    Preconditions:
        - games_file refers to a csv file in the same format as the small sample.

    >>> tree = load_game_tree('data/small_sample.csv')
    >>> print(tree)
    * -> Red's move
      C2.5 -> Black's move
        h2+3 -> Red's move
          H2+3 -> Black's move
            c8.6 -> Red's move
              R1.2 -> Black's move
                h8+7 -> Red's move
              A6+5 -> Black's move
                p7+1 -> Red's move
    <BLANKLINE>
    """
    tree = GameTree()
    games = {}  # the key is gameID and the value is a list

    with open(games_file) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header row
        for row in reader:
            # row[0] is gameID, which is unique
            if row[0] not in games:  # create a new list
                # row[2] is side and row[3] is move
                # games[row[0]] is a list and its i-th element is the i-th turn of the game,
                # which is a list with the first element being red's move, and possibly
                # the second element being black's move
                games[row[0]] = [[row[3]]]
            else:  # row[0] is in games
                turn = int(row[1])
                if turn > len(games[row[0]]):  # Need to add a new turn in the list
                    games[row[0]].append([row[3]])
                else:  # Need to add black's move to the existing list
                    games[row[0]][turn - 1].append(row[3])

    for game_id in games:
        # game is a list consisting of many lists, with each list representing a turn
        game = games[game_id]
        new_game = ChessGame()  # simulate a new game to calculate relative points
        sequence_so_far = []  # collect the red-black turn of game
        points_so_far = []  # the relative point corresponding to sequence_so_far

        for turn in game:  # turn is a list of two moves (red-black) or one move (red)
            sequence_so_far += turn
        for move in sequence_so_far:
            # simulate a move in game to get the point after this move
            new_game.make_move(move)
            board = new_game.get_board()
            points_so_far.append(chess_game.calculate_absolute_points(board))

        if len(sequence_so_far) % 2 == 1:
            # Red is the winner since Black did not move after Red made a move
            tree.insert_move_sequence(sequence_so_far, points_so_far, red_win_probability=1)
        else:  # Black is the winner
            tree.insert_move_sequence(sequence_so_far, points_so_far, black_win_probability=1)

    return tree


def tree_to_xml(tree: GameTree, filename: str) -> None:
    """Store the given GameTree as an xml file with the given filename.

    Note on naming of attributes (for shortening xml file size thus reducing running time):
        - m: move
        - i: is_red_move
        - p: relative_points
        - r: red_win_probability
        - b: black_win_probability
        - t: True
        - f: False

    Precondition:
        - filename has suffix .xml
    """
    bool_dict = {True: 't', False: 'f'}  # For shortening the xml file
    root = ET.Element('GameTree')
    root_move = ET.SubElement(root, 'm', m=str(tree.move), i=bool_dict[tree.is_red_move],
                              p=str(tree.relative_points),
                              r=str(tree.red_win_probability), b=str(tree.black_win_probability))
    _build_e_tree(root_move, tree)

    xml_tree = ET.ElementTree(root)  # Make <root> the root of an ElementTree
    xml_tree.write(filename)  # Store the ElementTree as file


def _build_e_tree(root_move: ET.Element, tree: GameTree) -> None:
    """Helper function that recursively builds up an ElementTree from a GameTree.

    This function mutates its input Element.
    """
    bool_dict = {True: 't', False: 'f'}  # For shortening the xml file
    for subtree in tree.get_subtrees():  # Build the ElementTree for each subtree and recurse down
        move = ET.SubElement(root_move, 'm', m=str(subtree.move),
                             i=bool_dict[subtree.is_red_move],
                             p=str(subtree.relative_points),
                             r=str(subtree.red_win_probability),
                             b=str(subtree.black_win_probability))
        _build_e_tree(move, subtree)


def xml_to_tree(filename: str) -> GameTree:
    """Return a game tree which is stored in the specified xml file.

    Precondition:
        - filename must be a file generated by the tree_to_xml function
    """
    tree = GameTree()
    with open(filename) as file:
        e_tree = ET.parse(file)  # Convert the xml file into an ElementTree
        root_move = e_tree.getroot()[0]  # There is only 1 root move (*), which is in index 0
        _build_game_tree(root_move, tree)

    return tree


def _build_game_tree(move: ET.Element, tree: GameTree) -> None:
    """Helper function that recursively builds up a GameTree from an ElementTree.

    This function mutates its input tree.
    """
    tree.move = move.attrib['m']  # Extract GameTree.move attribute
    tree.is_red_move = move.attrib['i'] == 't'  # Extract GameTree.is_red_move attribute
    tree.relative_points = int(move.attrib['p'])  # Extract GameTree.relative_points attribute

    # Extract GameTree.red_win_probability and GameTree.black_win_probability attribute
    tree.red_win_probability = float(move.attrib['r'])
    tree.black_win_probability = float(move.attrib['b'])

    for child_move in move:
        subtree = GameTree()
        _build_game_tree(child_move, subtree)  # Recurse into subtrees
        tree.add_subtree(subtree)


if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1136', 'E9998', 'R0913', 'R1702'],
    #     'extra-imports': ['csv', 'xml.etree.cElementTree', 'math', 'chess_game']
    # })
