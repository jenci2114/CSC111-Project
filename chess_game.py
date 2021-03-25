"""..."""

from __future__ import annotations
from typing import Optional


class ChessGame:
    """A class representing a state of a game of Chinese Chess.
    """
    # Private Instance Attributes:
    #   - _board: a two-dimensional representation of a Chinese Chess board
    #   - _valid_moves: a list of the valid moves of the current player
    #   - _is_red_active: a boolean representing whether red is the current player
    #   - _move_count: the number of moves that have been made in the current game
    _board: list[list[Optional[_Piece]]]
    _valid_moves: list[str]
    _is_red_active: bool
    _move_count: int

    def __init__(self, board: list[list[Optional[_Piece]]] = None,
                 red_active: bool = True, move_count: int = 0) -> None:
        """The list representing the board is set up like this
        (where the number represents the index):
        0  |----|----|----|----|----|----|----|----|
           |    |    |    | \  | /  |    |    |    |
        1  |----+----+----+----+----+----+----+----|
           |    |    |    | /  | \  |    |    |    |
        2  |----+----+----+----+----+----+----+----|
           |    |    |    |    |    |    |    |    |
        3  |----+----+----+----+----+----+----+----|
           |    |    |    |    |    |    |    |    |
        4  |----+----+----+----+----+----+----+----|  Black
           |         楚   河         汉   界         |
        5  |----+----+----+----+----+----+----+----|  Red
           |    |    |    |    |    |    |    |    |
        6  |----+----+----+----+----+----+----+----|
           |    |    |    |    |    |    |    |    |
        7  |----+----+----+----+----+----+----+----|
           |    |    |    | \  | /  |    |    |    |
        8  |----+----+----+----+----+----+----+----|
           |    |    |    | /  | \  |    |    |    |
        9  |----|----|----|----|----|----|----|----|
           0    1    2    3    4    5    6    7    8

        Note: the index numbering above is VERY different from what is used for the WXF notation.
        """
        if board is not None:
            self._board = board
        else:
            self._board = [
                # index 0:
                [_Piece('r', False), _Piece('h', False), _Piece('e', False), _Piece('a', False),
                 _Piece('k', False), _Piece('a', False), _Piece('e', False), _Piece('h', False),
                 _Piece('r', False)],
                # index 1:
                [None for _ in range(0, 9)],
                # index 2:
                [None, _Piece('c', False), None, None, None, None, None, _Piece('c', False), None],
                # index 3:
                [_Piece('p', False), None, _Piece('p', False), None, _Piece('p', False), None,
                 _Piece('p', False), None, _Piece('p', False)],
                # index 4:
                [None for _ in range(0, 9)],
                # index 5:
                [None for _ in range(0, 9)],
                # index 6:
                [_Piece('p', True), None, _Piece('p', True), None, _Piece('p', True), None,
                 _Piece('p', True), None, _Piece('p', True)],
                # index 7:
                [None, _Piece('c', True), None, None, None, None, None, _Piece('c', True), None],
                # index 8:
                [None for _ in range(0, 9)],
                # index 9:
                [_Piece('r', True), _Piece('h', True), _Piece('e', True), _Piece('a', True),
                 _Piece('k', True), _Piece('a', True), _Piece('e', True), _Piece('h', True),
                 _Piece('r', True)],
            ]
            self._is_red_active = red_active
            self._move_count = move_count
            self._valid_moves = []

            self._recalculate_valid_moves  # to be implemented


class _Piece:
    """Represents a single piece in Chinese Chess.

    Instance Attributes:
        - kind: the type of piece, where
            r = rook/chariot 车
            h = horse 马
            e = elephant 象
            a = assistant 士
            k = king 将/帅
            c = cannon 炮
            p = pawn 卒/兵
        - is_red: whether the piece belongs to the red player

    Representation Invariants:
        - kind in {'r', 'h', 'e', 'a', 'k', 'c', 'p'}
    """
    kind: str
    is_red: bool

    def __init__(self, kind: str, is_red: bool) -> None:
        """Initialize a new piece."""
        self.kind = kind
        self.is_red = is_red
