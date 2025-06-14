from src.core.inventory import Inventory
from src.core.constants import STARTING_STOCK


def test_basic_consume():
    """Test that consuming an item decreases its stock count"""
    inv = Inventory(STARTING_STOCK)
    assert inv.consume("Tropical Pizza Slice")
    assert inv.qty("Tropical Pizza Slice") == STARTING_STOCK["Tropical Pizza Slice"] - 1


def test_consume_out_of_stock():
    """Test that consuming an out-of-stock item fails"""
    inv = Inventory({"Tropical Pizza Slice": 0})
    assert not inv.consume("Tropical Pizza Slice")
    assert inv.qty("Tropical Pizza Slice") == 0


def test_add_to_inventory():
    """Test adding items respects MAX_STOCK limit"""
    from src.core.constants import MAX_STOCK

    inv = Inventory({"Tropical Pizza Slice": 0})
    inv.add("Tropical Pizza Slice", MAX_STOCK + 5)
    assert inv.qty("Tropical Pizza Slice") == MAX_STOCK


def test_nonexistent_item():
    """Test handling of non-existent items"""
    inv = Inventory({})
    assert inv.qty("Nonexistent Item") == 0
    assert not inv.in_stock("Nonexistent Item")


def test_purchase_deducts_money():
    """Test that purchasing deducts correct amount of money and adds stock"""
    inv = Inventory({"Tropical Pizza Slice": 0})
    money = 10
    spent = inv.purchase("Tropical Pizza Slice", money, qty=2)
    assert spent == 4  # 2 * buy_price
    assert inv.qty("Tropical Pizza Slice") == 2


def test_purchase_insufficient_funds():
    """Test purchase fails with insufficient funds"""
    inv = Inventory({"Island Ice Cream": 0})
    money = 0
    spent = inv.purchase("Island Ice Cream", money, qty=1)
    assert spent == 0
    assert inv.qty("Island Ice Cream") == 0
