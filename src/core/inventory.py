from src.core import constants

class Inventory:
    def __init__(self, initial_stock: dict[str, int]):
        # Copy so tests can mutate safely
        self.stock = dict(initial_stock)

    def __repr__(self):
        """String representation for debugging"""
        return f"Inventory({self.stock})"

    # ---------- Query ----------
    def in_stock(self, item: str) -> bool:
        """Check if an item is in stock"""
        return self.stock.get(item, 0) > 0

    def qty(self, item: str) -> int:
        """Get quantity of an item in stock"""
        return self.stock.get(item, 0)

    # ---------- Mutate ----------
    def consume(self, item: str) -> bool:
        """
        Consume one unit of an item if available.
        Return True if successfully deducted.
        """
        if self.in_stock(item):
            self.stock[item] -= 1
            return True
        return False

    def add(self, item: str, qty: int = 1) -> None:
        """Add quantity of an item to inventory, respecting MAX_STOCK"""
        if item not in self.stock:
            self.stock[item] = 0
        self.stock[item] = min(self.qty(item) + qty, constants.MAX_STOCK)
    
    def purchase(self, item: str, money: int, qty: int = 1) -> int:
        """
        Attempt to purchase qty of item with available money.
        Returns the amount spent if successful, otherwise 0.
        """
        if item not in constants.FOOD_PRICES:
            return 0
            
        cost = constants.FOOD_PRICES[item]["buy_price"] * qty
        if money >= cost:
            self.add(item, qty)
            return cost
        return 0
