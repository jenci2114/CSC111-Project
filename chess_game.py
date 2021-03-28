"""..."""

from __future__ import annotations
from typing import Optional


_MAX_MOVES = 200


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

            # self._recalculate_valid_moves  # to be implemented

    def get_valid_moves(self) -> list[str]:
        """Return a list of the valid moves for the active player."""
        return self._valid_moves

    def make_move(self, move: str) -> None:
        """Make the given chess move. This instance of ChessGame will be mutated, and will
        afterwards represent the game state after move is made.

        If move is not a currently valid move, raise a ValueError.
        """
        if move not in self._valid_moves:
            raise ValueError(f'Move "{move}" is not valid')

        self._board = self._board_after_move(move)

        self._is_red_active = not self._is_red_active
        self._move_count += 1

        self._recalculate_valid_moves()

    def copy_and_make_move(self, move: str) -> ChessGame:
        """Make the given chess move in a copy of this ChessGame, and return that copy.

        If move is not a currently valid move, raise a ValueError.
        """
        return ChessGame(board=self._board_after_move(move),
                         red_active=not self._is_red_active,
                         move_count=self._move_count + 1)

    def is_red_move(self) -> bool:
        """Return whether the red player is to move next."""
        return self.is_red_move()

    def get_winner(self) -> Optional[str]:
        """Return the winner of the game (red or black) or 'draw' if the game ended in a draw.

        Return None if the game is not over.
        """
        if self._move_count >= _MAX_MOVES:
            return 'Draw'
        elif ...:
            ...  # Implement later

    def _calculate_moves_for_board(self, board: list[list[Optional[_Piece]]],
                                   is_red_active: bool) -> tuple:
        """Return all posible moves on a given board with a given active player."""
        moves = []
        # Used to calculate whether the other players' king is in check
        # (i.e. the black king if is_red_active, otherwise the red king)
        check = []

        for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:
            piece = board[pos[0]][pos[1]]
            if piece is None or piece.is_red != is_red_active:
                continue

            kind, is_red = piece.kind, piece.is_red

            if kind == 'r':
                ...  # implement later

    def _find_moves_in_direction(self, board, moves, pos, is_red, direction, limit=None,
                                 capture=None):
        """Find valid moves moving in a given direction from a certain position.

        capture: True if must capture, False if must not capture, None otherwise.
        """
        move_start = ...  # implement later

    def _wxf_to_index(self, piece: str, is_red: bool) -> tuple[int, int]:
        """Return the coordinate of a piece (y, x) given the wxf notation for a piece (e.g. 'c6').

        Raise ValueError if not found.
        """
        piece_lower = piece.lower()
        type = piece_lower[0]
        location = piece_lower[1]
        if location in {'+', '-'}:
            y, x = 0, 0

            # Find the first piece
            while y <= 9 and self._board[y][x] != _Piece(type, is_red):
                x += 1
                if x >= 9:
                    y += 1
                    x = 0

            if y > 9:
                raise ValueError

            coord1 = (y, x)
            y += 1

            # Find the second piece (they are in the same column)
            while y <= 9 and self._board[y][x] != _Piece(type, is_red):
                y += 1

            if y > 9:
                raise ValueError

            coord2 = (y, x)  # y is greater than coord1

            if (is_red and location == '+') or (not is_red and location == '-'):
                return coord1
            else:
                return coord2
        else:  # location is a number
            if is_red:
                x = 9 - int(location)
            else:  # not is_red
                x = int(location) - 1

            y = 0
            # Find the piece in the given column
            while y <= 9 and self._board[y][x] != _Piece(type, is_red):
                y += 1

            if y > 9:
                raise ValueError
            else:
                return (y, x)

    def _index_to_wxf(self, pos: tuple[int, int], is_red: bool) -> str:
        """Return the wxf notation of a piece (e.g. 'c6') given its coordinate (y, x).

        Raise ValueError is there is no piece at the position or the piece has the opposite colour.
        """
        piece = self._board[pos[0]][pos[1]]
        if piece is None or piece.is_red != is_red:
            raise ValueError

        type = piece.kind
        x = pos[1]

        # Search if another piece is present in the column
        y = 0
        while y <= 9 and (self._board[y][x] != _Piece(type, is_red) or y == pos[0]):
            y += 1

        if y > 9:
            if is_red:
                return type + str(9 - x)
            else:  # not is_red
                return type + str(x + 1)
        else:
            if (is_red and pos[0] > y) or (not is_red and pos[0] < y):
                return type + '-'
            else:
                return type + '+'


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

    def __eq__(self, other: Optional[_Piece]) -> bool:
        if other is None:
            return False
        return self.kind == other.kind and self.is_red == other.is_red
