import unittest
from backend.MarketAnalyst.MarketAnalyst import market_analyst

class TestMarketAnalyst(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(market_analyst)
        self.assertEqual(market_analyst.name, "MarketAnalyst")

if __name__ == "__main__":
    unittest.main()
