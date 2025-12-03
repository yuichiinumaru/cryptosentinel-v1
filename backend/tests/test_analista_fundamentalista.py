import unittest
from backend.AnalistaFundamentalista.AnalistaFundamentalista import analista_fundamentalista

class TestAnalistaFundamentalista(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(analista_fundamentalista)
        self.assertEqual(analista_fundamentalista.name, "Analista Fundamentalista")

if __name__ == "__main__":
    unittest.main()
