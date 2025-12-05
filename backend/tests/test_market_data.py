import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.tools.market_data import MarketDataToolkit, FetchMarketDataInput

class TestMarketData(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_parallel(self):
        toolkit = MarketDataToolkit()

        # Mock Responses
        mock_price_resp = MagicMock()
        mock_price_resp.json.return_value = {"bitcoin": {"usd": 50000}, "ethereum": {"usd": 3000}}
        mock_price_resp.raise_for_status = lambda: None

        mock_hist_resp = MagicMock()
        mock_hist_resp.json.return_value = {"prices": [[1000, 50000]]}
        mock_hist_resp.raise_for_status = lambda: None
        mock_hist_resp.status_code = 200

        mock_client = AsyncMock()

        # Side effect for client.get to differentiate URLs?
        async def side_effect(url, timeout=None):
            if "simple/price" in url:
                return mock_price_resp
            return mock_hist_resp

        mock_client.get.side_effect = side_effect

        mock_client_cls = MagicMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = AsyncMock()

        with patch('httpx.AsyncClient', new=mock_client_cls):
            input_data = FetchMarketDataInput(
                coin_ids=["bitcoin", "ethereum"],
                vs_currency="usd",
                include_history=True
            )
            output = await toolkit.fetch_market_data(input_data)

            self.assertEqual(output.market_data["bitcoin"]["usd"], 50000)
            self.assertTrue("history" in output.market_data["bitcoin"])

if __name__ == "__main__":
    unittest.main()
