import pygame
import time

def toggle_debug_mode(current_state, sounds=None):
    """Toggle debug mode and play a sound if available"""
    new_state = not current_state
    
    # Print message to console
    if new_state:
        print("Debug mode enabled")
        # Play sound if available
        if sounds and 'button_sound' in sounds and sounds['button_sound']:
            sounds['button_sound'].play()
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
        self.logs.append({
            'message': message,
            'time': time.time(),
            'color': (255, 255, 255)  # Default white text
        })
        
        # Keep only the most recent logs
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
    
    def add_warning(self, message):
        """Add a warning message to the debug display"""
        self.logs.append({
            'message': f"WARNING: {message}",
            'time': time.time(),
            'color': (255, 255, 0)  # Yellow for warnings
        })
        
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
    
    def add_error(self, message):
        """Add an error message to the debug display"""
        self.logs.append({
            'message': f"ERROR: {message}",
            'time': time.time(),
            'color': (255, 0, 0)  # Red for errors
        })
        
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
    
    def update(self):
        """Update the log display, removing old logs"""
        current_time = time.time()
        self.logs = [log for log in self.logs if current_time - log['time'] < self.display_time]
    
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
            log_surf = self.font.render(log['message'], True, log['color'])
            x = self.position[0] + 5  # Small indent
            y = self.position[1] + i * self.line_height
            surface.blit(log_surf, (x, y))
