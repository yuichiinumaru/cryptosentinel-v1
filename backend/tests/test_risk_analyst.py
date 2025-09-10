import unittest
from backend.RiskAnalyst.RiskAnalyst import risk_analyst

class TestRiskAnalyst(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(risk_analyst)
        self.assertEqual(risk_analyst.name, "RiskAnalyst")

if __name__ == "__main__":
    unittest.main()
