import unittest
from backend.agents import get_crypto_trading_team
from agno.team.team import Team

class TestAgentsFactory(unittest.TestCase):
    def test_session_isolation(self):
        """
        Verify that two calls to get_crypto_trading_team with different session IDs
        return different Agent instances (memory isolation).
        """
        session_a = "session_a"
        session_b = "session_b"

        team_a = get_crypto_trading_team(session_a)
        team_b = get_crypto_trading_team(session_b)

        # Check Team IDs
        self.assertNotEqual(team_a.session_id, team_b.session_id)

        # Check Member Isolation
        # Get the 'Trader' agent from both teams
        trader_a = next(m for m in team_a.members if m.name == "Trader")
        trader_b = next(m for m in team_b.members if m.name == "Trader")

        # They should be different objects in memory
        self.assertIsNot(trader_a, trader_b)

    def test_missing_session_id(self):
        with self.assertRaises(ValueError):
            get_crypto_trading_team("")

if __name__ == "__main__":
    unittest.main()
