"""..."""


from __future__ import annotations
from typing import Optional
import csv

GAME_START_MOVE = '*'


class GameTree:
    """A decision tree for chess moves.

    Each node in the tree stores a chess move and a boolean representing whether
    the current player (who will make the next move) is Red or Black.

    Instance Attributes:
      - move: the current chess move (expressed in wxf notation), or '*' if this tree
              represents the start of a game
      - is_red_move: True if Red is to make the next move after this, False otherwise
      - relative_points: the points of Red - the points of Black
      - red_win_probability: the probability that Red will win from the current state
                               of the game

    Representation Invariants:
        - self.move == GAME_START_MOVE or self.move is a valid chess move
        - self.move != GAME_START_MOVE or self.is_red_move == True
        - 0 <= white_red_probability <= 1
    """
    move: str
    is_red_move: bool
    relative_points: int
    red_win_probability: float

    # Private Instance Attributes:
    #  - _subtrees:
    #      the subtrees of this tree, which represent the game trees after a possible
    #      move by the current player
    _subtrees: list[GameTree]

    def __init__(self, move: str = GAME_START_MOVE,
                 is_red_move: bool = True, relative_points: int = 0,
                 red_win_probability: float = 0.0) -> None:
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
        self._update_red_win_probability()

    def __str__(self) -> str:
        """Return a string representation of this tree.
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
        move_desc = f'{self.move} -> {turn_desc}\n'
        s = '  ' * depth + move_desc
        if self._subtrees == []:
            return s
        else:
            for subtree in self._subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def insert_move_sequence(self, moves: list[str],
                             white_win_probability: float = 0.0) -> None:
        """Insert the given sequence of moves into this tree.

        The inserted moves form a chain of descendants, where:
            - moves[0] is a child of this tree's root
            - moves[1] is a child of moves[0]
            - moves[2] is a child of moves[1]
            - etc.

        Do not create duplicate moves that share the same parent; for example, if moves[0] is
        already a child of this tree's root, you should recurse into that existing subtree rather
        than create a new subtree with moves[0].
        But if moves[0] is not a child of this tree's root, create a new subtree for it
        and append it to the existing list of subtrees.

        >>> gt = GameTree()
        >>> gt.insert_move_sequence(['a', 'b', 'c', 'd'])
        >>> print(gt)
        * -> Red's move
          a -> Black's move
            b -> Red's move
              c -> Black's move
                d -> Red's move
        <BLANKLINE>
        >>> gt.insert_move_sequence(['a', 'b', 'x', 'y', 'z'])
        >>> print(gt)
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
        self.insert_move_index(0, moves, white_win_probability)

    def insert_move_index(self, curr_index: int, moves: list[str],
                          red_win_probability: float) -> None:
        """A help method for insert_move_sequence."""
        if curr_index == len(moves):
            return None
        else:
            curr_move = moves[curr_index]
            for subtree in self._subtrees:
                if subtree.move == curr_move:
                    subtree.insert_move_index(curr_index + 1, moves, red_win_probability)
                    self._update_red_win_probability()
                    # an early return
                    return None

            # there is no early return after the for loop,
            # which means we need to create a new subtree
            if self.is_red_move:
                # should be Black
                self.add_subtree(GameTree(move=curr_move,
                                          is_red_move=False,
                                          red_win_probability=red_win_probability))
            else:
                # should be Red
                self.add_subtree(GameTree(move=curr_move,
                                          is_red_move=True,
                                          red_win_probability=red_win_probability))
            # recurse for the next move in moves
            self._subtrees[-1].insert_move_index(curr_index + 1, moves, red_win_probability)

        return None

    def _update_red_win_probability(self) -> None:
        """Recalculate the white win probability of this tree.

        Use the following definition for the white win probability of self:
            - if self is a leaf, don't change the white win probability
              (leave the current value alone)
            - if self is not a leaf and self.is_red_move is True, the red win probability
              is equal to the MAXIMUM of the red win probabilities of its subtrees
            - if self is not a leaf and self.is_red_move is False, the red win probability
              is equal to the AVERAGE of the red win probabilities of its subtrees

        Note: This definition is from the perspective of Red, which should be changed after
        discussion.
        """
        if self._subtrees == []:
            return None
        else:
            subtrees_win_prob = [subtree.red_win_probability for subtree in self._subtrees]
            if self.is_red_move:
                self.red_win_probability = max(subtrees_win_prob)
            else:
                self.red_win_probability = sum(subtrees_win_prob) / len(subtrees_win_prob)
        return None


def load_game_tree(games_file: str) -> GameTree:
    """Create a game tree based on games_file.

    Preconditions:
        - games_file refers to a csv file in the format described on the assignment handout

    Implementation hints:
        - You can review Tutorial 4 for how we read CSV files in Python.

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
    # TODO: to be implemented


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 100,
        'disable': ['E1136'],
    })
