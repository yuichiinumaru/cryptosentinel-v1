import unittest
from backend.AnalistaDeSentimento.AnalistaDeSentimento import analista_de_sentimento

class TestAnalistaDeSentimento(unittest.TestCase):
    def test_agent_initialization(self):
        self.assertIsNotNone(analista_de_sentimento)
        self.assertEqual(analista_de_sentimento.name, "Analista de Sentimento de Mercado")

if __name__ == "__main__":
    unittest.main()
