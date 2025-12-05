import unittest
from unittest.mock import MagicMock, patch
import asyncio
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Assuming the agent and tool definitions are in these modules
from backend.agents import market_analyst, trader_agent, deep_trader_manager, portfolio_manager, get_crypto_trading_team
from backend.tools.market_data import fetch_market_data
from backend.tools.token_security import check_token_security
from backend.tools.dex import dex_toolkit
from backend.tools.portfolio import get_portfolio

class TestAgentCommunication(unittest.TestCase):

    @patch('backend.tools.market_data.CoinGeckoAPI')
    @patch('backend.tools.token_security.requests.get')
    @patch('backend.tools.dex.Web3')
    @patch('backend.tools.wallet.Web3')
    @patch('agno.models.google.Gemini')
    def test_trading_workflow(self, MockGemini, MockWalletWeb3, MockDexWeb3, mock_requests_get, MockCoinGeckoAPI):
        print("Running test_trading_workflow...")
        # 1. Mock external dependencies
        # Mock Gemini
        mock_gemini_instance = MockGemini.return_value
        mock_gemini_instance.generate_content.return_value.text = "buy"

        # Mock CoinGecko
        mock_coingecko_instance = MockCoinGeckoAPI.return_value
        mock_coingecko_instance.get_price.return_value = {'bitcoin': {'usd': 50000}}
        mock_coingecko_instance.get_coin_market_chart_by_id.return_value = {
            'prices': [[1678886400000, 49000], [1678972800000, 50000]],
            'total_volumes': [[1678886400000, 1000000], [1678972800000, 1200000]],
            'market_caps': [[1678886400000, 900000000], [1678972800000, 950000000]]
        }

        # Mock Rugcheck
        mock_rugcheck_response = MagicMock()
        mock_rugcheck_response.json.return_value = {'score': 95}
        mock_requests_get.return_value = mock_rugcheck_response

        # Mock Web3
        mock_web3_instance = MockDexWeb3.return_value
        mock_web3_instance.eth.get_balance.return_value = 10 * 10**18  # 10 ETH
        mock_web3_instance.eth.get_transaction_count.return_value = 1
        mock_web3_instance.eth.gas_price = 50 * 10**9 # 50 gwei
        mock_web3_instance.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        mock_web3_instance.to_wei.return_value = 10**18
        mock_web3_instance.from_wei.return_value = 1.0
        MockWalletWeb3.return_value = mock_web3_instance


        # 2. Setup Agency and mock agent interactions
        # RESURRECTION FIX: Use Factory
        team = get_crypto_trading_team("test-session")

        # We need to mock the `invoke` method of the agents to simulate communication
        market_analyst.invoke = MagicMock(return_value="Recommend buying Bitcoin.")
        deep_trader_manager.invoke = MagicMock(return_value="Trader, please buy 0.05 Bitcoin.")
        trader_agent.invoke = MagicMock(return_value="Executing buy order for 0.05 Bitcoin.")

        # Mock tools to track calls
        market_analyst.tools = [MagicMock(spec=fetch_market_data), MagicMock(spec=check_token_security)]
        trader_agent.tools = [MagicMock(spec=dex_toolkit.execute_swap), MagicMock(spec=get_portfolio), MagicMock()]
        deep_trader_manager.tools = []
        portfolio_manager.tools = []


        # 3. Run the workflow
        # This is a simplified way to test the flow.
        # A true integration test would involve the team's `invoke` method
        # and mocking the LLM responses at each step.

        # Step 1: Market Analyst analyzes and recommends
        analyst_output = market_analyst.invoke("Analyze the market for trading opportunities.")
        self.assertIn("Bitcoin", analyst_output)

        # Step 2: Manager receives recommendation and approves
        manager_output = deep_trader_manager.invoke(f"Market Analyst recommends: {analyst_output}. Should I approve?")
        self.assertIn("Trader, please buy", manager_output)

        # Step 3: Trader receives approval and executes
        trader_output = trader_agent.invoke(f"Manager says: {manager_output}")
        self.assertIn("Executing", trader_output)

        print("Test finished successfully.")


if __name__ == '__main__':
    unittest.main()
