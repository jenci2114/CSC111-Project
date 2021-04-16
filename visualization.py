"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This Python module contains Game class, which is
responsible for displaying the Chinese Chess interface
via Pygame and enabling humans to play against the
AI Players we created.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei
"""

import pygame
from chess_game import ChessGame, _index_to_wxf, _wxf_to_index, \
    _get_index_movement, _get_wxf_movement, piece_count
from player import Player


class Game:
    """A simulation of Chinese Chess Game.

    Instance Attributes:
        - opponent: the computer player that plays as black.
        - music: whether to play background music.
        - sfx: whether to play sound effects.
    """
    # Private Instance Attributes:
    #   - _screen: The pygame screen to draw on.
    #   - _game: The chess game.
    #   - _curr_coord: The currently selected piece's coordinate.
    #   - _ready_to_move: Whether the human can move in one click.
    #   - _movement_indices: List of moves the human can make (in terms of coordinate indices).
    #   - _game_ended: Whether the game ended.
    opponent: Player
    music: bool
    sfx: bool
    _screen: pygame.Surface
    _game: ChessGame
    _curr_coord: tuple
    _ready_to_move: bool
    _movement_indices: list
    _game_ended: bool

    def __init__(self, player: Player, music: bool = False, sfx: bool = False) -> None:
        """Initialize the game."""
        pygame.init()

        # Initialize the attributes
        self.opponent = player
        self.music = music
        self.sfx = sfx
        self._screen = pygame.display.set_mode((920, 645))
        self._game = ChessGame()
        self._curr_coord = ()
        self._ready_to_move = False
        self._movement_indices = []
        self._game_ended = False

        # set caption and change the icon
        pygame.display.set_caption('Chinese Chess!')
        self._change_icon()

        # Initialize some global variables used for storing images, sounds, colors, and fonts
        global IMAGE_DICT
        global SOUND_DICT
        global COLOR_DICT
        global FONT_DICT
        IMAGE_DICT = self._load_images()
        SOUND_DICT = self._load_sound()
        COLOR_DICT = self._define_color()
        FONT_DICT = self._define_font()

        # Display background
        self._screen.fill(COLOR_DICT['background_color'])
        self.display_instructions()

    def _load_images(self) -> dict:
        """Load the images for the game, and return a dictionary of them.

        The keys of the dictionary are tuples, with the first element being
        the name of the piece and the second element being the sides.
        The values of the dictionary are the corresponding images.

        Note: this method is called only when initializing the class, as a helper function.
        """
        # Load images
        board_image = pygame.image.load('chessboard/board/004.jpg')
        coord_image = pygame.image.load('chessboard/board/xy2.png')
        black_advisor = pygame.image.load('chessboard/piece/ba.png')
        black_elephant = pygame.image.load('chessboard/piece/bb.png')
        black_cannon = pygame.image.load('chessboard/piece/bc.png')
        black_king = pygame.image.load('chessboard/piece/bk.png')
        black_horse = pygame.image.load('chessboard/piece/bn.png')
        black_pawn = pygame.image.load('chessboard/piece/bp.png')
        black_chariot = pygame.image.load('chessboard/piece/br.png')
        red_advisor = pygame.image.load('chessboard/piece/ra.png')
        red_elephant = pygame.image.load('chessboard/piece/rb.png')
        red_cannon = pygame.image.load('chessboard/piece/rc.png')
        red_king = pygame.image.load('chessboard/piece/rk.png')
        red_horse = pygame.image.load('chessboard/piece/rn.png')
        red_pawn = pygame.image.load('chessboard/piece/rp.png')
        red_chariot = pygame.image.load('chessboard/piece/rr.png')
        possible_move_frame = pygame.image.load('chessboard/piece/mask.png')
        selected_frame = pygame.image.load('chessboard/piece/mm.png')

        # return a dictionary with key being tuples and values being the corresponding image
        return {('r', False): black_chariot, ('h', False): black_horse,
                ('e', False): black_elephant, ('a', False): black_advisor,
                ('k', False): black_king, ('c', False): black_cannon,
                ('p', False): black_pawn, ('r', True): red_chariot,
                ('h', True): red_horse, ('e', True): red_elephant,
                ('a', True): red_advisor, ('k', True): red_king,
                ('c', True): red_cannon, ('p', True): red_pawn,
                'board_image': board_image, 'coord_image': coord_image,
                'possible_move_frame': possible_move_frame, 'selected_frame': selected_frame}

    def _load_sound(self) -> dict:
        """Load sound, and return a dictionary storing them.

        check_sound: the sound for clicking a red piece when it's red's turn
        move_sound: the sound for moving a piece, used for both sides
        capture_sound: the sound for capturing a piece, used for both sides

        Note: this method is called only when initializing the class, as a helper function.
        """
        # Load sound
        check_sound = pygame.mixer.Sound('chessboard/sound/check.wav')
        move_sound = pygame.mixer.Sound('chessboard/sound/move.wav')
        capture_sound = pygame.mixer.Sound('chessboard/sound/capture.wav')

        return {'check_sound': check_sound,
                'move_sound': move_sound,
                'capture_sound': capture_sound}

    def _define_color(self) -> dict:
        """Define colors that will be used in the game, and return a dictionary storing them.

        Note: this method is called only when initializing the class, as a helper function.
        """
        # Define RGB colours & display background
        black = (0, 0, 0)
        red = (255, 0, 0)
        blue = (0, 0, 255)
        white = (255, 255, 255)
        background_color = (181, 184, 191)

        return {'black': black,
                'red': red,
                'blue': blue,
                'white': white,
                'background_color': background_color}

    def _define_font(self) -> dict:
        """Define the font for the game interaction surface, and return a dictionary storing them.

        Note: this method is called only when initializing the class, as a helper function.
        """
        # Load font
        font_bold = pygame.font.SysFont('American Typewriter', 36, bold=True)
        font = pygame.font.SysFont('American Typewriter', 24)
        text = pygame.font.SysFont('Arial', 24)

        return {'font_bold': font_bold, 'font': font, 'text': text}

    def _change_icon(self) -> None:
        """Change the icon to the black elephant and set the font.

        Note: this method is used when initializing the class.
        """
        # Set the icon as the black elephant
        # Load the black elephant image
        black_elephant = pygame.image.load('chessboard/piece/bb.png')
        # Change icon
        icon = pygame.Surface(black_elephant.get_size())
        icon.blit(black_elephant, (0, 0))
        pygame.display.set_icon(icon)

    def display_instructions(self) -> None:
        """Display the instructions and the status bar on the right side of the board,
        as the followings:

        Instructions
        You are the red side.
        During your turn, click
        one of your pieces to get
        all of its valid moves.
        Then click on the desired
        location to make move or
        click anywhere else to
        deselect the piece.

            Your move
            Opponent's move
        """
        # Instructions display
        self._instruction('Instructions', (600, 50))
        self._instruction('You are the red side', (600, 86))
        self._instruction('During your turn, click', (600, 122))
        self._instruction('one of your pieces to get', (600, 158))
        self._instruction('all of its valid moves.', (600, 194))
        self._instruction('Then click on the desired', (600, 230))
        self._instruction('location to make move or', (600, 266))
        self._instruction('click anywhere else to', (600, 302))
        self._instruction('deselect the piece.', (600, 338))

        # Current status display
        self._status('Your move', (650, 450))
        self._status("Opponent's move", (650, 500))

    def _instruction(self, text: str, position: tuple) -> None:
        """Display the instruction text on the position.
        The color is 'black' and the font is 'text', which are defined in the FONT_DICT.

        Note: This is a helper function for self.display_instructions
        """
        output_text = FONT_DICT['text'].render(text, True, COLOR_DICT['black'])
        rect = output_text.get_rect(topleft=position)
        self._screen.blit(output_text, rect)

    def _status(self, text: str, position: tuple) -> None:
        """Display the current status text on the position.
        The color is 'red' and the font is 'font', which are defined in the FONT_DICT.

        Note: This is a helper function for self.display_instructions
        """
        output_text = FONT_DICT['font'].render(text, True, COLOR_DICT['red'])
        rect = output_text.get_rect(topleft=position)
        self._screen.blit(output_text, rect)

    def run(self) -> None:
        """Run the game."""
        # Initialize chess game
        self._print_game()
        red_status_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=(620, 465))
        self._screen.blit(IMAGE_DICT['possible_move_frame'], red_status_rect)
        pygame.display.flip()

        black_status_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=(620, 515))

        if self.music:  # Load the background music
            pygame.mixer.music.load('chessboard/sound/background_music.mp3')
            pygame.mixer.music.play(-1)

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
                    # print possible moves
                    self._get_possible_moves_for_piece(event.pos)
                    pygame.display.flip()
                elif event.type == pygame.MOUSEBUTTONDOWN \
                        and self._ready_to_move and not self._game_ended:
                    # make a move or unselect a piece
                    new_coordinate = pixel_to_coordinate((event.pos[0], event.pos[1]))
                    if new_coordinate not in self._movement_indices:  # Unselect this piece
                        self._print_game()
                        self._ready_to_move = False
                        pygame.display.flip()
                    else:  # Make the move!
                        try:
                            # get the wxf of the chosen move
                            wxf_move = _get_wxf_movement(self._game.get_board(),
                                                         self._curr_coord, new_coordinate, True)
                        except ValueError:  # A pygame error occurred! Reset to previous state.
                            self._print_game()
                            self._ready_to_move = False
                            pygame.display.flip()
                            continue
                        # change the status on the board
                        self._make_a_move(wxf_move, red_status_rect, black_status_rect, True)
                        if self._check_for_end():  # check whether the game is ended
                            continue

                        # Computer's turn
                        # choose a move
                        opponent_wxf_move = self.opponent.make_move(self._game, wxf_move)
                        self._curr_coord = _wxf_to_index(self._game.get_board(), opponent_wxf_move,
                                                         False)
                        # change the status on the board
                        self._make_a_move(opponent_wxf_move, black_status_rect, red_status_rect,
                                          False)
                        if self._check_for_end():  # check whether the game is ended
                            continue

    def _make_a_move(self, wxf_move: str, old_status_rect: tuple, new_status_rect: tuple,
                     is_red: bool) -> None:
        """Make a move on the pygame board based on wxf_move.

        NOte: This is a helper function for self.run.
        """
        # change wxf move to index move
        destination = _get_index_movement(self._game.get_board(), wxf_move, is_red)
        pieces_before = piece_count(self._game.get_board())  # the number of pieces before move
        self._game.make_move(wxf_move)
        pieces_after = piece_count(self._game.get_board())  # the number of pieces after move
        if self.sfx:  # Add sound
            if pieces_before != pieces_after:  # there is a capture
                SOUND_DICT['capture_sound'].play()
            else:  # there is no capture
                SOUND_DICT['move_sound'].play()
        # update the status of board on the pygame window
        self._print_game()

        # Mark where the piece was before the move
        piece_frame_coord = coordinate_to_pixel(self._curr_coord)
        piece_frame_rect = IMAGE_DICT['selected_frame'].get_rect(
            center=piece_frame_coord)
        self._screen.blit(IMAGE_DICT['selected_frame'], piece_frame_rect)

        # Mark where the piece is after move
        piece_frame_coord_after = coordinate_to_pixel(destination)
        piece_frame_after_rect = IMAGE_DICT['selected_frame'].get_rect(
            center=piece_frame_coord_after)
        self._screen.blit(IMAGE_DICT['selected_frame'], piece_frame_after_rect)

        # Clear the light displaying current status
        status_clear = pygame.Surface(IMAGE_DICT['possible_move_frame'].get_size())
        status_clear.fill((181, 184, 191))
        self._screen.blit(status_clear, old_status_rect)

        # Show the new status light
        self._screen.blit(IMAGE_DICT['possible_move_frame'], new_status_rect)
        pygame.display.flip()

    def _print_game(self) -> None:
        """Print the current state of the game."""
        self._screen.blit(IMAGE_DICT['board_image'], (0, 0))  # Display board
        self._screen.blit(IMAGE_DICT['coord_image'], (0, 0))  # Display coordinates
        for pos in [(y, x) for y in range(0, 10) for x in range(0, 9)]:  # Display pieces
            piece = self._game.get_board()[pos[0]][pos[1]]
            if piece is not None:
                piece_coord = coordinate_to_pixel((pos[0], pos[1]))
                piece_rect = IMAGE_DICT[(piece.kind, piece.is_red)].get_rect(center=piece_coord)
                self._screen.blit(IMAGE_DICT[(piece.kind, piece.is_red)], piece_rect)

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
        piece_frame_rect = IMAGE_DICT['selected_frame'].get_rect(center=piece_frame_coord)
        self._screen.blit(IMAGE_DICT['selected_frame'], piece_frame_rect)

        # Also frame where the selected piece can go
        piece_possible_moves = [move for move in possible_moves
                                if move[0:2] == piece_wxf]
        self._movement_indices = [_get_index_movement(self._game.get_board(), move, True)
                                  for move in piece_possible_moves]
        for coord in self._movement_indices:
            frame_coord = coordinate_to_pixel(coord)
            frame_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=frame_coord)
            self._screen.blit(IMAGE_DICT['possible_move_frame'], frame_rect)

        if self.sfx:
            SOUND_DICT['check_sound'].play()

        self._ready_to_move = True

    def _check_for_end(self) -> bool:
        """Check (and return) whether the game ended. If so, stop the game and print who won."""
        if self._game.get_winner() is not None:
            self._game_ended = True
            self._print_result(self._game.get_winner())
        else:
            pass

        return self._game_ended

    def _print_result(self, winner: str) -> None:
        """Print the result of the game.

        Note: This is a helper function for self._check_for_end.

        Precondition:
            - winner in {'Red', 'Black', 'Draw'}
        """
        text_dict = {'Red': 'Congratulations! You won!',
                     'Black': 'Too bad. You lost.',
                     'Draw': 'No one won.'}
        color_dict = {'Red': 'red', 'Black': 'black', 'Draw': 'blue'}
        # decide the text and color based on the winner
        text = text_dict[winner]
        color = color_dict[winner]
        # print the result of the game
        message = FONT_DICT['font_bold'].render(text, True, color)  # Text
        message_rect = message.get_rect(center=(280, 300))
        message_surface = pygame.Surface(message.get_size())  # Background for text
        message_surface.fill(COLOR_DICT['white'])
        message_surface.set_alpha(200)  # Make background translucent
        self._screen.blit(message_surface, message_rect)
        self._screen.blit(message, message_rect)
        # print the closing message
        closing_message = FONT_DICT['font'].render('Please close this window.', True, color)  # Text
        closing_message_rect = closing_message.get_rect(center=(280, 350))
        closing_message_surface = pygame.Surface(closing_message.get_size())  # Background for text
        closing_message_surface.fill(COLOR_DICT['white'])
        closing_message_surface.set_alpha(200)  # Make background translucent
        self._screen.blit(closing_message_surface, closing_message_rect)
        self._screen.blit(closing_message, closing_message_rect)

        pygame.display.flip()  # Update display


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


# if __name__ == '__main__':
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    #
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1101', 'E1136', 'E9997', 'E9998', 'R0902', 'R0201', 'R0914', 'R1702'],
    #     'extra-imports': ['chess_game', 'player', 'pygame']
    # })
