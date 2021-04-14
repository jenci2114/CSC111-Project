"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This module is for coordinating all our other
modules and presenting our project.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao, Jenci Wei
"""
from player import AIBlack, ExploringPlayer
from visualization import Game


def present() -> None:
    """Present our project. Gives the user the options of fighting against AIs of different
    skill levels using Pygame, and allows the user to choose whether to mute/play background
    music and/or sound effects.
    """
    print('In our project, you will fight the AIs we made in Chinese Chess.')
    print('You will play as the \033[91mred player\33[0m. '
          'Good luck and hopefully you can beat our AI!')
    print('Please indicate which AI you would like to fight against:')
    print("Enter '1' for a beginner-level AI")
    print("'2' for a novice-level AI")
    print("'3' for an intermediate-level AI (Warning: each step takes 30-600 seconds)")
    print("'4' for a trained novice-level AI (Warning: takes 1 minute to load tree)")
    option = input()

    while option not in {'1', '2', '3', '4'}:
        print('Invalid input. Please try again.')
        option = input()

    print("Please indicate your music settings:")

    print("Enter 'y' (just the letter) if you want background music. "
          "Enter anything else otherwise.")
    bgm_option = input()
    if bgm_option == 'y':
        bgm = True
    else:
        bgm = False

    print("Enter 'y' (just the letter) if you want sound effects. "
          "Enter anything else otherwise.")
    sfx_option = input()
    if sfx_option == 'y':
        sfx = True
    else:
        sfx = False

    if option == '4':
        g = Game(AIBlack('tree.xml', 3), bgm, sfx)
    else:  # option in {'1', '2', '3'}
        g = Game(ExploringPlayer(int(option) + 1), bgm, sfx)

    g.run()


if __name__ == '__main__':
    present()
