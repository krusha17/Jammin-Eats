import pygame
from src.core.constants import WIDTH, HEIGHT, FPS, MENU, PLAYING, CUSTOMER_SPAWN_RATE
from src.persistence.dal import is_tutorial_complete
from src.persistence.game_persistence import GamePersistence
from src.states import TitleState, TutorialState

class Game:
    def __init__(self, screen_width=WIDTH, screen_height=HEIGHT):
        # Initialize pygame
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Jammin' Eats")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_state = MENU
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize game objects
        self.player = None
        self.game_map = None
        self.customers = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()
        self.sounds = {}
        
        # Setup economy and tracking
        self.selected_food = None
        self.money = 0
        self.successful_deliveries = 0
        
        # Initialize persistence
        self.persistence = GamePersistence()
        
        # Setup tutorial flow
        if not is_tutorial_complete(self.persistence.player_id):
            self.tutorial_state = TutorialState(self)
        else:
            self.tutorial_state = None

    def run(self):
        """Main loop: tutorial, title, then gameplay."""
        # Tutorial Phase
        if self.tutorial_state:
            state = self.tutorial_state
            state.enter()
            while True:
                dt = self.clock.tick(FPS) / 1000.0
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if state.handle_event(event):
                        if state.next_state:
                            state.exit()
                            state = state.next_state
                            state.enter()
                        continue
                state.update(dt)
                state.draw(self.screen)
                pygame.display.flip()
                if isinstance(state, TitleState):
                    break

        # Title Phase
        title_state = TitleState(self)
        title_state.enter()
        while self.game_state != PLAYING:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if title_state.handle_event(event):
                    continue
            title_state.update(dt)
            title_state.draw(self.screen)
            pygame.display.flip()

        # Start main gameplay
        self.run_gameplay()

    def run_gameplay(self):
        """Extracted gameplay loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            # Input
            for event in pygame.event.get():
                if hasattr(self, 'shop') and self.shop.handle_event(event):
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    self.shop.toggle()
                    continue
                if event.type == pygame.QUIT:
                    running = False
                if self.game_state == MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.start_button.is_clicked(event):
                            if self.player is None:
                                self.reset_game()
                            else:
                                self.reset_state()
                            self.game_state = PLAYING
                        if self.exit_button.is_clicked(event):
                            running = False
                elif self.game_state == PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            self.spawn_customer()
                        food_keys = {
                            pygame.K_1: "Tropical Pizza Slice",
                            pygame.K_2: "Ska Smoothie",
                            pygame.K_3: "Island Ice Cream",
                            pygame.K_4: "Rasta Rice Pudding"
                        }
                        if event.key in food_keys:
                            self.selected_food = food_keys[event.key]
                            if 'select_sound' in self.sounds and self.sounds['select_sound']:
                                self.sounds['select_sound'].play()

            # Spawn logic
            if self.game_state == PLAYING:
                if not hasattr(self, 'customer_spawn_timer'):
                    self.customer_spawn_timer = 0
                self.customer_spawn_timer += dt
                if self.customer_spawn_timer >= CUSTOMER_SPAWN_RATE:
                    self.spawn_customer()
                    self.customer_spawn_timer = 0

            # Updates
            if self.player:
                self.player.update(dt, self.customers, self.foods, self.game_map)
            self.customers.update(dt)
            self.foods.update(dt)

            # Collision and economy
            for food in list(self.foods):
                for customer in list(self.customers):
                    if food.collides_with(customer):
                        was_fed_before = getattr(customer, 'fed', False)
                        customer.feed(food.food_type)
                        food.kill()
                        if getattr(customer, 'fed', False) and not was_fed_before:
                            payment = self.economy.calculate_delivery_payment(food.food_type, "perfect_delivery")
                            self.economy.add_money(payment, reason=f"Delivery to {customer.type}")

            # Render
            if hasattr(self, 'particles'):
                self.particles.update(dt)
            self._render(mouse_pos)
            pygame.display.flip()

    def draw_current_state(self, screen):
        """Draw the current game state - used by tutorial and other states."""
        # Clear the screen
        screen.fill((0, 0, 0))  # Black background
        
        # Draw map if available
        if self.game_map:
            self.game_map.draw(screen)
            
        # Draw game objects
        if self.player:
            self.player.draw(screen)
        self.customers.draw(screen)
        self.foods.draw(screen)
    
    def _render(self, mouse_pos):
        """Render the game screen."""
        # First draw the base game state
        self.draw_current_state(self.screen)
        
        # Then add gameplay UI elements
        font = pygame.font.SysFont(None, 24)
        money_text = font.render(f'${self.money}', True, (255, 255, 255))
        self.screen.blit(money_text, (10, 10))
        
        # Draw selected food indicator if applicable
        if self.selected_food:
            selected_text = font.render(f'Selected: {self.selected_food}', True, (255, 255, 255))
            self.screen.blit(selected_text, (10, 40))
        
        # Draw shop button indicator
        shop_text = font.render('Press B to open shop', True, (255, 255, 255))
        self.screen.blit(shop_text, (10, self.screen_height - 30))
    
    def reset_game(self):
        """Reset the game to initial state."""
        # Initialize or reset game objects
        # This is a simplified implementation
        from src.sprites.player import Player  # Import here to avoid circular imports
        from src.map.game_map import GameMap
        
        self.player = Player(self.screen_width // 2, self.screen_height // 2)
        self.game_map = GameMap()
        self.customers.empty()
        self.foods.empty()
        
        # Reset economy
        self.money = 0
        self.successful_deliveries = 0
        self.selected_food = None
        
        # Initialize shop if not already done
        if not hasattr(self, 'shop'):
            from src.ui.shop import Shop  # Import here to avoid circular imports
            self.shop = Shop(self)
        
        # Initialize economy if not already done
        if not hasattr(self, 'economy'):
            from src.economy.economy import Economy  # Import here to avoid circular imports
            self.economy = Economy(self)
        
        # Initialize particles if not already done
        if not hasattr(self, 'particles'):
            from src.effects.particles import ParticleSystem  # Import here to avoid circular imports
            self.particles = ParticleSystem()
    
    def reset_state(self):
        """Reset the game state without recreating objects."""
        self.money = 0
        self.successful_deliveries = 0
        self.selected_food = None
        self.customers.empty()
        self.foods.empty()
        
        # Reset player position if exists
        if self.player:
            self.player.reset_position()
    
    def spawn_customer(self):
        """Spawn a new customer at a valid spawn point."""
        from src.sprites.customer import Customer  # Import here to avoid circular imports
        import random
        
        # Get valid spawn points from the map or use predefined positions
        spawn_points = getattr(self.game_map, 'customer_spawn_points', [(100, 100), (200, 100), (300, 100)])
        
        if spawn_points:
            x, y = random.choice(spawn_points)
            customer = Customer(x, y)
            self.customers.add(customer)
