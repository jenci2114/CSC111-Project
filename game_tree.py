"""Game Tree"""


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
                             red_win_probability: float = 0.0) -> None:
        """Insert the given sequence of moves into this tree.

        The inserted moves form a chain of descendants, where:
            - moves[0] is a child of this tree's root
            - moves[1] is a child of moves[0]
            - moves[2] is a child of moves[1]
            - etc.

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
        self.insert_move_index(0, moves, red_win_probability)

    def insert_move_index(self, curr_index: int, moves: list[str],
                          red_win_probability: float) -> None:
        """A help method for insert_move_sequence."""
        if curr_index == len(moves):
            return
        else:
            curr_move = moves[curr_index]
            for subtree in self._subtrees:
                if subtree.move == curr_move:
                    subtree.insert_move_index(curr_index + 1, moves, red_win_probability)
                    self._update_red_win_probability()
                    # an early return
                    return

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

        return

    def _update_red_win_probability(self) -> None:
        """Recalculate the red win probability of this tree.

        Note: This definition is from the perspective of Red, which should be changed after
        discussion.
        """
        # TODO: Change the algorithm so that it is fair for both sides
        if self._subtrees == []:
            return None
        else:
            subtrees_win_prob = [subtree.red_win_probability for subtree in self._subtrees]
            if self.is_red_move:
                self.red_win_probability = max(subtrees_win_prob)
            else:
                self.red_win_probability = sum(subtrees_win_prob) / len(subtrees_win_prob)
        return None

    def _calculate_relative_points(self) -> None:
        """Calculate the relative points.

        We need to go back to all the ancestors to see the change of pieces.
        """
        # TODO: implement this method


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
        sequence_so_far = []  # collect the red-black turn of game

        for turn in game:
            sequence_so_far += turn

        tree.insert_move_sequence(sequence_so_far)

    return tree


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
