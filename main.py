"""CSC111 Final Project: AI Player in Chinese Chess

Module Description
===============================

This is module contains the code necessary for running the entire program.

Copyright and Usage Information
===============================

This file is Copyright (c) 2021 Junru Lin, Zixiu Meng, Krystal Miao and Jenci Wei
"""
from player import AIBlack
from visualization import Game

if __name__ == '__main__':
    # Data Processing Example
    # TODO: Add a data processing example (using middle_sample,csv)
    # Interaction Window
    ai_black_player = AIBlack('data/tree.xml', 3)
    game = Game(ai_black_player)
    game.run()
