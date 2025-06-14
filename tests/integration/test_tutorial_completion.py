"""
Script to specifically test tutorial completion logic
"""

import os
import sys
import pygame

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_tutorial_completion():
    """Test tutorial completion logic without complex state transitions"""
    print("=== TUTORIAL COMPLETION TEST ===")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tutorial Test")
    clock = pygame.time.Clock()

    # Create a very basic state to track money and deliveries
    class SimpleTutorialTest:
        def __init__(self):
            self.money = 0
            self.successful_deliveries = 0
            self.target_money = 50
            self.target_deliveries = 5
            self.tutorial_completed = False
            self.font = pygame.font.SysFont(None, 36)

        def check_completion(self):
            """Check tutorial completion criteria"""
            if (
                self.money >= self.target_money
                or self.successful_deliveries >= self.target_deliveries
            ):
                self.tutorial_completed = True
                return True
            return False

        def add_money(self, amount=10):
            """Add money and check for completion"""
            self.money += amount
            print(f"Money: ${self.money}")
            return self.check_completion()

        def add_delivery(self, count=1):
            """Add delivery and check for completion"""
            self.successful_deliveries += count
            print(f"Deliveries: {self.successful_deliveries}")
            return self.check_completion()

        def draw(self, screen):
            """Draw the current game state"""
            screen.fill((0, 0, 0))  # Black background

            # Draw money and deliveries
            money_text = self.font.render(
                f"Money: ${self.money}", True, (255, 255, 255)
            )
            deliveries_text = self.font.render(
                f"Deliveries: {self.successful_deliveries}", True, (255, 255, 255)
            )

            # Draw goals
            money_goal = self.font.render(
                f"Goal: ${self.target_money}", True, (200, 200, 200)
            )
            deliveries_goal = self.font.render(
                f"Goal: {self.target_deliveries} deliveries", True, (200, 200, 200)
            )

            # Draw tutorial status
            status = "COMPLETED!" if self.tutorial_completed else "In Progress"
            status_color = (0, 255, 0) if self.tutorial_completed else (255, 255, 0)
            status_text = self.font.render(
                f"Tutorial Status: {status}", True, status_color
            )

            # Draw instructions
            instr1 = self.font.render("Press M: Add $10", True, (200, 200, 200))
            instr2 = self.font.render("Press D: Add 1 Delivery", True, (200, 200, 200))
            instr3 = self.font.render(
                "Press SPACE: Mark Complete in DB", True, (200, 200, 200)
            )
            instr4 = self.font.render("Press ESC: Quit", True, (200, 200, 200))

            # Position and draw all text
            screen.blit(status_text, (20, 20))
            screen.blit(money_text, (20, 80))
            screen.blit(money_goal, (20, 120))
            screen.blit(deliveries_text, (20, 180))
            screen.blit(deliveries_goal, (20, 220))

            screen.blit(instr1, (20, 300))
            screen.blit(instr2, (20, 340))
            screen.blit(instr3, (20, 380))
            screen.blit(instr4, (20, 420))

            # Update display
            pygame.display.flip()

    # Test if we can mark tutorial complete in the database
    def mark_tutorial_complete_in_db():
        """Mark tutorial as complete in the database"""
        try:
            from src.persistence.dal import mark_tutorial_complete

            result = mark_tutorial_complete(1)  # Default player ID
            print(f"✓ Marked tutorial complete in database: {result}")
            return True
        except Exception as e:
            print(f"✗ Failed to mark tutorial complete: {e}")
            return False

    # Test if tutorial completion is properly detected
    def check_tutorial_status_in_db():
        """Check tutorial completion status in the database"""
        try:
            from src.persistence.dal import is_tutorial_complete

            status = is_tutorial_complete(1)  # Default player ID
            print(f"Database tutorial status: {status}")
            return status
        except Exception as e:
            print(f"Error checking tutorial status: {e}")
            return None

    # Create test instance
    test = SimpleTutorialTest()

    # Check initial status
    print("\nChecking initial tutorial status in database...")
    check_tutorial_status_in_db()

    # Main loop
    running = True
    print("\nStarting tutorial test. Use keyboard to interact:")
    print("M: Add $10, D: Add delivery, SPACE: Save to DB, ESC: Quit")

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_m:
                    # Add money
                    completed = test.add_money()
                    if completed and not test.tutorial_completed:
                        print("✓ Tutorial goal reached through money!")

                elif event.key == pygame.K_d:
                    # Add delivery
                    completed = test.add_delivery()
                    if completed and not test.tutorial_completed:
                        print("✓ Tutorial goal reached through deliveries!")

                elif event.key == pygame.K_SPACE:
                    # Save to database
                    if test.tutorial_completed:
                        mark_tutorial_complete_in_db()
                        print("Checking database status after update...")
                        check_tutorial_status_in_db()

        # Draw screen
        test.draw(screen)

        # Cap at 30 FPS
        clock.tick(30)

    # Clean up
    pygame.quit()
    print("\nTutorial completion test finished.")


if __name__ == "__main__":
    test_tutorial_completion()
