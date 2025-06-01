import unittest
from src.core.inventory import Inventory
from src.core.constants import STARTING_STOCK, FOOD_PRICES, MAX_STOCK

class TestInventory(unittest.TestCase):
    def test_basic_consume(self):
        """Test that consuming an item decreases its stock count"""
        inv = Inventory(STARTING_STOCK)
        self.assertTrue(inv.consume("Tropical Pizza Slice"))
        self.assertEqual(inv.qty("Tropical Pizza Slice"), STARTING_STOCK["Tropical Pizza Slice"] - 1)

    def test_consume_out_of_stock(self):
        """Test that consuming an out-of-stock item fails"""
        inv = Inventory({"Tropical Pizza Slice": 0})
        self.assertFalse(inv.consume("Tropical Pizza Slice"))
        self.assertEqual(inv.qty("Tropical Pizza Slice"), 0)

    def test_add_to_inventory(self):
        """Test adding items respects MAX_STOCK limit"""
        inv = Inventory({"Tropical Pizza Slice": 0})
        inv.add("Tropical Pizza Slice", MAX_STOCK + 5)
        self.assertEqual(inv.qty("Tropical Pizza Slice"), MAX_STOCK)

    def test_nonexistent_item(self):
        """Test handling of non-existent items"""
        inv = Inventory({})
        self.assertEqual(inv.qty("Nonexistent Item"), 0)
        self.assertFalse(inv.in_stock("Nonexistent Item"))
        
    def test_purchase_deducts_money(self):
        """Test that purchasing deducts correct amount of money and adds stock"""
        inv = Inventory({"Tropical Pizza Slice": 0})
        money = 10
        spent = inv.purchase("Tropical Pizza Slice", money, qty=2)
        self.assertEqual(spent, 4)  # 2 * buy_price
        self.assertEqual(inv.qty("Tropical Pizza Slice"), 2)

    def test_purchase_insufficient_funds(self):
        """Test purchase fails with insufficient funds"""
        inv = Inventory({"Island Ice Cream": 0})
        money = 0
        spent = inv.purchase("Island Ice Cream", money, qty=1)
        self.assertEqual(spent, 0)
        self.assertEqual(inv.qty("Island Ice Cream"), 0)

if __name__ == '__main__':
    unittest.main()
