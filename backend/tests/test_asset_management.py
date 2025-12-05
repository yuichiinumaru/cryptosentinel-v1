import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.tools.asset_management import AssetManagementToolkit, MonitorTransactionsInput

class TestAssetManagement(unittest.IsolatedAsyncioTestCase):
    async def test_monitor_transactions(self):
        toolkit = AssetManagementToolkit()

        # Mock httpx response
        mock_response = MagicMock() # Response object is not async
        mock_response.json.return_value = {
            "status": "1",
            "result": [
                {"hash": "0x123", "value": "1000000000000000000", "to": "0xABC", "timeStamp": "1600000000"}
            ]
        }
        mock_response.raise_for_status = lambda: None

        # Mock AsyncClient context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response # get() is awaited, returns response

        # Mock AsyncClient constructor to return context manager
        # async with httpx.AsyncClient() as client:
        # __aenter__ returns client instance
        mock_client_cls = MagicMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
        mock_client_cls.return_value.__aexit__.return_value = AsyncMock()

        with patch('httpx.AsyncClient', new=mock_client_cls):

            output = await toolkit.monitor_transactions(MonitorTransactionsInput(
                wallet_address="0xUser",
                chain="ethereum"
            ))

            self.assertEqual(len(output.transactions), 1)
            self.assertEqual(output.transactions[0]["value"], "1")

if __name__ == "__main__":
    unittest.main()
