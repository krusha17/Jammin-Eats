import unittest
import sys
import os

# Add project root to path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.upgrade_manager import UpgradeManager
from src.core.constants import UPGRADE_DATA

class TestUpgradeManager(unittest.TestCase):
    def setUp(self):
        # Create a fresh UpgradeManager for each test
        self.upgrade_manager = UpgradeManager()
        # Mock money for testing
        self.test_money = 1000  # Plenty of money for most upgrades
    
    def test_initialization(self):
        """Test that the UpgradeManager initializes correctly"""
        # Default initialization should have no upgrades
        self.assertEqual(len(self.upgrade_manager.owned), 0)
        
        # Initialize with some upgrades
        um = UpgradeManager(['UP_SKATE', 'UP_TRUCK'])
        self.assertEqual(len(um.owned), 2)
        self.assertTrue(um.has('UP_SKATE'))
        self.assertTrue(um.has('UP_TRUCK'))
    
    def test_has_upgrade(self):
        """Test the has() method for checking owned upgrades"""
        # Should not have any upgrades initially
        self.assertFalse(self.upgrade_manager.has('UP_SKATE'))
        
        # Add an upgrade and check again
        self.upgrade_manager.owned.add('UP_SKATE')
        self.assertTrue(self.upgrade_manager.has('UP_SKATE'))
    
    def test_get_all_available(self):
        """Test getting all available upgrades"""
        # Initially all base upgrades should be available (no prerequisites)
        available = self.upgrade_manager.get_all_available()
        self.assertIn('UP_SKATE', available)  # No prerequisites
        self.assertIn('UP_TRUCK', available)  # No prerequisites
        self.assertNotIn('UP_BLADE', available)  # Requires UP_SKATE
        
        # After owning UP_SKATE, UP_BLADE should become available
        self.upgrade_manager.owned.add('UP_SKATE')
        available = self.upgrade_manager.get_all_available()
        self.assertIn('UP_BLADE', available)  # Now should be available
        self.assertNotIn('UP_JETS', available)  # Still unavailable (requires UP_BLADE)
    
    def test_affordable(self):
        """Test the affordable() method"""
        # All base upgrades should be affordable with enough money
        self.assertTrue(self.upgrade_manager.affordable('UP_SKATE', self.test_money))
        
        # Should not be affordable with insufficient money
        self.assertFalse(self.upgrade_manager.affordable('UP_SKATE', 10))
        
        # UP_BLADE should not be affordable without owning UP_SKATE
        self.assertFalse(self.upgrade_manager.affordable('UP_BLADE', self.test_money))
        
        # After buying UP_SKATE, UP_BLADE should be affordable
        self.upgrade_manager.owned.add('UP_SKATE')
        self.assertTrue(self.upgrade_manager.affordable('UP_BLADE', self.test_money))
        
        # After buying UP_BLADE, it should no longer be affordable (already owned)
        self.upgrade_manager.owned.add('UP_BLADE')
        self.assertFalse(self.upgrade_manager.affordable('UP_BLADE', self.test_money))
    
    def test_buy_upgrade(self):
        """Test buying upgrades"""
        # Try to buy UP_SKATE with enough money
        cost = self.upgrade_manager.buy('UP_SKATE', self.test_money)
        self.assertEqual(cost, UPGRADE_DATA['UP_SKATE']['cost'])
        self.assertTrue(self.upgrade_manager.has('UP_SKATE'))
        
        # Try to buy UP_SKATE again (should fail)
        cost = self.upgrade_manager.buy('UP_SKATE', self.test_money)
        self.assertEqual(cost, 0)  # Should not deduct money
        
        # Try to buy UP_BLADE (should succeed now that we have UP_SKATE)
        cost = self.upgrade_manager.buy('UP_BLADE', self.test_money)
        self.assertEqual(cost, UPGRADE_DATA['UP_BLADE']['cost'])
        self.assertTrue(self.upgrade_manager.has('UP_BLADE'))
        
        # Try to buy UP_JETS with insufficient money
        insufficient_money = 10
        cost = self.upgrade_manager.buy('UP_JETS', insufficient_money)
        self.assertEqual(cost, 0)  # Should not deduct money
        self.assertFalse(self.upgrade_manager.has('UP_JETS'))
    
    def test_get_details(self):
        """Test getting detailed information about upgrades"""
        # Get details for UP_SKATE
        details = self.upgrade_manager.get_details('UP_SKATE')
        self.assertIsNotNone(details)
        self.assertEqual(details['name'], 'Skateboard')
        self.assertEqual(details['cost'], 150)
        self.assertFalse(details['owned'])
        
        # Buy UP_SKATE and check details again
        self.upgrade_manager.buy('UP_SKATE', self.test_money)
        details = self.upgrade_manager.get_details('UP_SKATE')
        self.assertTrue(details['owned'])

if __name__ == '__main__':
    unittest.main()
