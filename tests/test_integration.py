import unittest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
import json
from datetime import datetime
from uuid import uuid4

from backend.main import app, get_api_key
from backend.protocol import TradeRecommendation, TradeOrder, TradeResult, MessageHeader

class TestAgentIntegration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Mock the API key dependency for all tests in this class
        app.dependency_overrides[get_api_key] = lambda: "test_api_key"

    def tearDown(self):
        # Clear the dependency overrides after each test
        app.dependency_overrides = {}

    @patch('agno.sync_layer.SyncLayer._create_completion')
    def test_full_trade_workflow(self, mock_create_completion):
        # I'm patching agno's SyncLayer._create_completion, which is a more
        # reliable target than guessing the specific OpenAI method. This is
        # an internal method, but for testing purposes it's a good seam.

        # --- 1. Define the mock LLM responses for each agent's turn ---

        # The LLM's raw response is a string of JSON.

        # MarketAnalyst response: output a TradeRecommendation JSON
        recommendation_payload = {
            "header": {
                "sender": "MarketAnalyst",
                "recipient": "DeepTraderManager",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid4()),
                "priority": "medium"
            },
            "token_address": "0xBTC",
            "chain": "Bitcoin",
            "action": "buy",
            "amount": 0.1,
            "confidence": 0.95,
            "reasoning": "RSI is low, indicating a buy signal."
        }
        market_analyst_response_str = json.dumps(recommendation_payload)

        # DeepTraderManager response: output a TradeOrder JSON
        order_payload = {
            "header": {
                "sender": "DeepTraderManager",
                "recipient": "Trader",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid4()),
                "priority": "high"
            },
            "symbol": "BTC/USD",
            "action": "buy",
            "quantity": 0.05, # Risk-adjusted
            "order_type": "market"
        }
        manager_response_str = json.dumps(order_payload)

        # Trader response: output a TradeResult JSON
        result_payload = {
            "header": {
                "sender": "Trader",
                "recipient": "DeepTraderManager",
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid4()),
                "priority": "medium"
            },
            "order_id": "order-123",
            "symbol": "BTC/USD",
            "action": "buy",
            "quantity": 0.05,
            "price": 50000.0,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        trader_response_str = json.dumps(result_payload)

        # Final response from DeepTraderManager after receiving the result
        final_manager_response_str = "Trade completed successfully and logged."

        # Set the side_effect for the mock LLM calls
        mock_create_completion.side_effect = [
            market_analyst_response_str,
            manager_response_str,
            trader_response_str,
            final_manager_response_str,
        ]

        # --- 2. Trigger the workflow by sending a message to the MarketAnalyst ---
        initial_message = "Analyze the BTC market and suggest a trade."
        response = self.client.post(
            "/chat",
            json={"message": initial_message, "agent": "MarketAnalyst"}
        )

        # --- 3. Assertions ---
        self.assertEqual(response.status_code, 200)

        # The final response should be the one from the DeepTraderManager
        self.assertEqual(response.json(), {"response": final_manager_response_str})

        # Check that the mock was called the correct number of times
        self.assertEqual(mock_create_completion.call_count, 4)

        # We can also inspect the calls to see if the messages were passed correctly
        # First call is from User to MarketAnalyst
        first_call_args = mock_create_completion.call_args_list[0]
        self.assertIn(initial_message, str(first_call_args))

        # Second call is from MarketAnalyst to DeepTraderManager, containing the recommendation
        second_call_args = mock_create_completion.call_args_list[1]
        self.assertIn("TradeRecommendation", str(second_call_args))
        self.assertIn("RSI is low", str(second_call_args))

        # Third call is from DeepTraderManager to Trader, containing the order
        third_call_args = mock_create_completion.call_args_list[2]
        self.assertIn("TradeOrder", str(third_call_args))
        self.assertIn("Risk-adjusted", str(third_call_args))

        # Fourth call is from Trader to DeepTraderManager, containing the result
        fourth_call_args = mock_create_completion.call_args_list[3]
        self.assertIn("TradeResult", str(fourth_call_args))
        self.assertIn("order-123", str(fourth_call_args))

if __name__ == '__main__':
    unittest.main()
