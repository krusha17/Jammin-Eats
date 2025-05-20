#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats - A food truck game

This is the main entry point for the Jammin' Eats game. It imports and uses
the modular game components from the src directory.
"""

import os
import sys

# Make sure the src directory is in the path so we can import modules from it
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import main function from our modular structure
from src.main import main

# Set debug flag if needed (can be removed or set via command line in the future)
# import src.debug.debug_tools as debug
# debug.DEBUG_MODE = True

# Run the game
if __name__ == '__main__':
    main()
