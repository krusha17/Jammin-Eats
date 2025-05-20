#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats Debug Launcher

This is a special debug version of the main file for Jammin' Eats.
It will catch and report errors with more detailed information.
"""

import os
import sys
import traceback

# Make sure the src directory is in the path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Wrapper for better error reporting
def run_with_error_handling():
    try:
        # Import main function from our modular structure
        from src.main import main
        main()
    except Exception as e:
        # Print detailed error information
        print("\n===== DETAILED ERROR REPORT =====\n")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        
        # Check specifically for index errors
        if isinstance(e, IndexError):
            print("\nIndex Error Details:")
            # Get the traceback info
            tb = traceback.extract_tb(sys.exc_info()[2])
            for frame in tb:
                filename, line, function, code = frame
                print(f"File: {filename}")
                print(f"Line: {line}")
                print(f"Function: {function}")
                print(f"Code: {code}")
                
                # Try to find the specific list/array being accessed
                if code and '[' in code and ']' in code:
                    print("Possible array access: " + code)
        
        print("\n===== END ERROR REPORT =====\n")
        
        # Handle specific errors
        if "'NoneType' object is not subscriptable" in str(e):
            print("SOLUTION: It looks like you might be trying to index a None value.")
            print("Check if an expected list or dictionary is actually None.")
        
        return 1  # Error exit code

# Run the game
if __name__ == '__main__':
    sys.exit(run_with_error_handling())
