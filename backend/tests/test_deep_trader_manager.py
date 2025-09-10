import unittest
from backend.DeepTraderManager.DeepTraderManager import deep_trader_manager

class TestDeepTraderManager(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(deep_trader_manager)
        self.assertEqual(deep_trader_manager.name, "DeepTraderManager")

if __name__ == "__main__":
    unittest.main()
