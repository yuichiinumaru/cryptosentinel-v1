import unittest
from unittest.mock import patch, MagicMock, ANY
import os
from fastapi.testclient import TestClient
import json
from datetime import datetime
from uuid import uuid4

# This needs to be set before the app is imported.
os.environ['GEMINI_API_KEY'] = 'dummy_key_for_testing'

from backend.main import app, get_api_key
from backend.protocol import TradeRecommendation, TradeOrder, TradeResult, MessageHeader

class TestAgentIntegration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        # We still need to override the dependency because the endpoint requires it,
        # but the environment variable handles the google library's needs.
        app.dependency_overrides[get_api_key] = lambda: "test_api_key"

    def tearDown(self):
        app.dependency_overrides = {}

    @patch('google.genai.models.Models._generate_content')
    def test_full_trade_workflow(self, mock_generate_content):
        # Patching the method that makes the actual API call in the google-genai library.

        # --- 1. Define the mock LLM responses for each agent's turn ---
        def create_mock_response(json_string):
            # This function creates a mock GenerateContentResponse object
            # that mimics the structure the agno parser expects.
            from google.genai.types import Part
            mock_response = MagicMock()
            mock_response.candidates = [MagicMock()]
            mock_response.candidates[0].content = MagicMock()
            mock_response.candidates[0].content.role = "model"
            mock_response.candidates[0].content.parts = [Part.from_text(text=json_string)]
            mock_response.usage_metadata = None
            mock_response.candidates[0].grounding_metadata = None
            return mock_response

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
            "order_type": "market",
            "reasoning": "Risk-adjusted order based on market analysis."
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
        mock_generate_content.side_effect = [
            create_mock_response(market_analyst_response_str),
            create_mock_response(manager_response_str),
            create_mock_response(trader_response_str),
            create_mock_response(final_manager_response_str),
        ]

        # --- 2. Trigger the workflow by sending a message to the MarketAnalyst ---
        initial_message = "Analyze the BTC market and suggest a trade."
        response = self.client.post(
            "/chat",
            json={"message": initial_message, "agent": "MarketAnalyst"}
        )

        # --- 3. Assertions ---
        self.assertEqual(response.status_code, 200)

        # The response from the generator needs to be assembled
        response_json = response.json()
        full_response = "".join(response_json.get("response", []))

        # The final response should be the one from the DeepTraderManager
        self.assertEqual(full_response, final_manager_response_str)

        # Check that the mock was called the correct number of times
        self.assertEqual(mock_generate_content.call_count, 4)

        # We can also inspect the calls to see if the messages were passed correctly
        # The 'contents' kwarg holds the list of messages.
        first_call_kwargs = mock_generate_content.call_args_list[0].kwargs
        self.assertIn(initial_message, str(first_call_kwargs['contents']))

        # Second call is from MarketAnalyst to DeepTraderManager, containing the recommendation
        second_call_kwargs = mock_generate_content.call_args_list[1].kwargs
        self.assertIn("TradeRecommendation", str(second_call_kwargs['contents']))
        self.assertIn("RSI is low", str(second_call_kwargs['contents']))

        # Third call is from DeepTraderManager to Trader, containing the order
        third_call_kwargs = mock_generate_content.call_args_list[2].kwargs
        self.assertIn("TradeOrder", str(third_call_kwargs['contents']))
        self.assertIn("Risk-adjusted", str(third_call_kwargs['contents']))

        # Fourth call is from Trader to DeepTraderManager, containing the result
        fourth_call_kwargs = mock_generate_content.call_args_list[3].kwargs
        self.assertIn("TradeResult", str(fourth_call_kwargs['contents']))
        self.assertIn("order-123", str(fourth_call_kwargs['contents']))

if __name__ == '__main__':
    unittest.main()
