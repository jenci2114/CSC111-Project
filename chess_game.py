"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This Python module contains the class ChessGame, which is
responsible for Chinese Chess functioning; class _Piece, which
represents Chinese Chess pieces. Also, this module
contains methods necessary for converting between coordinate
notation and wxf (i.e. World Xiangqi Foundation) notations.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei"""

from __future__ import annotations
from typing import Optional
import statistics
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
    #
    # Private Representation Invariants:
    #   - _board must be a legal Chinese Chess board (e.g. cannot contain 3 red elephants, etc.)
    #   - all moves in _valid_moves must be legal (e.g. cannot have a pawn like a horse, etc.)
    #   - 0 <= _move_count <= _MAX_MOVES
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

        Note: the index numbering above is VERY different from what is used for the WXF notation,
        please use the conversion functions below to convert between the two.
        """
        if board is not None:
            self._board = board  # load the given board
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

        self._recalculate_valid_moves()  # Ensure that self._valid_moves is up-to-date

    def __str__(self) -> str:
        """Return the string representation of the board, who is active, and valid moves.

        If the game is finished, return the string representation of the board and who wins.
        """
        # Print (not return) the board representation in a visual way
        print_board(self._board)
        winner = self.get_winner()

        if winner is None:  # the if-branch returns who's turn is it and the valid moves
            turn_message = ''
            if self._is_red_active:
                turn_message += "Red's turn.\n"
            else:
                turn_message += "Black's turn.\n"
            return turn_message + f'Valid moves: {self._valid_moves}'
        elif winner == 'Draw':  # the elif-branch and the else-branch return the result
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
        # Ensure that all moves - whether given in upper-case or lower-case - will be recognized
        move_lowered = move.lower()

        # Invalid move
        if move_lowered not in self._valid_moves:
            raise ValueError(f'Move "{move}" is not valid')

        # Update board
        self._board = self._board_after_move(move_lowered, self._is_red_active)

        self._is_red_active = not self._is_red_active  # Whoever just played won't play again
        self._move_count += 1

        self._recalculate_valid_moves()

    def copy_and_make_move(self, move: str) -> ChessGame:
        """Make the given chess move in a copy of this ChessGame, and return that copy.

        If move is not a currently valid move, raise a ValueError.
        """
        if move not in self._valid_moves:
            raise ValueError(f'Move "{move}" is not valid')

        # Create a new instance of ChessGame accordingly then return it
        return ChessGame(board=self._board_after_move(move, self._is_red_active),
                         red_active=not self._is_red_active,
                         move_count=self._move_count + 1)

    def is_red_move(self) -> bool:
        """Return whether the red player is to move next."""
        return self._is_red_active

    def get_winner(self) -> Optional[str]:
        """Return the winner of the game (red or black) or 'draw' if the game ended in a draw.

        Return None if the game is not over.
        """
        if self._move_count >= _MAX_MOVES:  # Exceeded maximum number of moves, so draw
            return 'Draw'
        elif all(self._board[y][x] != _Piece('k', True)
                 for y in range(0, 10) for x in range(0, 9)):  # Cannot find red king
            return 'Black'
        elif all(self._board[y][x] != _Piece('k', False)
                 for y in range(0, 10) for x in range(0, 9)):  # Cannot find black king
            return 'Red'
        else:  # Game not over yet
            return None

    def _calculate_moves_for_board(self, board: list[list[Optional[_Piece]]],
                                   is_red_active: bool) -> list[str]:
        """Return all possible moves on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        """
        moves = []  # accumulator

        for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:  # search entire board
            piece = board[pos[0]][pos[1]]
            if piece is None or piece.is_red != is_red_active:
                continue  # Not your piece, can't do anything, so skip

            if piece.kind == 'r':
                moves += self._calculate_moves_for_chariot(board, pos)
            elif piece.kind == 'h':
                moves += self._calculate_moves_for_horse(board, pos)
            elif piece.kind == 'e':
                moves += self._calculate_moves_for_elephant(board, pos)
            elif piece.kind == 'a':
                moves += self._calculate_moves_for_assistant(board, pos)
            elif piece.kind == 'k':
                moves += self._calculate_moves_for_king(board, pos)
            elif piece.kind == 'c':
                moves += self._calculate_moves_for_cannon(board, pos)
            else:  # kind == 'p'
                moves += self._calculate_moves_for_pawn(board, pos)

        return moves

    def _calculate_moves_for_chariot(self, board: list[list[Optional[_Piece]]],
                                     pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the chariot at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - a chariot is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 0))
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 0))
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, 1))
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, -1))

        return moves

    def _calculate_moves_for_horse(self, board: list[list[Optional[_Piece]]],
                                   pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the horse at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - a horse is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        # The if-statements are 'horse-leg' condition checks
        if pos[0] != 0 and board[pos[0] - 1][pos[1]] is None:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-2, 1), limit=1)
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-2, -1), limit=1)
        if pos[0] != 9 and board[pos[0] + 1][pos[1]] is None:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (2, 1), limit=1)
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (2, -1), limit=1)
        if pos[1] != 0 and board[pos[0]][pos[1] - 1] is None:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, -2), limit=1)
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, -2), limit=1)
        if pos[1] != 8 and board[pos[0]][pos[1] + 1] is None:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 2), limit=1)
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 2), limit=1)

        return moves

    def _calculate_moves_for_elephant(self, board: list[list[Optional[_Piece]]],
                                      pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the elephant at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - an elephant is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        if pos[0] not in {0, 5}:  # Can move towards black base
            # The if-statements are 'elephant-leg' condition checks
            if pos[1] != 0 and board[pos[0] - 1][pos[1] - 1] is None:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (-2, -2), limit=1)
            if pos[1] != 8 and board[pos[0] - 1][pos[1] + 1] is None:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (-2, 2), limit=1)
        if pos[0] not in {4, 9}:  # Can move towards red base
            if pos[1] != 0 and board[pos[0] + 1][pos[1] - 1] is None:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (2, -2), limit=1)
            if pos[1] != 8 and board[pos[0] + 1][pos[1] + 1] is None:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (2, 2), limit=1)

        return moves

    def _calculate_moves_for_assistant(self, board: list[list[Optional[_Piece]]],
                                       pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the assistant at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - an assistant is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        # Movement restricted in palace
        if pos[0] not in {2, 9}:
            if pos[1] != 3:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, -1), limit=1)
            if pos[1] != 5:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 1), limit=1)
        if pos[0] not in {0, 7}:
            if pos[1] != 3:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, -1), limit=1)
            if pos[1] != 5:
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 1), limit=1)

        return moves

    def _calculate_moves_for_king(self, board: list[list[Optional[_Piece]]],
                                  pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the king at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - a king is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        # Movement restricted in palace
        if pos[0] not in {2, 9}:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 0), limit=1)
        if pos[0] not in {0, 7}:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 0), limit=1)
        if pos[1] != 3:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, -1), limit=1)
        if pos[1] != 5:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, 1), limit=1)
        # Confront check
        if piece.is_red:
            king_row = pos[0] - 1
            while king_row >= 0:  # Search 'upwards' (index going down)
                if board[king_row][pos[1]] is not None:
                    if board[king_row][pos[1]].kind == 'k':  # Can confront other king
                        moves.append(_get_wxf_movement(board, pos, (king_row, pos[1]),
                                                       piece.is_red))
                    else:
                        break
                king_row -= 1  # Search the place right above in the next iteration
        else:  # not is_red
            king_row = pos[0] + 1
            while king_row <= 9:  # Search 'downwards' (index going up)
                if board[king_row][pos[1]] is not None:
                    if board[king_row][pos[1]].kind == 'k':  # Can confront other king
                        moves.append(
                            _get_wxf_movement(board, pos, (king_row, pos[1]), piece.is_red))
                    else:
                        break
                king_row += 1  # Search the place right below in the next iteration

        return moves

    def _calculate_moves_for_cannon(self, board: list[list[Optional[_Piece]]],
                                    pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the cannon at the given position
        on a given board with a given active player.

        Note: the mechanism for cannon firing is written in ChessGame._find_moves_in_direction.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - a cannon is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 0), capture=False)
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 0), capture=False)
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, 1), capture=False)
        moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, -1), capture=False)

        return moves

    def _calculate_moves_for_pawn(self, board: list[list[Optional[_Piece]]],
                                  pos: tuple[int, int]) -> list[str]:
        """Return all possible moves for the pawn at the given position
        on a given board with a given active player.

        Preconditions:
            - board must be in a legal state (e.g. cannot have three red cannons, etc.)
            - a pawn is on the given position of the board
        """
        piece = board[pos[0]][pos[1]]
        moves = []  # accumulator

        if piece.is_red:
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (-1, 0), limit=1)
            if pos[0] <= 4:  # Crossed the river, so can move horizontally
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, 1), limit=1)
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, -1), limit=1)
        else:  # not is_red
            moves += self._find_moves_in_direction(board, pos, piece.is_red, (1, 0), limit=1)
            if pos[0] >= 5:  # Crossed the river, so can move horizontally
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, 1), limit=1)
                moves += self._find_moves_in_direction(board, pos, piece.is_red, (0, -1), limit=1)

        return moves

    def _find_moves_in_direction(self, board: list[list[Optional[_Piece]]],
                                 pos: tuple[int, int], is_red: bool, direction: tuple[int, int],
                                 limit: int = None, capture: bool = None) -> list[str]:
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
        moves = []  # accumulator

        kind = board[pos[0]][pos[1]].kind
        stop = False
        i = 1
        while not stop:  # Keep searching to the given direction
            # Add one step towards the given direction
            y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i

            if x < 0 or y < 0 or x > 8 or y > 9:
                break  # Out of bounds

            contents = board[y][x]  # What's currently on the spot being searched

            # Store this move first, will later decide whether to add this move to the accumulator
            move = _get_wxf_movement(board, pos, (y, x), is_red)

            if contents is not None:  # the spot being searched contains another piece
                stop = True  # Can't move any further; this is the last iteration of the whlie loop
                if kind == 'c':  # Check if this cannon can be fired in the given direction
                    i += 1
                    y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i
                    while 0 <= x <= 8 and 0 <= y <= 9:  # only check non-out-of-bound locations
                        if board[y][x] is not None and board[y][x].is_red == is_red:
                            # Cannot fire cannon since it's blocked by an ally piece
                            break
                        if board[y][x] is not None and board[y][x].is_red != is_red:
                            # Can fire cannon because found an opponent piece
                            moves.append(_get_wxf_movement(board, pos, (y, x), is_red))
                            break
                        i += 1
                        y, x = pos[0] + direction[0] * i, pos[1] + direction[1] * i

                # If this piece is allowed to capture, then add the move to the accumulator
                if contents.is_red != is_red and capture is not False:
                    moves.append(move)
            else:  # Found an empty square, we can go there, so add the move to the accumulator
                moves.append(move)

            i += 1  # Search for the next spot in the next iteration of the while loop

            # For pieces that can only move by x steps, stop when the step limit is reached
            if limit is not None and i > limit:
                stop = True

        return moves

    def get_board(self) -> list[list[Optional[_Piece]]]:
        """Return the board representation."""
        return self._board

    def _board_after_move(self, move: str, is_red: bool) -> list[list[Optional[_Piece]]]:
        """Return a copy of self._board representing the state of the board after making move.
        """
        board_copy = copy.deepcopy(self._board)  # Deepcopy the board (no aliasing to self._board)

        start_pos = _wxf_to_index(self._board, move[0:2], is_red)  # Obtain which piece is moving
        end_pos = _get_index_movement(self._board, move, is_red)  # Obtain to where the piece moves

        # The destination is now occupied by the piece moving
        board_copy[end_pos[0]][end_pos[1]] = board_copy[start_pos[0]][start_pos[1]]
        board_copy[start_pos[0]][start_pos[1]] = None  # The starting spot is now empty

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
    """Returns the row representation at a given row of the board
    This is a helper function for print board"""
    str_so_far = ''
    # Since there are 9 columns in each row and the for loop iterates 8 times
    # we will leave the last column separately.
    for i in range(0, 8):
        str_so_far += f'{_print_piece(board, row, i)}----'
    # print the last column
    str_so_far += f'{_print_piece(board, row, 8)}'
    return str_so_far


def _print_piece(board: list[list[Optional[_Piece]]], y: int, x: int) -> str:
    """Returns the piece representation at the given coordinate of the board.
    This is a helper function of _print_row"""
    piece = board[y][x]  # the coordinate of the piece
    try:  # if the piece is not empty
        return PIECES[(piece.kind, piece.is_red)]
    except AttributeError:  # if the piece is empty
        if x in {0, 8}:  # if it is in the left or right most of the column
            return '丨'
        elif y in {0, 9}:  # if it is at the top or at the bottom of the row
            return '一'
        else:
            return '十'  # if it is inside the board


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
    y, x = _wxf_to_index(board, move[0:2], is_red)  # the initial coordinate of the piece
    sign = move[2]  # either + or - o
    # if the move is horizontally, then it represents the final position of x coords.
    # if the move is vertically, it represents the piece move by how much
    # if the move is diagonal, it represents the final position of x coord
    value = int(move[3])
    piece = board[y][x]
    if sign == '.' and is_red:
        return (y, 9 - value)  # change the x coordinate of the piece when the piece is red and return
    elif sign == '.' and not is_red:
        return (y, value - 1)  # change the x coordinate of the piece when the piecblack red and return
    elif piece.kind in {'r', 'k', 'c', 'p'}:  # they all move vert, change the y coords
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

    Preconditions:
        - board is a legal Chinese Chess board (e.g. there cannot be three red elephants, etc.)

    >>> g = ChessGame()
    >>> board = g.get_board()
    >>> _wxf_to_index(board, 'c2', True)
    (7, 7)
    >>> _wxf_to_index(board, 'a4', False)
    (0, 3)
    """
    piece_lower = piece.lower()  # Lowercase the wxf notation of the piece for consistency
    piece_type = piece_lower[0]  # Extract first letter/number
    location = piece_lower[1]  # Extract second letter/number/symbol

    if piece_type.isdigit():  # piece is one of the 3+ vertically aligned pieces
        return _wxf_to_index_more_than_three_aligned(board, piece, is_red)
    if location in {'+', '-'}:  # piece is one of the two vertically aligned pieces
        return _wxf_to_index_two_aligned(board, piece, is_red)
    else:  # location is a number
        if is_red:
            x = 9 - int(location)  # Convert between wxf coords and index coords
        else:  # not is_red
            x = int(location) - 1  # Convert between wxf coords and index coords

        y = 0
        # Find the piece in the given column (fixing the x-value)
        while y <= 9 and board[y][x] != _Piece(piece_type, is_red):
            y += 1

        if y > 9:  # Out of bound, piece not found
            print_board(board)
            print(piece)
            raise ValueError('Invalid piece')
        else:  # Piece is found, return it
            return (y, x)


def _wxf_to_index_two_aligned(board: list[list[Optional[_Piece]]], piece: str,
                              is_red: bool) -> tuple[int, int]:
    """Return the coordinate of a piece (y, x) given the wxf notation for a piece (e.g. 'c6').

    Raise ValueError if not found.

    Preconditions:
        - board is a legal Chinese Chess board (e.g. there cannot be three red elephants, etc.)
        - piece represents one of the two vertically aligned pieces of the same kind, therefore:
        - piece[1] in {'+', '-'}
    """
    piece_lower = piece.lower()  # Lowercase the wxf notation of the piece for consistency
    piece_type = piece_lower[0]  # Extract first letter
    location = piece_lower[1]  # Extract the second symbol

    y, x = 0, 0

    locations_so_far = []  # Accumulator
    while y <= 9:  # Collect all the pieces of the given type
        if board[y][x] == _Piece(piece_type, is_red):
            locations_so_far.append((y, x))
        x += 1
        if x >= 9:  # Move onto the next row, reset to the first column
            y += 1
            x = 0

    coord1, coord2 = (), ()
    out = False

    # Search for aligned pairs within all pieces of the given type
    for first_piece in locations_so_far:
        for second_piece in locations_so_far:
            # If the pair is not the same piece and they are in the same column
            if first_piece != second_piece and first_piece[1] == second_piece[1]:
                # Sort them so coord1 has a smaller y-coordinate
                coord1, coord2 = sorted((first_piece, second_piece))  # Get their coordinates
                out = True  # Use to break outer loop
                break  # Break inner loop
        if out:
            break  # Break outer loop

    if coord1 == () and coord2 == ():  # Piece not found
        raise ValueError('Invalid piece')

    if (is_red and location == '+') or (not is_red and location == '-'):  # Want the 'upper' piece
        return coord1  # Smaller y-value so it's the 'upper' piece
    else:  # Want the 'lower' piece
        return coord2  # Larger y-value so it's the 'lower' piece


def _wxf_to_index_more_than_three_aligned(board: list[list[Optional[_Piece]]], piece: str,
                                          is_red: bool) -> tuple[int, int]:
    """Return the coordinate of a piece (y, x) given the wxf notation for a piece (e.g. 'c6').

    Raise ValueError if not found.

    Preconditions:
        - board is a legal Chinese Chess board (e.g. there cannot be three red elephants, etc.)
        - piece represents one of the 3+ vertically aligned pieces of the same kind, therefore:
        - piece[0].isdigit()
    """
    piece_lower = piece.lower()  # Lowercase the wxf notation of the piece for consistency
    piece_type = piece_lower[0]  # Extract first number

    y, x = 0, 0

    locations_so_far = []  # Accumulator
    while y <= 9:  # Collect all the pieces of the given type
        if board[y][x] == _Piece('p', is_red):
            locations_so_far.append((y, x))
        x += 1
        if x >= 9:  # Move onto the next row, reset to the first column
            y += 1
            x = 0

    x_values = [l[1] for l in locations_so_far]
    # There is at most 5 pieces of the same kind, so to get the 3+ in the same column,
    # we take the mode of its x-value
    mode = statistics.mode(x_values)
    aligned_pieces = [l for l in locations_so_far if l[1] == mode]
    aligned_pieces.sort()  # In order of increasing x-value (index)

    if len(aligned_pieces) < 3:  # We don't have 3 pieces in the same column
        raise ValueError('Invalid piece')

    if is_red:
        return aligned_pieces[int(piece_type) - 1]  # First one has index 0 in aligned_pieces
    else:
        return aligned_pieces[-int(piece_type)]  # First one is the last in aligned_pieces


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

    piece_type = piece.kind
    x = pos[1]

    # Search for all pieces present in the column
    pieces = []
    y = 0
    while y <= 9:
        if board[y][x] == _Piece(piece_type, is_red):
            pieces.append((y, x))
        y += 1

    if len(pieces) == 1:  # there is only one piece with the same type
        if is_red:
            return piece_type + str(9 - x)
        else:  # not is_red
            return piece_type + str(x + 1)
    elif len(pieces) == 2:  # there are 2 pieces on the board with the same type
        if (is_red and pieces.index((pos[0], pos[1])) == 1) \
                or (not is_red and pieces.index((pos[0], pos[1])) == 0):
            return piece_type + '-'
        else:
            return piece_type + '+'
    else:
        if is_red:
            return str(pieces.index((pos[0], pos[1])) + 1) + str(9 - x)
        else:  # not is_red
            return str(len(pieces) - pieces.index((pos[0], pos[1]))) + str(x + 1)


def calculate_absolute_points(board: list[list[Optional[_Piece]]]) -> int:
    """Calculate the absolute points for the given board.
    Each piece on the board holds a certain value and all pieces on the board will be
    accounted in calculating relative points. Red pieces contribute to positive points and
    black pieces contribute to negative points. Different types of pieces have different values:
        - King: 10000
        - Rook/Chariot: 900
        - Cannon: 450
        - Horse: 400
        - Elephant: 200
        - Advisor: 200
        - Pawn (after crossing river): 200
        - Pawn (before crossing river): 100
    Additionally, the locations of certain pieces affect the absolute points (which are based
    on the discussion of group members):
        - The horse being in the 'barn' will be awarded bonus points (+70)
        - The horse being on the diagonal of opponent's palace will be awarded bonus points (+30)
        - The elephant being 'on-guard' will be awarded bonus points (+20)
        - The elephant being 'off-guard' will be penalized (-10)
        - The cannon being in the middle will be awarded bonus points (+60)
        - The cannon being in the back end of opponent's side will be awarded bonus points (+30)
        - The king not being on the bottom line will be penalized (-10)
        - The chariot being stuck in the corner will be penalized (-10)
        - The advisor being 'off-guard' will be penalized (-10)

    Preconditions:
        - board is in the format as defined previously.
    """
    points_so_far = 0
    for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:
        piece = board[pos[0]][pos[1]]
        if piece is None:
            continue
        else:
            if piece.kind == 'p':
                points_so_far += _absolute_pawn(board, pos)
            elif piece.kind == 'h':
                points_so_far += _absolute_horse(board, pos)
            elif piece.kind == 'e':
                points_so_far += _absolute_elephant(board, pos)
            elif piece.kind == 'c':
                points_so_far += _absolute_cannon(board, pos)
            elif piece.kind == 'r':
                points_so_far += _absolute_chariot(board, pos)
            elif piece.kind == 'k':
                points_so_far += _absolute_king(board, pos)
            else:  # piece.kind == 'a'
                points_so_far += _absolute_advisor(board, pos)
    return points_so_far


def _absolute_pawn(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all pawns on the board. If the pawn does not cross river,
    it is 100 points. Otherwise, it is 200 points
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - a pawn is on the given position of the board
    """
    points_so_far = 0
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    if (piece.is_red and pos[0] <= 4) or (not piece.is_red and pos[0] >= 5):
        points_so_far += 200 * side
    else:
        points_so_far += 100 * side

    return points_so_far


def _absolute_horse(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all pawns on the board, each horse is 400 points.
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - a horse is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 400

    # Horse in the barn check
    if pos[0] == 1 and pos[1] in {2, 6} and side == 1:
        points_so_far += 70
    elif pos[0] == 8 and pos[1] in {2, 6} and side == -1:
        points_so_far -= 70

    # Horse in the palace check
    if pos[0] == 2 and pos[1] in {3, 5} and side == 1:
        points_so_far += 30
    elif pos[0] == 7 and pos[1] in {3, 5} and side == -1:
        points_so_far -= 30

    return points_so_far


def _absolute_elephant(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all elephants on the board, each elephant is 200 points'
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - an elephant is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 200

    # Elephant on-guard check
    if pos[0] == 7 and pos[1] == 4 and side == 1:
        points_so_far += 20
    elif pos[0] == 2 and pos[1] == 4 and side == -1:
        points_so_far -= 20

    # Elephant off-guard penalty
    if pos[0] == 7 and pos[1] in {0, 8} and side == 1:
        points_so_far -= 10
    elif pos[0] == 2 and pos[1] in {0, 8} and side == -1:
        points_so_far += 10

    return points_so_far


def _absolute_cannon(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all cannons on the board, each cannon is 450 points.
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - an cannon is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 450

    # Cannon in the middle check
    if pos[1] == 4 and pos[0] in {3, 4, 5} and side == 1:
        points_so_far += 60
    elif pos[1] == 4 and pos[0] in {4, 5, 6} and side == -1:
        points_so_far -= 60

    # Cannon in the back check
    if pos[0] == 0 and pos[1] in {0, 1, 7, 8} and side == 1:
        points_so_far += 30
    elif pos[0] == 9 and pos[1] in {0, 1, 7, 8} and side == -1:
        points_so_far -= 30

    return points_so_far


def _absolute_king(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all cannons on the board, each cannon is 450 points.
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - an cannon is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 10000

    # King unprotected penalty
    if pos[0] in {7, 8} and side == 1:
        points_so_far -= 10
    elif pos[0] in {1, 2} and side == -1:
        points_so_far += 10

    return points_so_far


def _absolute_chariot(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all chariot on the board, each chariot is 900 points.
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - an cannon is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 900

    # Chariot stuck penalty
    if pos[0] == 9 and pos[1] in {0, 8} and side == 1:
        points_so_far -= 10
    elif pos[0] == 0 and pos[1] in {0, 8} and side == -1:
        points_so_far += 10

    return points_so_far


def _absolute_advisor(board: list[list[Optional[_Piece]]], pos: tuple[int, int]) -> int:
    """Calculate the points for all advisor on the board, each advisor is 200 points.
    Red pieces contribute to positive points and
    black pieces contribute to negative points.

    Preconditions:
        - board must be in a legal state (e.g. cannot have three red cannons, etc.)
        - an advisor is on the given position of the board
    """
    piece = board[pos[0]][pos[1]]
    if piece.is_red:
        side = 1
    else:
        side = -1

    points_so_far = side * 200

    # Assistant off-guard penalty
    if pos[0] == 7 and pos[1] in {3, 5} and side == 1:
        points_so_far -= 10
    elif pos[0] == 2 and pos[1] in {3, 5} and side == -1:
        points_so_far += 10

    return points_so_far


def piece_count(board: list[list[Optional[_Piece]]]) -> int:
    """Return how many pieces there are on the board at the moment.

    Preconditions:
        - board is a list of list representing a valid Chinese Chess board
    """
    pieces_so_far = 0
    for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:
        if board[pos[0]][pos[1]] is not None:
            pieces_so_far += 1

    return pieces_so_far


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
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 150,
    #     # Some code here is copied from the Assignment 2 package, and we disabled all the
    #     # errors present on the provided Assignment 2 package.
    #     'disable': ['E9989', 'E1136', 'E9998', 'W1401', 'R1702',
    #                 'R0912', 'R0913', 'R0914', 'R0915', 'R0201'],
    #     'extra-imports': ['typing', 'statistics', 'copy']
    # })

    import doctest
    doctest.testmod()
