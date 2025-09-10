import unittest
from backend.Trader.Trader import trader_agent

class TestTrader(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(trader_agent)
        self.assertEqual(trader_agent.name, "Trader")

if __name__ == "__main__":
    unittest.main()
