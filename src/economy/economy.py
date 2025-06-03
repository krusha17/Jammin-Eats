import pygame
from src.core.constants import FOOD_PRICES

class Economy:
    """Manages the in-game economy including prices, inventory, and transactions.
    
    This class handles:
    - Food/item pricing
    - Purchase and sale transactions
    - Money management
    - Economic simulation (price fluctuations, etc.)
    """
    
    def __init__(self, game):
        self.game = game
        self.transaction_log = []  # Track all economic transactions
        
        # Initialize default prices if not defined in constants
        self.prices = getattr(FOOD_PRICES, {}) if hasattr(globals(), 'FOOD_PRICES') else {
            "Tropical Pizza Slice": {"buy_price": 5, "sell_price": 10},
            "Ska Smoothie": {"buy_price": 3, "sell_price": 7},
            "Island Ice Cream": {"buy_price": 4, "sell_price": 8},
            "Rasta Rice Pudding": {"buy_price": 2, "sell_price": 5}
        }
        
        # Initialize demand factors
        self.demand_factors = {
            "Tropical Pizza Slice": 1.0,
            "Ska Smoothie": 1.0,
            "Island Ice Cream": 1.0,
            "Rasta Rice Pudding": 1.0
        }
        
        # Track customer preferences
        self.customer_preferences = {}
    
    def get_buy_price(self, item_name):
        """Get the current buy price for an item."""
        if item_name in self.prices:
            return self.prices[item_name]["buy_price"]
        return 0  # Item not found
    
    def get_sell_price(self, item_name):
        """Get the current sell price for an item."""
        if item_name in self.prices:
            base_price = self.prices[item_name]["sell_price"]
            # Apply demand factor
            if item_name in self.demand_factors:
                demand_modifier = self.demand_factors[item_name]
                return int(base_price * demand_modifier)
            return base_price
        return 0  # Item not found
    
    def log_transaction(self, transaction_type, item_name, amount, price):
        """Log a transaction for analytics."""
        import time
        transaction = {
            "timestamp": time.time(),
            "type": transaction_type,  # 'buy' or 'sell'
            "item": item_name,
            "amount": amount,
            "price": price,
            "total": amount * price
        }
        self.transaction_log.append(transaction)
        
        # Update demand factors based on transactions
        if transaction_type == "sell" and item_name in self.demand_factors:
            # Slightly increase demand for items that sell well
            self.demand_factors[item_name] *= 1.01
            # Cap the demand factor
            self.demand_factors[item_name] = min(self.demand_factors[item_name], 1.5)
    
    def purchase_item(self, item_name, amount=1):
        """Purchase an item (player buying from supplier)."""
        if not hasattr(self.game, 'money'):
            print("[ERROR] Game object has no money attribute")
            return False
            
        price = self.get_buy_price(item_name) * amount
        
        # Check if the player has enough money
        if self.game.money >= price:
            # Deduct money
            self.game.money -= price
            
            # Add to inventory if it exists
            if hasattr(self.game, 'inventory') and self.game.inventory is not None:
                self.game.inventory.add_item(item_name, amount)
            
            # Log the transaction
            self.log_transaction("buy", item_name, amount, price / amount)
            return True
        
        return False  # Not enough money
    
    def sell_item(self, item_name, amount=1):
        """Sell an item (customer buying from player)."""
        if not hasattr(self.game, 'money'):
            print("[ERROR] Game object has no money attribute")
            return False
            
        price = self.get_sell_price(item_name) * amount
        
        # Add money to player
        self.game.money += price
        
        # Log the transaction
        self.log_transaction("sell", item_name, amount, price / amount)
        
        # Update success metrics if they exist
        if hasattr(self.game, 'successful_deliveries'):
            self.game.successful_deliveries += amount
        
        return True
    
    def update_prices(self, game_time):
        """Update prices based on time of day, events, etc."""
        # This would be more complex in a full implementation
        # For now, just small random fluctuations
        import random
        
        for item in self.prices:
            # Small random price fluctuation (±5%)
            fluctuation = 0.95 + (random.random() * 0.1)  # 0.95 to 1.05
            
            # Apply fluctuation to buy price
            new_buy_price = max(1, int(self.prices[item]["buy_price"] * fluctuation))
            self.prices[item]["buy_price"] = new_buy_price
            
            # Apply fluctuation to sell price, ensuring markup
            new_sell_price = max(new_buy_price + 1, int(self.prices[item]["sell_price"] * fluctuation))
            self.prices[item]["sell_price"] = new_sell_price
    
    def get_recommended_items(self):
        """Get list of items recommended for purchase based on profit margin."""
        recommendations = []
        
        for item in self.prices:
            buy_price = self.prices[item]["buy_price"]
            sell_price = self.get_sell_price(item)  # Use the demand-adjusted price
            profit_margin = sell_price - buy_price
            roi = profit_margin / buy_price if buy_price > 0 else 0
            
            recommendations.append({
                "item": item,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "profit": profit_margin,
                "roi": roi
            })
        
        # Sort by ROI (return on investment)
        recommendations.sort(key=lambda x: x["roi"], reverse=True)
        return recommendations
