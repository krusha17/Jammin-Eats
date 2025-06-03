#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats - Debug Launcher

This file provides detailed diagnostic information during startup.
"""

import os
import sys
import traceback

# Ensure src is in sys.path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
# Setup basic logging to console
def setup_basic_logging():
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("DebugLauncher")

# Main debug function
def debug_main():
    logger = setup_basic_logging()
    logger.info("===== STARTING DEBUG MODE =====")
    
    # Step 1: Initialize database
    logger.info("Step 1: Initializing database")
    try:
        from src.persistence.db_init import initialize_database, check_database_integrity
        db_result = initialize_database()
        logger.info(f"Database initialization result: {db_result}")
        
        integrity_result, missing = check_database_integrity()
        logger.info(f"Database integrity check: {integrity_result}, Missing: {missing}")
        
        if not integrity_result:
            logger.warning("Database integrity issues detected, attempting to reinitialize")
            db_result = initialize_database()
            logger.info(f"Database reinitialization result: {db_result}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        traceback.print_exc()
    
    # Step 2: Initialize pygame
    logger.info("Step 2: Initializing pygame")
    try:
        import pygame
        pygame.init()
        logger.info(f"Pygame initialization result: {pygame.get_init()}")
    except Exception as e:
        logger.error(f"Pygame initialization failed: {e}")
        traceback.print_exc()
    
    # Step 3: Load game modules
    logger.info("Step 3: Loading game modules")
    try:
        # Import critical modules with explicit error handling
        from src.core.game import Game
        from src.states.state import GameState
        from src.states.title_state import TitleState
        from src.states.tutorial_state import TutorialState
        from src.states.gameplay_state import GameplayState
        logger.info("All game modules loaded successfully")
    except Exception as e:
        logger.error(f"Module loading failed: {e}")
        traceback.print_exc()
    
    # Step 4: Initialize game instance
    logger.info("Step 4: Creating game instance")
    try:
        game = Game()
        logger.info("Game instance created successfully")
    except Exception as e:
        logger.error(f"Game instance creation failed: {e}")
        traceback.print_exc()
        return
    
    # Step 5: Start game loop
    logger.info("Step 5: Starting game loop")
    try:
        game.run()
        logger.info("Game exited normally")
    except Exception as e:
        logger.error(f"Game loop error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        debug_main()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
