import os
import time
import traceback

# Global log file
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "debug_log.txt")

def init_logger():
    """Initialize the logger by creating the log file"""
    with open(LOG_FILE, 'w') as f:
        f.write(f"==== Jammin' Eats Debug Log - Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ====\n\n")

def log(message, category="INFO"):
    """Log a message to the debug log file"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {category}: {message}\n")

def log_error(message, exception=None):
    """Log an error message with optional exception details"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] ERROR: {message}\n")
        if exception:
            f.write(f"Exception: {str(exception)}\n")
            f.write(traceback.format_exc())
            f.write("\n")

def log_asset_load(asset_type, asset_name, path, success):
    """Log asset loading attempt"""
    status = "SUCCESS" if success else "FAILED"
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] ASSET LOAD {status}: {asset_type}/{asset_name} at {path}\n")
