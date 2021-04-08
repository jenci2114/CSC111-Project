"""..."""

from __future__ import annotations
from typing import Optional
import copy


_MAX_MOVES = 200

# For printing colours
RED = '\033[91m'
BLACK = '\33[0m'

PIECES = {('r', True): RED + '车' + BLACK, ('r', False): '车',
          ('h', True): RED + '马' + BLACK, ('h', False): '马',
          ('e', True): RED + '相' + BLACK, ('e', False): '象',
          ('a', True): RED + '仕' + BLACK, ('a', False): '士',
          ('k', True): RED + '帅' + BLACK, ('k', False): '将',
          ('c', True): RED + '炮' + BLACK, ('c', False): '炮',
          ('p', True): RED + '兵' + BLACK, ('p', False): '卒'}


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
        0  丨----一----一----一----一----一----一----一----丨
           丨    丨    丨    丨 \  丨  / 丨    丨    丨    丨
        1  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨 /  丨  \ 丨    丨    丨    丨
        2  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨    丨    丨    丨    丨    丨
        3  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨    丨    丨    丨    丨    丨
        4  丨----十----十----十----十----十----十----十----丨 Black
           丨    一    楚    河    一    汉    界    一    丨
        5  丨----十----十----十----十----十----十----十----丨  Red
           丨    丨    丨    丨    丨    丨    丨    丨    丨
        6  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨    丨    丨    丨    丨    丨
        7  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨 \  丨  / 丨    丨    丨    丨
        8  丨----十----十----十----十----十----十----十----丨
           丨    丨    丨    丨 /  丨  \ 丨    丨    丨    丨
        9  丨----一----一----一----一----一----一----一----丨
           〇    一    二    三    四    五    六    七    八

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

            self._recalculate_valid_moves()

    def __str__(self) -> str:
        """Return the string representation of the board, who is active, and valid moves.

        If the game is finished, return the string representation of the board and who wins.
        """
        print_board(self._board)
        winner = self.get_winner()

        if winner is None:
            turn_message = ''
            if self._is_red_active:
                turn_message += "Red's turn.\n"
            else:
                turn_message += "Black's turn.\n"
            return turn_message + f'Valid moves: {self._valid_moves}'
        elif winner == 'Draw':
            return 'Draw!'
        else:  # Red wins or black wins
            return f'{winner} wins!'

    def get_valid_moves(self) -> list[str]:
        """Return a list of the valid moves for the active player."""
        return self._valid_moves

    def make_move(self, move: str) -> None:
        """Make the given chess move. The instance of ChessGame will be mutated, and will
        afterwards represent the game state after move is made.

        If move is not a currently valid move, raise a ValueError.
        """
        move_lowered = move.lower()

        if move_lowered not in self._valid_moves:
            raise ValueError(f'Move "{move}" is not valid')

        self._board = self._board_after_move(move_lowered, self._is_red_active)

        self._is_red_active = not self._is_red_active
        self._move_count += 1

        self._recalculate_valid_moves()

    def copy_and_make_move(self, move: str) -> ChessGame:
        """Make the given chess move in a copy of this ChessGame, and return that copy.

        If move is not a currently valid move, raise a ValueError.
        """
        return ChessGame(board=self._board_after_move(move, self._is_red_active),
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
        elif all(self._board[y][x] != _Piece('k', True) for y in range(0, 10) for x in range(0, 9)):
            return 'Black'
        elif all(self._board[y][x] != _Piece('k', False) for y in range(0, 10) for x in range(0, 9)):
            return 'Red'
        else:
            return None

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
                moves += self._find_moves_in_direction(board, pos, is_red, (1, 0))
                moves += self._find_moves_in_direction(board, pos, is_red, (-1, 0))
                moves += self._find_moves_in_direction(board, pos, is_red, (0, 1))
                moves += self._find_moves_in_direction(board, pos, is_red, (0, -1))
            elif kind == 'h':
                # The if-statements are 'horse-leg' condition checks
                if pos[0] != 0 and board[pos[0] - 1][pos[1]] is None:
                    moves += self._find_moves_in_direction(board, pos, is_red, (-2, 1), limit=1)
                    moves += self._find_moves_in_direction(board, pos, is_red, (-2, -1), limit=1)
                if pos[0] != 9 and board[pos[0] + 1][pos[1]] is None:
                    moves += self._find_moves_in_direction(board, pos, is_red, (2, 1), limit=1)
                    moves += self._find_moves_in_direction(board, pos, is_red, (2, -1), limit=1)
                if pos[1] != 0 and board[pos[0]][pos[1] - 1] is None:
                    moves += self._find_moves_in_direction(board, pos, is_red, (1, -2), limit=1)
                    moves += self._find_moves_in_direction(board, pos, is_red, (-1, -2), limit=1)
                if pos[1] != 8 and board[pos[0]][pos[1] + 1] is None:
                    moves += self._find_moves_in_direction(board, pos, is_red, (1, 2), limit=1)
                    moves += self._find_moves_in_direction(board, pos, is_red, (-1, 2), limit=1)
            elif kind == 'e':
                if pos[0] not in {0, 5}:  # Can move towards black base
                    # The if-statements are 'elephant-leg' condition checks
                    if pos[1] != 0 and board[pos[0] - 1][pos[1] - 1] is None:
                        moves += self._find_moves_in_direction(board, pos, is_red, (-2, -2), limit=1)
                    if pos[1] != 8 and board[pos[0] - 1][pos[1] + 1] is None:
                        moves += self._find_moves_in_direction(board, pos, is_red, (-2, 2), limit=1)
                if pos[0] not in {4, 9}:  # Can move towards red base
                    if pos[1] != 0 and board[pos[0] + 1][pos[1] - 1] is None:
                        moves += self._find_moves_in_direction(board, pos, is_red, (2, -2), limit=1)
                    if pos[1] != 8 and board[pos[0] + 1][pos[1] + 1] is None:
                        moves += self._find_moves_in_direction(board, pos, is_red, (2, 2), limit=1)
            elif kind == 'a':
                # Movement restricted in palace
                if pos[0] not in {2, 9}:
                    if pos[1] != 3:
                        moves += self._find_moves_in_direction(board, pos, is_red, (1, -1), limit=1)
                    if pos[1] != 5:
                        moves += self._find_moves_in_direction(board, pos, is_red, (1, 1), limit=1)
                if pos[0] not in {0, 7}:
                    if pos[1] != 3:
                        moves += self._find_moves_in_direction(board, pos, is_red, (-1, -1), limit=1)
                    if pos[1] != 5:
                        moves += self._find_moves_in_direction(board, pos, is_red, (-1, 1), limit=1)
            elif kind == 'k':
                # Movement restricted in palace
                if pos[0] not in {2, 9}:
                    moves += self._find_moves_in_direction(board, pos, is_red, (1, 0), limit=1)
                if pos[0] not in {0, 7}:
                    moves += self._find_moves_in_direction(board, pos, is_red, (-1, 0), limit=1)
                if pos[1] != 3:
                    moves += self._find_moves_in_direction(board, pos, is_red, (0, -1), limit=1)
                if pos[1] != 5:
                    moves += self._find_moves_in_direction(board, pos, is_red, (0, 1), limit=1)
                # Confront
                if is_red:
                    king_row = pos[0] - 1
                    while king_row >= 0:
                        if board[king_row][pos[1]] is not None:
                            if board[king_row][pos[1]].kind == 'k':
                                moves.append(_get_wxf_movement(board, pos, (king_row, pos[1]), is_red))
                            break
                        king_row -= 1
                else:  # not is_red
                    king_row = pos[0] + 1
                    while king_row <= 9:
                        if board[king_row][pos[1]] is not None:
                            if board[king_row][pos[1]].kind == 'k':
                                moves.append(
                                    _get_wxf_movement(board, pos, (king_row, pos[1]), is_red))
                            break
                        king_row += 1
            elif kind == 'c':
                moves += self._find_moves_in_direction(board, pos, is_red, (1, 0), capture=False)
                moves += self._find_moves_in_direction(board, pos, is_red, (-1, 0), capture=False)
                moves += self._find_moves_in_direction(board, pos, is_red, (0, 1), capture=False)
                moves += self._find_moves_in_direction(board, pos, is_red, (0, -1), capture=False)
            else:  # kind == 'p'
                if is_red:
                    moves += self._find_moves_in_direction(board, pos, is_red, (-1, 0), limit=1)
                    if pos[0] <= 4:  # Crossed the river
                        moves += self._find_moves_in_direction(board, pos, is_red, (0, 1), limit=1)
                        moves += self._find_moves_in_direction(board, pos, is_red, (0, -1), limit=1)
                else:  # not is_red
                    moves += self._find_moves_in_direction(board, pos, is_red, (1, 0), limit=1)
                    if pos[0] >= 5:  # Crossed the river
                        moves += self._find_moves_in_direction(board, pos, is_red, (0, 1), limit=1)
                        moves += self._find_moves_in_direction(board, pos, is_red, (0, -1), limit=1)

        return moves

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

    def _board_after_move(self, move: str, is_red: bool) -> list[list[Optional[_Piece]]]:
        """Return a copy of self._board representing the state of the board after making move.
        """
        board_copy = copy.deepcopy(self._board)

        start_pos = _wxf_to_index(self._board, move[0:2], is_red)
        end_pos = _get_index_movement(self._board, move, is_red)

        board_copy[end_pos[0]][end_pos[1]] = board_copy[start_pos[0]][start_pos[1]]
        board_copy[start_pos[0]][start_pos[1]] = None

        return board_copy

    def _recalculate_valid_moves(self) -> None:
        """Update the valid moves for this game board."""
        self._valid_moves = self._calculate_moves_for_board(self._board, self._is_red_active)


def print_board(board: list[list[Optional[_Piece]]]) -> None:
    """Print the string representation of the given board.

    The board should look similar to what was drawn in the docstring for ChessGame.__init__.
    """
    row_normal = '丨    丨    丨    丨    丨    丨    丨    丨    丨'
    row_down = '丨    丨    丨    丨 \  丨  / 丨    丨    丨    丨'
    row_up = '丨    丨    丨    丨 /  丨  \ 丨    丨    丨    丨'
    print('一    二    三    四    五    六    七    八    九   (Black)\n'
          f'{_print_row(board, 0)}\n'
          f'{row_down}\n'
          f'{_print_row(board, 1)}\n'
          f'{row_up}\n'
          f'{_print_row(board, 2)}\n'
          f'{row_normal}\n'
          f'{_print_row(board, 3)}\n'
          f'{row_normal}\n'
          f'{_print_row(board, 4)}\n'
          '丨    一    楚    河    一    汉    界    一    丨\n'
          f'{_print_row(board, 5)}\n'
          f'{row_normal}\n'
          f'{_print_row(board, 6)}\n'
          f'{row_normal}\n'
          f'{_print_row(board, 7)}\n'
          f'{row_down}\n'
          f'{_print_row(board, 8)}\n'
          f'{row_up}\n'
          f'{_print_row(board, 9)}\n'
          '九    八    七    六    五    四    三    二    一    (Red)\n')


def _print_row(board: list[list[Optional[_Piece]]], row: int) -> str:
    """Returns the row representation at a given row of the board."""
    str_so_far = ''
    for i in range(0, 8):
        str_so_far += f'{_print_piece(board, row, i)}----'
    str_so_far += f'{_print_piece(board, row, 8)}'
    return str_so_far


def _print_piece(board: list[list[Optional[_Piece]]], y: int, x: int) -> str:
    """Returns the piece representation at the given coordinate of the board."""
    piece = board[y][x]
    try:
        return PIECES[(piece.kind, piece.is_red)]
    except AttributeError:
        if x in {0, 8}:
            return '丨'
        elif y in {0, 9}:
            return '一'
        else:
            return '十'


def _get_index_movement(board: list[list[Optional[_Piece]]],
                        move: str, is_red: bool) -> tuple[int, int]:
    """Return the end position of a move, given the move in wxf notation and the colour.

    Preconditions:
        - The move given in wxf notation is legal

    >>> g = ChessGame()
    >>> board = g.get_board()
    >>> _get_index_movement(board, 'c2.5', True)
    (7, 4)
    >>> _get_index_movement(board, 'c8.6', False)
    (2, 5)
    >>> _get_index_movement(board, 'h2+3', False)
    (2, 2)
    >>> _get_index_movement(board, 'e3+5', True)
    (7, 4)
    >>> _get_index_movement(board, 'r9+2', True)
    (7, 0)
    >>> _get_index_movement(board, 'c8-1', False)
    (1, 7)
    """
    y, x = _wxf_to_index(board, move[0:2], is_red)
    sign = move[2]
    value = int(move[3])
    piece = board[y][x]
    if sign == '.' and is_red:
        return (y, 9 - value)
    elif sign == '.' and not is_red:
        return (y, value - 1)
    elif piece.kind in {'r', 'k', 'c', 'p'}:  # they all move vertically
        if is_red and sign == '+' or not is_red and sign == '-':
            return (y - value, x)
        else:  # black and -, or red and +
            return (y + value, x)
    elif piece.kind == 'h' and is_red:
        vert = 3 - abs(x - (9 - value))  # Vertical steps = 3 - horizontal steps
        if sign == '+':
            return (y - vert, 9 - value)
        else:  # sign == '-'
            return (y + vert, 9 - value)
    elif piece.kind == 'h' and not is_red:
        vert = 3 - abs(x - (value - 1))
        if sign == '+':
            return (y + vert, value - 1)
        else:  # sign == '-'
            return (y - vert, value - 1)
    else:  # piece.kind in {'e', 'a'}  elephant and assistant both move in perfect diagonal lines
        # Determine the vertical steps
        if piece.kind == 'e':
            vert = 2
        else:  # piece.kind == 'a'
            vert = 1

        if sign == '+' and is_red:
            return (y - vert, 9 - value)
        elif sign == '-' and is_red:
            return (y + vert, 9 - value)
        elif sign == '+' and not is_red:
            return (y + vert, value - 1)
        else:  # sign == '-' and not is_red
            return (y - vert, value - 1)


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
    piece_type = piece_lower[0]
    location = piece_lower[1]
    if location in {'+', '-'}:
        y, x = 0, 0

        locations_so_far = []
        # Search the board
        while y <= 9:
            if board[y][x] == _Piece(piece_type, is_red):
                locations_so_far.append((y, x))
            x += 1
            if x >= 9:
                y += 1
                x = 0

        coord1, coord2 = (), ()
        out = False
        for first_piece in locations_so_far:
            for second_piece in locations_so_far:
                if first_piece != second_piece and first_piece[1] == second_piece[1]:
                    coord1, coord2 = sorted((first_piece, second_piece))
                    out = True
                    break
            if out:
                break

        if coord1 == () and coord2 == ():
            raise ValueError

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
        while y <= 9 and board[y][x] != _Piece(piece_type, is_red):
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
