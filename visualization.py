"""..."""

import pygame
from chess_game import ChessGame, _index_to_wxf, _wxf_to_index, \
    _get_index_movement, _get_wxf_movement
from player import Player, RandomPlayer

# Initialize Pygame
pygame.init()

# Load images
BOARD_IMAGE = pygame.image.load('chessboard/board/004.jpg')
COORD_IMAGE = pygame.image.load('chessboard/board/xy2.png')
BLACK_ASSISTANT = pygame.image.load('chessboard/piece/ba.png')
BLACK_ELEPHANT = pygame.image.load('chessboard/piece/bb.png')
BLACK_CANNON = pygame.image.load('chessboard/piece/bc.png')
BLACK_KING = pygame.image.load('chessboard/piece/bk.png')
BLACK_HORSE = pygame.image.load('chessboard/piece/bn.png')
BLACK_PAWN = pygame.image.load('chessboard/piece/bp.png')
BLACK_CHARIOT = pygame.image.load('chessboard/piece/br.png')
RED_ASSISTANT = pygame.image.load('chessboard/piece/ra.png')
RED_ELEPHANT = pygame.image.load('chessboard/piece/rb.png')
RED_CANNON = pygame.image.load('chessboard/piece/rc.png')
RED_KING = pygame.image.load('chessboard/piece/rk.png')
RED_HORSE = pygame.image.load('chessboard/piece/rn.png')
RED_PAWN = pygame.image.load('chessboard/piece/rp.png')
RED_CHARIOT = pygame.image.load('chessboard/piece/rr.png')
POSSIBLE_MOVE_FRAME = pygame.image.load('chessboard/piece/mask.png')
SELECTED_FRAME = pygame.image.load('chessboard/piece/mm.png')

PIECE_DICT = {('r', False): BLACK_CHARIOT, ('h', False): BLACK_HORSE,
              ('e', False): BLACK_ELEPHANT, ('a', False): BLACK_ASSISTANT,
              ('k', False): BLACK_KING, ('c', False): BLACK_CANNON,
              ('p', False): BLACK_PAWN, ('r', True): RED_CHARIOT, ('h', True): RED_HORSE,
              ('e', True): RED_ELEPHANT, ('a', True): RED_ASSISTANT, ('k', True): RED_KING,
              ('c', True): RED_CANNON, ('p', True): RED_PAWN}

# Load font TODO change font
FONT_BOLD = pygame.font.SysFont('Comic Sans MS', 36, bold=True)
FONT = pygame.font.SysFont('Comic Sans MS', 24)

# Define RGB colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)


class Game:
    """A simulation of Chinese Chess Game.

    Instance Attributes:
        - opponent: the computer player that plays as black.
    """
    # Private Instance Attributes:
    #   - _screen: The pygame screen to draw on.
    #   - _game: The chess game.
    #   - _curr_coord: The currently selected piece's coordinate.
    #   - _ready_to_move: Whether the human can move in one click.
    #   - _movement_indices: List of moves the human can make (in terms of coordinate indices).
    #   - _game_ended: Whether the game ended.
    opponent: Player
    _screen: pygame.Surface
    _game: ChessGame
    _curr_coord: tuple
    _ready_to_move: bool
    _movement_indices: list
    _game_ended: bool

    def __init__(self, player: Player) -> None:
        """Initialize the game."""
        pygame.init()
        self.opponent = player
        self._screen = pygame.display.set_mode((560, 645))
        self._game = ChessGame()
        self._curr_coord = ()
        self._ready_to_move = False
        self._movement_indices = []
        self._game_ended = False

    def run(self) -> None:
        """Run the game."""
        # Initialize chess game
        self._print_game()
        pygame.display.flip()

        # Event loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Exit the event loop
                    pygame.quit()
                    print('Thanks for playing!')
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and not self._ready_to_move and not self._game_ended:
                    self._get_possible_moves_for_piece(event.pos)
                    pygame.display.flip()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self._ready_to_move and not self._game_ended:
                    new_coordinate = pixel_to_coordinate((event.pos[0], event.pos[1]))
                    if new_coordinate not in self._movement_indices:  # Unselect this piece
                        self._print_game()
                        self._ready_to_move = False
                        pygame.display.flip()
                    else:  # Make the move!
                        wxf_move = _get_wxf_movement(self._game.get_board(),
                                                     self._curr_coord, new_coordinate, True)
                        self._game.make_move(wxf_move)
                        self._print_game()

                        # Mark where the piece was before the move
                        piece_frame_coord = coordinate_to_pixel(self._curr_coord)
                        piece_frame_rect = SELECTED_FRAME.get_rect(center=piece_frame_coord)
                        self._screen.blit(SELECTED_FRAME, piece_frame_rect)

                        self._ready_to_move = False
                        pygame.display.flip()

                        if self._check_for_end():
                            continue

                        # Computer's turn
                        opponent_wxf_move = self.opponent.make_move(self._game, wxf_move)
                        opponent_piece_coord = _wxf_to_index(self._game.get_board(),
                                                             opponent_wxf_move[0:2], False)
                        self._game.make_move(opponent_wxf_move)
                        self._print_game()

                        # Mark where the piece was before the move
                        opponent_piece_frame_coord = coordinate_to_pixel(opponent_piece_coord)
                        opponent_piece_frame_rect = \
                            SELECTED_FRAME.get_rect(center=opponent_piece_frame_coord)
                        self._screen.blit(SELECTED_FRAME, opponent_piece_frame_rect)
                        pygame.display.flip()

                        if self._check_for_end():
                            continue

    def _print_game(self) -> None:
        """Print the current state of the game."""
        self._screen.blit(BOARD_IMAGE, (0, 0))  # Display board
        self._screen.blit(COORD_IMAGE, (0, 0))  # Display coordinates
        for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:  # Display pieces
            piece = self._game.get_board()[pos[0]][pos[1]]
            if piece is not None:
                piece_coord = coordinate_to_pixel((pos[0], pos[1]))
                piece_rect = PIECE_DICT[(piece.kind, piece.is_red)].get_rect(center=piece_coord)
                self._screen.blit(PIECE_DICT[(piece.kind, piece.is_red)], piece_rect)

    def _get_possible_moves_for_piece(self, pos: tuple[int, int]) -> None:
        """Print the possible moves one can go with the selected piece (whose location is indicated
        by <pos>.
        """
        possible_moves = self._game.get_valid_moves()
        self._curr_coord = pixel_to_coordinate((pos[0], pos[1]))
        if not (0 <= self._curr_coord[0] <= 9 and 0 <= self._curr_coord[1] <= 8):
            return  # This place is outside of the board
        try:  # Check if this piece exists and belongs to red
            piece_wxf = _index_to_wxf(self._game.get_board(), self._curr_coord, True)
        except ValueError:
            return

        # Since this piece belongs to red, frame it to indicate that it is selected
        piece_frame_coord = coordinate_to_pixel(self._curr_coord)
        piece_frame_rect = SELECTED_FRAME.get_rect(center=piece_frame_coord)
        self._screen.blit(SELECTED_FRAME, piece_frame_rect)

        # Also frame where the selected piece can go
        piece_possible_moves = [move for move in possible_moves
                                if move[0:2] == piece_wxf]
        self._movement_indices = [_get_index_movement(self._game.get_board(), move, True)
                                  for move in piece_possible_moves]
        for coord in self._movement_indices:
            frame_coord = coordinate_to_pixel(coord)
            frame_rect = POSSIBLE_MOVE_FRAME.get_rect(center=frame_coord)
            self._screen.blit(POSSIBLE_MOVE_FRAME, frame_rect)

        self._ready_to_move = True

    def _check_for_end(self) -> bool:
        """Check (and return) whether the game ended. If so, stop the game and print who won."""
        if self._game.get_winner() is not None:
            if self._game.get_winner() == 'Red':
                self._game_ended = True
                # Display winning message
                message = FONT_BOLD.render('Congratulations! You won!', True, RED)
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(WHITE)
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = FONT.render('Please close this window.', True, RED)
            elif self._game.get_winner() == 'Black':
                self._game_ended = True
                # Display losing message
                message = FONT_BOLD.render('Too bad. You lost.', True, BLACK)
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(WHITE)
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = FONT.render('Please close this window.', True, BLACK)
            else:  # self._game.get_winner() == 'Draw'
                self._game_ended = True
                # Display draw message
                message = FONT_BOLD.render('No one won.', True, BLUE)
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(WHITE)
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = FONT.render('Please close this window.', True, BLUE)

            # Instructs the player to close the window
            closing_message_rect = closing_message.get_rect(center=(280, 350))
            closing_message_surface = pygame.Surface(closing_message.get_size())
            closing_message_surface.fill(WHITE)
            closing_message_surface.set_alpha(200)
            self._screen.blit(closing_message_surface, closing_message_rect)
            self._screen.blit(closing_message, closing_message_rect)
            pygame.display.flip()
        else:
            pass

        return self._game_ended


def coordinate_to_pixel(coordinate: tuple[int, int]) -> tuple[int, int]:
    """Convert the coordinate of the board (as in the list of list coordinate) to the pixel
    coordinate (of what will be displayed)

    Note: coordinate is given in (y, x); this function returns in (x, y).

    Preconditions:
        - 0 <= coordinate[0] <= 9
        - 0 <= coordinate[1] <= 8
    """
    return 56 + coordinate[1] * 56, 66 + coordinate[0] * 56


def pixel_to_coordinate(pixel: tuple[int, int]) -> tuple[int, int]:
    """Convert the coordinate of the pixel (as displayed on the screen) to the coordinate of the
    board (as in the list of list coordinate).

    Note: pixel is given in (x, y); this function returns in (y, x).
    """
    x, y = pixel
    x -= 32
    y -= 41
    return y // 56, x // 56


if __name__ == '__main__':
    g = Game(RandomPlayer())
    g.run()
