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
        self.opponent = player
        self.music = music
        self.sfx = sfx
        self._screen = pygame.display.set_mode((920, 645))
        self._game = ChessGame()
        self._curr_coord = ()
        self._ready_to_move = False
        self._movement_indices = []
        self._game_ended = False
        pygame.display.set_caption('Chinese Chess!')

        # Load images
        board_image = pygame.image.load('chessboard/board/004.jpg')
        coord_image = pygame.image.load('chessboard/board/xy2.png')
        black_assistant = pygame.image.load('chessboard/piece/ba.png')
        black_elephant = pygame.image.load('chessboard/piece/bb.png')
        black_cannon = pygame.image.load('chessboard/piece/bc.png')
        black_king = pygame.image.load('chessboard/piece/bk.png')
        black_horse = pygame.image.load('chessboard/piece/bn.png')
        black_pawn = pygame.image.load('chessboard/piece/bp.png')
        black_chariot = pygame.image.load('chessboard/piece/br.png')
        red_assistant = pygame.image.load('chessboard/piece/ra.png')
        red_elephant = pygame.image.load('chessboard/piece/rb.png')
        red_cannon = pygame.image.load('chessboard/piece/rc.png')
        red_king = pygame.image.load('chessboard/piece/rk.png')
        red_horse = pygame.image.load('chessboard/piece/rn.png')
        red_pawn = pygame.image.load('chessboard/piece/rp.png')
        red_chariot = pygame.image.load('chessboard/piece/rr.png')
        possible_move_frame = pygame.image.load('chessboard/piece/mask.png')
        selected_frame = pygame.image.load('chessboard/piece/mm.png')

        # Change icon
        icon = pygame.Surface(black_elephant.get_size())
        icon.blit(black_elephant, (0, 0))
        pygame.display.set_icon(icon)

        # Load sound and music
        check_sound = pygame.mixer.Sound('chessboard/sound/check.wav')
        move_sound = pygame.mixer.Sound('chessboard/sound/move.wav')
        capture_sound = pygame.mixer.Sound('chessboard/sound/capture.wav')

        # Load font
        font_bold = pygame.font.SysFont('American Typewriter', 36, bold=True)
        font = pygame.font.SysFont('American Typewriter', 24)
        text = pygame.font.SysFont('Arial', 24)

        # Define RGB colours & display background
        black = (0, 0, 0)
        red = (255, 0, 0)
        blue = (0, 0, 255)
        white = (255, 255, 255)
        background_color = (181, 184, 191)

        global IMAGE_DICT
        IMAGE_DICT = {('r', False): black_chariot, ('h', False): black_horse,
                      ('e', False): black_elephant, ('a', False): black_assistant,
                      ('k', False): black_king, ('c', False): black_cannon,
                      ('p', False): black_pawn, ('r', True): red_chariot, ('h', True): red_horse,
                      ('e', True): red_elephant, ('a', True): red_assistant, ('k', True): red_king,
                      ('c', True): red_cannon, ('p', True): red_pawn, 'board_image': board_image,
                      'coord_image': coord_image, 'possible_move_frame': possible_move_frame,
                      'selected_frame': selected_frame, 'check_sound': check_sound,
                      'move_sound': move_sound, 'capture_sound': capture_sound,
                      'font_bold': font_bold, 'font': font, 'text': text, 'black': black,
                      'red': red, 'blue': blue, 'white': white}

        # Display background
        self._screen.fill(background_color)
        self.display_instructions()

    def display_instructions(self) -> None:
        """Display the instructions and the status bar on the right side of the board."""
        # Instructions display
        instruction_1 = IMAGE_DICT['text'].render('Instructions', True, IMAGE_DICT['black'])
        instruction_1_rect = instruction_1.get_rect(topleft=(600, 50))
        self._screen.blit(instruction_1, instruction_1_rect)
        instruction_2 = IMAGE_DICT['text'].render('During your turn, click', True,
                                                  IMAGE_DICT['black'])
        instruction_2_rect = instruction_2.get_rect(topleft=(600, 100))
        self._screen.blit(instruction_2, instruction_2_rect)
        instruction_3 = IMAGE_DICT['text'].render('one of your pieces to get', True,
                                                  IMAGE_DICT['black'])
        instruction_3_rect = instruction_3.get_rect(topleft=(600, 140))
        self._screen.blit(instruction_3, instruction_3_rect)
        instruction_4 = IMAGE_DICT['text'].render('all of its valid moves.', True,
                                                  IMAGE_DICT['black'])
        instruction_4_rect = instruction_4.get_rect(topleft=(600, 180))
        self._screen.blit(instruction_4, instruction_4_rect)
        instruction_5 = IMAGE_DICT['text'].render('Then click on the desired', True,
                                                  IMAGE_DICT['black'])
        instruction_5_rect = instruction_5.get_rect(topleft=(600, 220))
        self._screen.blit(instruction_5, instruction_5_rect)
        instruction_6 = IMAGE_DICT['text'].render('location to make move or', True,
                                                  IMAGE_DICT['black'])
        instruction_6_rect = instruction_6.get_rect(topleft=(600, 260))
        self._screen.blit(instruction_6, instruction_6_rect)
        instruction_7 = IMAGE_DICT['text'].render('click anywhere else to', True,
                                                  IMAGE_DICT['black'])
        instruction_7_rect = instruction_7.get_rect(topleft=(600, 300))
        self._screen.blit(instruction_7, instruction_7_rect)
        instruction_8 = IMAGE_DICT['text'].render('deselect the piece.', True, IMAGE_DICT['black'])
        instruction_8_rect = instruction_8.get_rect(topleft=(600, 340))
        self._screen.blit(instruction_8, instruction_8_rect)

        # Current status display
        your_move = IMAGE_DICT['font'].render('Your move', True, IMAGE_DICT['red'])
        your_move_rect = your_move.get_rect(topleft=(650, 450))
        self._screen.blit(your_move, your_move_rect)

        opponent_move = IMAGE_DICT['font'].render("Opponent's move", True, IMAGE_DICT['red'])
        opponent_move_rect = opponent_move.get_rect(topleft=(650, 500))
        self._screen.blit(opponent_move, opponent_move_rect)

    def run(self) -> None:
        """Run the game."""
        # Initialize chess game
        self._print_game()
        status_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=(620, 465))
        self._screen.blit(IMAGE_DICT['possible_move_frame'], status_rect)

        pygame.display.flip()

        if self.music:
            # Load the background music
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
                        try:
                            wxf_move = _get_wxf_movement(self._game.get_board(),
                                                         self._curr_coord, new_coordinate, True)
                        except ValueError:  # A pygame error occurred! Reset to previous state.
                            self._print_game()
                            self._ready_to_move = False
                            pygame.display.flip()
                            continue

                        destination = _get_index_movement(self._game.get_board(), wxf_move, True)

                        pieces_before = piece_count(self._game.get_board())
                        self._game.make_move(wxf_move)
                        pieces_after = piece_count(self._game.get_board())
                        if self.sfx and pieces_before != pieces_after:
                            IMAGE_DICT['capture_sound'].play()
                        self._print_game()
                        if self.sfx:
                            IMAGE_DICT['move_sound'].play()

                        # Mark where the piece was before the move
                        piece_frame_coord = coordinate_to_pixel(self._curr_coord)
                        piece_frame_rect = IMAGE_DICT['selected_frame'].get_rect(
                            center=piece_frame_coord)
                        self._screen.blit(IMAGE_DICT['selected_frame'], piece_frame_rect)

                        # Mark where the piece is right now
                        piece_frame_coord_after = coordinate_to_pixel(destination)
                        piece_frame_after_rect = IMAGE_DICT['selected_frame'].get_rect(
                            center=piece_frame_coord_after)
                        self._screen.blit(IMAGE_DICT['selected_frame'], piece_frame_after_rect)

                        # Clear the light displaying current status
                        status_clear = pygame.Surface(IMAGE_DICT['possible_move_frame'].get_size())
                        status_clear.fill((181, 184, 191))
                        self._screen.blit(status_clear, status_rect)

                        # Show the new status light
                        status_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=(620, 515))
                        self._screen.blit(IMAGE_DICT['possible_move_frame'], status_rect)
                        pygame.display.flip()

                        if self._check_for_end():
                            continue

                        # Computer's turn
                        opponent_wxf_move = self.opponent.make_move(self._game, wxf_move)
                        opponent_piece_coord = _wxf_to_index(self._game.get_board(),
                                                             opponent_wxf_move[0:2], False)

                        opponent_destination = _get_index_movement(self._game.get_board(),
                                                                   opponent_wxf_move, False)

                        self._game.make_move(opponent_wxf_move)
                        if self.sfx:
                            IMAGE_DICT['move_sound'].play()
                        pieces_after_opponent = piece_count(self._game.get_board())
                        if self.sfx and pieces_after != pieces_after_opponent:
                            IMAGE_DICT['capture_sound'].play()
                        self._print_game()

                        # Mark where the piece was before the move
                        opponent_piece_frame_coord = coordinate_to_pixel(opponent_piece_coord)
                        opponent_piece_frame_rect = \
                            IMAGE_DICT['selected_frame'].get_rect(center=opponent_piece_frame_coord)
                        self._screen.blit(IMAGE_DICT['selected_frame'], opponent_piece_frame_rect)

                        # Mark where the piece is right now
                        opponent_piece_frame_coord_after = coordinate_to_pixel(opponent_destination)
                        opponent_piece_frame_after_rect = IMAGE_DICT['selected_frame'].get_rect(
                            center=opponent_piece_frame_coord_after)
                        self._screen.blit(IMAGE_DICT['selected_frame'],
                                          opponent_piece_frame_after_rect)

                        # Clear the light displaying current status
                        status_clear = pygame.Surface(IMAGE_DICT['possible_move_frame'].get_size())
                        status_clear.fill((181, 184, 191))
                        self._screen.blit(status_clear, status_rect)

                        # Show the new status light
                        status_rect = IMAGE_DICT['possible_move_frame'].get_rect(center=(620, 465))
                        self._screen.blit(IMAGE_DICT['possible_move_frame'], status_rect)
                        pygame.display.flip()

                        if self._check_for_end():
                            continue

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
            IMAGE_DICT['check_sound'].play()

        self._ready_to_move = True

    def _check_for_end(self) -> bool:
        """Check (and return) whether the game ended. If so, stop the game and print who won."""
        if self._game.get_winner() is not None:
            if self._game.get_winner() == 'Red':
                self._game_ended = True
                # Display winning message
                message = IMAGE_DICT['font_bold'].render('Congratulations! You won!', True,
                                                         IMAGE_DICT['red'])
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(IMAGE_DICT['white'])
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = IMAGE_DICT['font'].render('Please close this window.', True,
                                                            IMAGE_DICT['red'])
            elif self._game.get_winner() == 'Black':
                self._game_ended = True
                # Display losing message
                message = IMAGE_DICT['font_bold'].render('Too bad. You lost.', True,
                                                         IMAGE_DICT['black'])
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(IMAGE_DICT['white'])
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = IMAGE_DICT['font'].render('Please close this window.', True,
                                                            IMAGE_DICT['black'])
            else:  # self._game.get_winner() == 'Draw'
                self._game_ended = True
                # Display draw message
                message = IMAGE_DICT['font_bold'].render('No one won.', True, IMAGE_DICT['blue'])
                message_rect = message.get_rect(center=(280, 300))
                message_surface = pygame.Surface(message.get_size())
                message_surface.fill(IMAGE_DICT['white'])
                message_surface.set_alpha(200)
                self._screen.blit(message_surface, message_rect)
                self._screen.blit(message, message_rect)
                # Sets colour for closing message
                closing_message = IMAGE_DICT['font'].render('Please close this window.', True,
                                                            IMAGE_DICT['blue'])

            # Instructs the player to close the window
            closing_message_rect = closing_message.get_rect(center=(280, 350))
            closing_message_surface = pygame.Surface(closing_message.get_size())
            closing_message_surface.fill(IMAGE_DICT['white'])
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
    from player import ExploringPlayer, AIBlack
    g = Game(ExploringPlayer(3))
    g.run()
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()
    #
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 100,
    #     'disable': ['E1101', 'E1136', 'E9997', 'E9998', 'R1702', 'R0915'],
    #     'extra-imports': ['chess_game', 'player', 'pygame']
    # })
