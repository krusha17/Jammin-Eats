#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats - A food truck game

This is the main entry point for the Jammin' Eats game. It imports and uses
the modular game components from the src directory.
"""

import os
import sys

# Ensure src is in sys.path for both normal and PyInstaller builds
if getattr(sys, 'frozen', False):
    # If running as a bundled exe
    src_dir = os.path.join(sys._MEIPASS, 'src')
else:
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from core.game import Game

# Set debug flag if needed (can be removed or set via command line in the future)
# import src.debug.debug_tools as debug
# debug.DEBUG_MODE = True

def main():
    game = Game()
    game.run()

# Run the game
if __name__ == '__main__':
    main()
