import unittest
from backend.StrategyAgent.StrategyAgent import strategy_agent

class TestStrategyAgent(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(strategy_agent)
        self.assertEqual(strategy_agent.name, "StrategyAgent")

if __name__ == "__main__":
    unittest.main()
