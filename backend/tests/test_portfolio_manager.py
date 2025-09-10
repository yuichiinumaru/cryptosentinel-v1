import unittest
from backend.PortfolioManager.PortfolioManager import portfolio_manager

class TestPortfolioManager(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(portfolio_manager)
        self.assertEqual(portfolio_manager.name, "PortfolioManager")

if __name__ == "__main__":
    unittest.main()
