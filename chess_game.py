"""..."""

from __future__ import annotations
from typing import Optional
import copy


_MAX_MOVES = 200
_INITIAL_POINTS = 100
_POINTS = {'r': 1, 'h': 2, 'e': 3, 'a': 4, 'k': 5, 'c': 6, 'p': 7}


class ChessGame:
    """A class representing a state of a game of Chinese Chess.
    """
    # Private Instance Attributes:
    #   - _board: a two-dimensional representation of a Chinese Chess board
    #   - _valid_moves: a list of the valid moves of the current player
    #   - _is_red_active: a boolean representing whether red is the current player
    #   - _move_count: the number of moves that have been made in the current game
    #   - _red_points: the points of Red
    #   - _black_points: the points of Black
    _board: list[list[Optional[_Piece]]]
    _valid_moves: list[str]
    _is_red_active: bool
    _move_count: int
    _red_points: int
    _black_points: int

    def __init__(self, board: list[list[Optional[_Piece]]] = None,
                 red_active: bool = True, move_count: int = 0,
                 red_points: int = _INITIAL_POINTS,
                 black_points: int = _INITIAL_POINTS) -> None:
        """The list representing the board is set up like this
        (where the number represents the index):
        0  |---------------------------------------|
           |    |    |    | \  |  / |    |    |    |
        1  |----+----+----+----+----+----+----+----|
           |    |    |    | /  |  \ |    |    |    |
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
           |    |    |    | \  |  / |    |    |    |
        8  |----+----+----+----+----+----+----+----
           |    |    |    | /  |  \ |    |    |    |
        9  |---------------------------------------|
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
            self._red_points = red_points
            self._black_points = black_points

            # self._recalculate_valid_moves  # TODO: to be implemented

    def get_valid_moves(self) -> list[str]:
        """Return a list of the valid moves for the active player."""
        return self._valid_moves

    def make_move(self, move: str) -> None:
        """Make the given chess move. The instance of ChessGame will be mutated, and will
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
            ...  # TODO: implement later

    def _calculate_moves_for_board(self, board: list[list[Optional[_Piece]]],
                                   is_red_active: bool) -> list[str]:
        """Return all possible moves on a given board with a given active player."""
        moves = []

        for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:
            piece = board[pos[0]][pos[1]]
            if piece is None or piece.is_red != is_red_active:
                continue

            kind, is_red = piece.kind, piece.is_red

            if kind == 'r':
                moves += ...

    def _find_moves_in_direction(self, board: list[list[Optional[_Piece]]],
                                 pos: tuple[int, int], is_red: bool, direction: tuple[int, int],
                                 limit: int = None, capture: bool = None):
        """Find valid moves moving in a given direction from a certain position.

        capture: True if must capture, False if must not capture, None otherwise.

        >>> g = ChessGame()
        >>> g._find_moves_in_direction(g._board, (7, 1), True, (-1, 0), capture=False)
        ['c8+1', 'c8+2', 'c8+3', 'c8+4', 'c8+7']
        >>> g._find_moves_in_direction(g._board, (7, 1), True, (0, 1), capture=False)
        ['c8.7', 'c8.6', 'c8.5', 'c8.4', 'c8.3']
        >>> g._find_moves_in_direction(g._board, (0, 0), False, (1, 0), capture=True)
        ['r1+1', 'r1+2']
        >>> g._find_moves_in_direction(g._board, (6, 2), True, (-1, 0), capture=True, limit=1)
        ['p7+1']
        """
        moves = []

        kind = board[pos[0]][pos[1]].kind
        stop = False
        i = 1
        while not stop:
            y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i

            if x < 0 or y < 0 or x > 8 or y > 9:
                break  # Out of bounds

            contents = board[y][x]
            move = _get_wxf_movement(board, pos, (y, x), is_red)

            if contents is not None:
                # point contains piece
                stop = True
                if kind == 'c':
                    i += 1
                    y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i
                    while 0 <= x <= 8 and 0 <= y <= 9:
                        if board[y][x] is not None and board[y][x].is_red != is_red:
                            # Can fire cannon
                            moves.append(_get_wxf_movement(board, pos, (y, x), is_red))
                            break
                        i += 1
                        y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i

                if contents.is_red != is_red and capture is not False:
                    moves.append(move)
            else:
                # Empty square
                moves.append(move)

            i += 1

            if limit is not None and i > limit:
                stop = True

        return moves

    def get_board(self) -> list[list[Optional[_Piece]]]:
        """Return the board representation."""
        return self._board


def _get_wxf_movement(board: list[list[Optional[_Piece]]],
                      start: tuple[int, int], end: tuple[int, int], is_red: bool) -> str:
    """Return the move in wxf notation given the colour, start coordinates, and end coordinates.

    Preconditions:
        - start represents a piece whose colour is consistent with is_red
        - the move from start to end is legal

    >>> g = ChessGame()
    >>> board = g.get_board()
    >>> _get_wxf_movement(board, (7, 7), (7, 4), True)
    'c2.5'
    >>> _get_wxf_movement(board, (2, 7), (2, 5), False)
    'c8.6'
    >>> _get_wxf_movement(board, (0, 1), (2, 2), False)
    'h2+3'
    >>> _get_wxf_movement(board, (9, 6), (7, 4), True)
    'e3+5'
    >>> _get_wxf_movement(board, (9, 0), (7, 0), True)
    'r9+2'
    >>> _get_wxf_movement(board, (2, 7), (1, 7), False)
    'c8-1'
    """
    move_start = _index_to_wxf(board, start, is_red)
    kind = board[start[0]][start[1]].kind

    if start[0] == end[0]:  # Horizontal movement
        if is_red:
            return move_start + '.' + str(9 - end[1])
        else:  # not is_red
            return move_start + '.' + str(end[1] + 1)
    elif start[1] == end[1]:  # Vertical movement
        if (is_red and end[0] < start[0]) or (not is_red and end[0] > start[0]):
            return move_start + '+' + str(abs(end[0] - start[0]))
        else:  # (is_red and end[0] > start[0]) or (not is_red and end[0] < start[0])
            return move_start + '-' + str(abs(end[0] - start[0]))
    else:  # Movement that changes both x and y coordinates
        if is_red:
            move_end = str(9 - end[1])
        else:  # not is_red
            move_end = str(end[1] + 1)

        if (is_red and end[0] < start[0]) or (not is_red and end[0] > start[0]):
            return move_start + '+' + move_end
        else:  # (is_red and end[0] > start[0]) or (not is_red and end[0] < start[0])
            return move_start + '-' + move_end


def _wxf_to_index(board: list[list[Optional[_Piece]]], piece: str, is_red: bool) -> tuple[int, int]:
    """Return the coordinate of a piece (y, x) given the wxf notation for a piece (e.g. 'c6').

    Raise ValueError if not found.

    >>> g = ChessGame()
    >>> board = g.get_board()
    >>> _wxf_to_index(board, 'c2', True)
    (7, 7)
    >>> _wxf_to_index(board, 'a4', False)
    (0, 3)
    """
    piece_lower = piece.lower()
    type = piece_lower[0]
    location = piece_lower[1]
    if location in {'+', '-'}:
        y, x = 0, 0

        # Find the first piece
        while y <= 9 and board[y][x] != _Piece(type, is_red):
            x += 1
            if x >= 9:
                y += 1
                x = 0

        if y > 9:
            raise ValueError

        coord1 = (y, x)
        y += 1

        # Find the second piece (they are in the same column)
        while y <= 9 and board[y][x] != _Piece(type, is_red):
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
        while y <= 9 and board[y][x] != _Piece(type, is_red):
            y += 1

        if y > 9:
            raise ValueError
        else:
            return (y, x)


def _index_to_wxf(board: list[list[Optional[_Piece]]], pos: tuple[int, int], is_red: bool) -> str:
    """Return the wxf notation of a piece (e.g. 'c6') given its coordinate (y, x).

    Raise ValueError is there is no piece at the position or the piece has the opposite colour.

    >>> g = ChessGame()
    >>> board = g.get_board()
    >>> _index_to_wxf(board, (9, 6), True)
    'e3'
    >>> _index_to_wxf(board, (0, 0), False)
    'r1'
    """
    piece = board[pos[0]][pos[1]]
    if piece is None or piece.is_red != is_red:
        raise ValueError

    type = piece.kind
    x = pos[1]

    # Search if another piece is present in the column
    y = 0
    while y <= 9 and (board[y][x] != _Piece(type, is_red) or y == pos[0]):
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




if __name__ == '__main__':
    import doctest
    doctest.testmod()
