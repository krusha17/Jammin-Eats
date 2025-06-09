import pygame
import sys
from src.ui.button import Button
from src.core.constants import WIDTH, HEIGHT, WHITE, GREEN, RED, MENU, PLAYING

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Button Test")

# Create buttons
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start", GREEN, (100, 255, 100))
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))

# Game state
game_state = MENU

# Main game loop
running = True
clock = pygame.time.Clock()

print("Button test started. Click the Start button to test state transition.")

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.is_clicked(event):
                    print("[DEBUG] Start button clicked")
                    print(f"[DEBUG] Changing game state from {game_state} to PLAYING ({PLAYING})")
                    game_state = PLAYING
                    print(f"[DEBUG] Game state is now: {game_state}")
                if exit_button.is_clicked(event):
                    print("[DEBUG] Exit button clicked")
                    running = False
    
    # Clear the screen
    screen.fill((0, 0, 0))
    
    if game_state == MENU:
        # Draw menu elements
        font = pygame.font.Font(None, 74)
        title = font.render("BUTTON TEST", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        
        # Update and draw buttons
        start_button.update(mouse_pos)
        exit_button.update(mouse_pos)
        start_button.draw(screen)
        exit_button.draw(screen)
    
    elif game_state == PLAYING:
        # Draw playing state
        font = pygame.font.Font(None, 48)
        msg = font.render("PLAYING STATE - Press ESC to return to menu", True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        
        # Allow return to menu with ESC key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            game_state = MENU
    
    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
