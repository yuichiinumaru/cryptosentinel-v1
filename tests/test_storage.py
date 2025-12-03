import unittest
import os
from datetime import datetime, timezone
import json

from backend.storage.sqlite import SqliteStorage
from backend.storage.models import (
    TradeData,
    ActivityData,
    PortfolioPosition,
    AlertRecord,
    AgentMessageRecord,
)

class TestSqliteStorage(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database for testing."""
        self.db_path = "test_storage.db"
        # Ensure the old db file is removed before each test
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.storage = SqliteStorage(f"sqlite:///{self.db_path}")

    def tearDown(self):
        """Remove the temporary database after tests."""
        # The connection is held by the instance, so we can just remove the file.
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_and_get_recent_trades(self):
        """Test adding trades and retrieving the most recent ones."""
        # The model in sqlite.py has different fields than the one in my original test
        # I need to adjust the test data to match the schema in sqlite.py
        # trades table: id, token, action, amount, price, timestamp, profit, status

        trade1 = TradeData(
            id="trade1",
            token="BTC",
            action="buy",
            amount=0.1,
            price=50000.0,
            timestamp=datetime.now(timezone.utc),
            profit=0,
            status="completed"
        )
        trade2 = TradeData(
            id="trade2",
            token="ETH",
            action="sell",
            amount=2.0,
            price=3000.0,
            timestamp=datetime.now(timezone.utc),
            profit=100.0,
            status="completed"
        )

        self.storage.add_trade(trade1)
        self.storage.add_trade(trade2)

        recent_trades = self.storage.get_recent_trades(limit=1)
        self.assertEqual(len(recent_trades), 1)
        # The most recent trade should be trade2
        self.assertEqual(recent_trades[0].id, "trade2")
        self.assertEqual(recent_trades[0].token, "ETH")

        all_trades = self.storage.get_recent_trades(limit=10)
        self.assertEqual(len(all_trades), 2)

    def test_add_and_get_recent_activities(self):
        """Test adding activities and retrieving the most recent ones."""
        # activities table: id, timestamp, type, message, details

        activity1 = ActivityData(
            id="activity1",
            timestamp=datetime.now(timezone.utc),
            type="MarketAnalysis",
            message="BTC price is trending up.",
            details={"indicator": "RSI", "value": 72}
        )
        activity2 = ActivityData(
            id="activity2",
            timestamp=datetime.now(timezone.utc),
            type="TradeExecution",
            message="Executed buy order for BTC.",
            details={"order_id": "xyz-123", "quantity": 0.1}
        )

        self.storage.add_activity(activity1)
        self.storage.add_activity(activity2)

        recent_activities = self.storage.get_recent_activities(limit=1)
        self.assertEqual(len(recent_activities), 1)
        self.assertEqual(recent_activities[0].id, "activity2")
        # The details are stored as a JSON string, so they should be parsed back
        self.assertEqual(recent_activities[0].details["order_id"], "xyz-123")

        all_activities = self.storage.get_recent_activities(limit=5)
        self.assertEqual(len(all_activities), 2)

    def test_portfolio_and_alert_records(self):
        position = PortfolioPosition(
            token_address="0xtoken",
            symbol="TEST",
            chain="ethereum",
            coingecko_id="test-token",
            amount=10.0,
            average_price=2.0,
            last_price=2.5,
            last_valuation_usd=25.0,
            updated_at=datetime.now(timezone.utc),
        )
        self.storage.upsert_portfolio_position(position)
        positions = self.storage.get_portfolio_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].symbol, "TEST")

        alert = AlertRecord(
            id="alert1",
            timestamp=datetime.now(timezone.utc),
            recipient="ops",
            channel="internal",
            message="Test alert",
            status="delivered",
            metadata={"foo": "bar"},
        )
        self.storage.record_alert(alert)
        alerts = self.storage.get_recent_alerts(limit=5)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].message, "Test alert")

    def test_agent_messages_and_state_store(self):
        message = AgentMessageRecord(
            id="msg1",
            timestamp=datetime.now(timezone.utc),
            sender="manager",
            recipient="trader",
            content={"text": "Hello"},
            status="sent",
            correlation_id="trade-1",
        )
        self.storage.record_agent_message(message)
        messages = self.storage.get_recent_agent_messages(limit=5)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender, "manager")

        self.storage.set_state_value("test", "key", {"value": 42})
        state_value = self.storage.get_state_value("test", "key")
        self.assertEqual(state_value["value"], 42)


if __name__ == '__main__':
    unittest.main()
