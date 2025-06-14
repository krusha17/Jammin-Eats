import pygame
import time
import sys
import traceback

# Global debug state
DEBUG_MODE = False

# Global error tracking log
ERROR_LOG = []


def toggle_debug_mode(current_state, sounds=None):
    """Toggle debug mode and play a sound if available"""
    new_state = not current_state

    # Print message to console
    if new_state:
        print("Debug mode enabled")
        # Play sound if available
        if sounds and "button_sound" in sounds and sounds["button_sound"]:
            sounds["button_sound"].play()
    else:
        print("Debug mode disabled")

    return new_state


def log_performance(label, start_time=None):
    """Log performance metrics with timing information"""
    if start_time is None:
        # If no start time provided, just return the current time
        return time.time()
    else:
        # Calculate elapsed time and log it
        elapsed = time.time() - start_time
        print(f"[PERFORMANCE] {label}: {elapsed:.4f} seconds")
        return time.time()  # Return new time for chaining measurements


def track_exceptions(func):
    """Decorator to track exceptions in functions"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get detailed error information
            error_type = type(e).__name__
            error_msg = str(e)
            tb = traceback.format_exc()

            # Log error details
            error_info = {
                "type": error_type,
                "message": error_msg,
                "traceback": tb,
                "time": time.time(),
                "function": func.__name__,
            }

            # Add to global error log
            ERROR_LOG.append(error_info)

            # Print to console
            print(f"\n===== ERROR IN {func.__name__} =====")
            print(f"Type: {error_type}")
            print(f"Message: {error_msg}")
            print("\nTraceback:")
            print(tb)
            print("===============================\n")

            # Re-raise the exception
            raise

    return wrapper


def install_exception_handler():
    """Install a global exception handler to catch unhandled exceptions"""
    original_hook = sys.excepthook

    def exception_handler(exc_type, exc_value, exc_traceback):
        # Log the exception
        error_info = {
            "type": exc_type.__name__,
            "message": str(exc_value),
            "traceback": "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            ),
            "time": time.time(),
            "function": "global",
        }

        ERROR_LOG.append(error_info)

        # Print a more helpful message
        print("\n===== UNHANDLED EXCEPTION =====")
        print(f"Type: {exc_type.__name__}")
        print(f"Message: {str(exc_value)}")

        # Check for common errors
        if exc_type is IndexError:
            print(
                "\nINDEX ERROR DETECTED: You might be trying to access an item in a list that doesn't exist."
            )
            print("Check array bounds and make sure lists are properly initialized.")
        elif exc_type is AttributeError and "NoneType" in str(exc_value):
            print("\nNONE ERROR DETECTED: You're trying to use an object that is None.")
            print("Check if an object was properly initialized or loaded.")

        # Call the original exception handler
        original_hook(exc_type, exc_value, exc_traceback)

    # Set our custom exception handler
    sys.excepthook = exception_handler

    return "Exception handler installed"


class DebugDisplay:
    """Class to handle rendering debug information on screen"""

    def __init__(self, font_size=16):
        self.font = pygame.font.Font(None, font_size)
        self.logs = []  # List of log entries to display
        self.max_logs = 10  # Maximum number of log entries to show
        self.display_time = 5.0  # How long each log stays on screen
        self.position = (10, 120)  # Starting position for logs
        self.line_height = font_size + 2
        self.background_color = (0, 0, 0, 128)  # Semi-transparent black

    def add_log(self, message):
        """Add a log message to the debug display"""
        # Add new log with timestamp
        self.logs.append(
            {
                "message": message,
                "time": time.time(),
                "color": (255, 255, 255),  # Default white text
            }
        )

        # Keep only the most recent logs
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def add_warning(self, message):
        """Add a warning message to the debug display"""
        self.logs.append(
            {
                "message": f"WARNING: {message}",
                "time": time.time(),
                "color": (255, 255, 0),  # Yellow for warnings
            }
        )

        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def add_error(self, message):
        """Add an error message to the debug display"""
        self.logs.append(
            {
                "message": f"ERROR: {message}",
                "time": time.time(),
                "color": (255, 0, 0),  # Red for errors
            }
        )

        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def update(self):
        """Update the log display, removing old logs"""
        current_time = time.time()
        self.logs = [
            log for log in self.logs if current_time - log["time"] < self.display_time
        ]

    def draw(self, surface):
        """Draw all active log messages on the screen"""
        self.update()  # Remove expired logs

        if not self.logs:
            return  # Nothing to draw

        # Calculate background size based on number of logs
        bg_width = 400  # Fixed width for simplicity
        bg_height = len(self.logs) * self.line_height

        # Create a semi-transparent surface for the background
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill(self.background_color)
        surface.blit(bg_surface, self.position)

        # Draw each log message
        for i, log in enumerate(self.logs):
            log_surf = self.font.render(log["message"], True, log["color"])
            x = self.position[0] + 5  # Small indent
            y = self.position[1] + i * self.line_height
            surface.blit(log_surf, (x, y))
