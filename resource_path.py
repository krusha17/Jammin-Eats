import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Use the folder where this file is located
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)
