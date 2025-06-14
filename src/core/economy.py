"""
Economy System for Jammin' Eats - Revised for Progression
Handles money, pricing, and economic progression through the game
"""

from enum import Enum


class EconomyPhase(Enum):
    """Different phases of the game economy"""

    TUTORIAL = "tutorial"  # Working for tips only
    STARTUP = "startup"  # Low margins, building capital
    GROWTH = "growth"  # Better margins
    ESTABLISHED = "established"  # Good profits
    FESTIVAL = "festival"  # Special event pricing


class Economy:
    """
    Manages the game's economy with progression-based pricing
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Starting conditions - player starts with nothing!
        self.money = 0.00
        self.lifetime_earnings = 0.00

        # Current phase
        self.phase = EconomyPhase.TUTORIAL
        self.current_map = 1
        self.current_frame = 1

        # Base food economics (buy/sell prices by food type)
        self.base_food_economics = {
            "pizza": {
                "buy": 3.00,
                "sell": 6.00,
                "unlock_cost": 0.00,  # Starter food
                "unlocked": True,
            },
            "smoothie": {
                "buy": 4.00,
                "sell": 8.00,
                "unlock_cost": 20.00,
                "unlocked": False,
            },
            "icecream": {
                "buy": 5.00,
                "sell": 10.00,
                "unlock_cost": 50.00,
                "unlocked": False,
            },
            "pudding": {
                "buy": 3.50,
                "sell": 7.00,
                "unlock_cost": 30.00,
                "unlocked": False,
            },
            "rasgulla": {
                "buy": 6.00,
                "sell": 12.00,
                "unlock_cost": 100.00,
                "unlocked": False,
            },
        }

        # Phase-based multipliers
        self.phase_multipliers = {
            EconomyPhase.TUTORIAL: {
                "buy": 0.0,  # Free during tutorial
                "sell": 0.5,  # Only get tips (50% of normal)
                "customer_spawn": 0.5,  # Fewer customers
            },
            EconomyPhase.STARTUP: {"buy": 1.0, "sell": 1.0, "customer_spawn": 1.0},
            EconomyPhase.GROWTH: {
                "buy": 1.0,
                "sell": 1.2,  # 20% better prices
                "customer_spawn": 1.5,
            },
            EconomyPhase.ESTABLISHED: {
                "buy": 0.9,  # 10% discount on supplies
                "sell": 1.5,  # 50% better prices
                "customer_spawn": 2.0,
            },
            EconomyPhase.FESTIVAL: {
                "buy": 0.8,  # Bulk discounts
                "sell": 3.0,  # Premium festival prices!
                "customer_spawn": 3.0,
            },
        }

        # Delivery bonuses/penalties
        self.delivery_modifiers = {
            "perfect_delivery": 1.5,  # 50% bonus for happy customer
            "standard_delivery": 1.0,  # Base price
            "late_delivery": 0.7,  # 30% penalty
            "wrong_delivery": -0.5,  # Lose 50% of food cost
            "missed_customer": -1.0,  # Lose full food cost
        }

        # Track statistics
        self.session_stats = {
            "deliveries": 0,
            "perfect_deliveries": 0,
            "money_earned": 0.00,
            "money_spent": 0.00,
            "tips_earned": 0.00,
        }

        self._initialized = True

    def get_food_price(self, food_type: str, price_type: str = "sell") -> float:
        """
        Get current price for a food item based on phase and type

        Args:
            food_type: Type of food ('pizza', 'smoothie', etc.)
            price_type: 'buy' or 'sell'

        Returns:
            float: Current price
        """
        if food_type not in self.base_food_economics:
            return 0.0

        base_price = self.base_food_economics[food_type][price_type]
        multiplier = self.phase_multipliers[self.phase][price_type]

        return round(base_price * multiplier, 2)

    def calculate_delivery_payment(
        self, food_type: str, delivery_quality: str
    ) -> float:
        """
        Calculate payment for a delivery

        Args:
            food_type: Type of food delivered
            delivery_quality: Quality of delivery (perfect/standard/late/wrong)

        Returns:
            float: Money earned (can be negative for penalties)
        """
        sell_price = self.get_food_price(food_type, "sell")
        modifier = self.delivery_modifiers.get(delivery_quality, 1.0)

        payment = sell_price * modifier

        # In tutorial phase, it's just tips
        if self.phase == EconomyPhase.TUTORIAL and payment > 0:
            payment = min(payment, 2.00)  # Max $2 tips during tutorial
            self.session_stats["tips_earned"] += payment

        return round(payment, 2)

    def can_afford_food(self, food_type: str, quantity: int = 1) -> bool:
        """Check if player can afford to buy food"""
        if self.phase == EconomyPhase.TUTORIAL:
            return True  # Free during tutorial

        cost = self.get_food_price(food_type, "buy") * quantity
        return self.money >= cost

    def purchase_food(self, food_type: str, quantity: int = 1) -> bool:
        """Purchase food items"""
        if self.phase == EconomyPhase.TUTORIAL:
            return True  # Free during tutorial

        cost = self.get_food_price(food_type, "buy") * quantity

        if not self.can_afford_food(food_type, quantity):
            return False

        self.money -= cost
        self.session_stats["money_spent"] += cost

        print(f"[ECONOMY] Purchased {quantity}x {food_type} for ${cost:.2f}")
        return True

    def unlock_food(self, food_type: str) -> bool:
        """Unlock a new food type"""
        if food_type not in self.base_food_economics:
            return False

        food_data = self.base_food_economics[food_type]

        if food_data["unlocked"]:
            return True  # Already unlocked

        unlock_cost = food_data["unlock_cost"]

        if self.money >= unlock_cost:
            self.money -= unlock_cost
            food_data["unlocked"] = True
            print(f"[ECONOMY] Unlocked {food_type} for ${unlock_cost:.2f}!")
            return True

        return False

    def update_phase(self, map_num: int, frame_num: int):
        """Update economy phase based on progression"""
        self.current_map = map_num
        self.current_frame = frame_num

        # Determine phase
        if map_num == 1 and frame_num <= 3:
            self.phase = EconomyPhase.TUTORIAL
        elif map_num == 1:
            self.phase = EconomyPhase.STARTUP
        elif map_num <= 2:
            self.phase = EconomyPhase.GROWTH
        elif map_num <= 4:
            self.phase = EconomyPhase.ESTABLISHED
        else:
            self.phase = EconomyPhase.ESTABLISHED

    def set_festival_mode(self, active: bool):
        """Toggle festival pricing"""
        if active:
            self.phase = EconomyPhase.FESTIVAL
        else:
            # Return to normal phase based on progression
            self.update_phase(self.current_map, self.current_frame)

    def add_money(self, amount: float, reason: str = ""):
        """Add money with tracking"""
        self.money += amount
        self.lifetime_earnings += max(0, amount)

        if amount > 0:
            self.session_stats["money_earned"] += amount

        # Prevent negative money
        self.money = max(0, self.money)

        if reason:
            print(f"[ECONOMY] {reason}: ${amount:+.2f} (Total: ${self.money:.2f})")
