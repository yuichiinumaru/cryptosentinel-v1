import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Row

from .base import Storage
from .models import (
    Team,
    Workflow,
    TradeData,
    ActivityData,
    PortfolioPosition,
    AlertRecord,
    AgentMessageRecord,
)

logger = logging.getLogger(__name__)

class SqliteStorage(Storage):
    """
    Thread-safe SQLite storage implementation using SQLAlchemy connection pooling.
    Resurrected from the corrupt original.
    """

    def __init__(self, url: str):
        # Normalize URL
        if not url.startswith("sqlite"):
            # Handle local file paths
            if "://" not in url:
                url = f"sqlite:///{url}"
            else:
                 # Assume it's a valid url
                 pass

        # Check_same_thread=False is necessary for SQLite when using a pool across threads,
        # provided we handle the connections properly (which QueuePool/Engine does).
        self.engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            connect_args={"check_same_thread": False}
        )
        self._create_tables()

    def _create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS teams (
                name TEXT PRIMARY KEY,
                team_id TEXT,
                members TEXT,
                description TEXT,
                instructions TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS workflows (
                name TEXT PRIMARY KEY,
                id TEXT,
                description TEXT,
                steps TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                token TEXT,
                action TEXT,
                amount REAL,
                price REAL,
                timestamp TEXT,
                profit REAL,
                status TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                type TEXT,
                message TEXT,
                details TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                token_address TEXT PRIMARY KEY,
                symbol TEXT,
                chain TEXT,
                coingecko_id TEXT,
                amount REAL,
                average_price REAL,
                last_price REAL,
                last_valuation_usd REAL,
                updated_at TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                recipient TEXT,
                channel TEXT,
                message TEXT,
                status TEXT,
                metadata TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS agent_messages (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                sender TEXT,
                recipient TEXT,
                content TEXT,
                status TEXT,
                correlation_id TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS state_store (
                namespace TEXT,
                key TEXT,
                value TEXT,
                updated_at TEXT,
                PRIMARY KEY (namespace, key)
            );
            """
        ]
        with self.engine.connect() as conn:
            for q in queries:
                conn.execute(text(q))
            conn.commit()

    def _row_to_dict(self, row: Row) -> Dict[str, Any]:
        """Convert SQLAlchemy Row to dict."""
        return dict(row._mapping)

    def save_team(self, team: Team) -> None:
        query = """
        INSERT INTO teams (name, team_id, members, description, instructions)
        VALUES (:name, :team_id, :members, :description, :instructions)
        ON CONFLICT (name) DO UPDATE
        SET team_id = excluded.team_id,
            members = excluded.members,
            description = excluded.description,
            instructions = excluded.instructions;
        """
        params = {
            "name": team.name,
            "team_id": team.team_id,
            "members": json.dumps(team.members),
            "description": team.description,
            "instructions": json.dumps(team.instructions),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_team(self, name: str) -> Optional[Team]:
        query = "SELECT * FROM teams WHERE name = :name;"
        with self.engine.connect() as conn:
            result = conn.execute(text(query), {"name": name}).fetchone()
            if result:
                data = self._row_to_dict(result)
                data["members"] = json.loads(data["members"])
                data["instructions"] = json.loads(data["instructions"])
                return Team(**data)
            return None

    def delete_team(self, name: str) -> None:
        query = "DELETE FROM teams WHERE name = :name;"
        with self.engine.connect() as conn:
            conn.execute(text(query), {"name": name})
            conn.commit()

    def save_workflow(self, workflow: Workflow) -> None:
        query = """
        INSERT INTO workflows (name, id, description, steps)
        VALUES (:name, :id, :description, :steps)
        ON CONFLICT (name) DO UPDATE
        SET id = excluded.id,
            description = excluded.description,
            steps = excluded.steps;
        """
        params = {
            "name": workflow.name,
            "id": workflow.id,
            "description": workflow.description,
            "steps": json.dumps(workflow.steps),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_workflow(self, name: str) -> Optional[Workflow]:
        query = "SELECT * FROM workflows WHERE name = :name;"
        with self.engine.connect() as conn:
            result = conn.execute(text(query), {"name": name}).fetchone()
            if result:
                data = self._row_to_dict(result)
                data["steps"] = json.loads(data["steps"])
                return Workflow(**data)
            return None

    def delete_workflow(self, name: str) -> None:
        query = "DELETE FROM workflows WHERE name = :name;"
        with self.engine.connect() as conn:
            conn.execute(text(query), {"name": name})
            conn.commit()

    def get_all_workflows(self) -> List[Workflow]:
        query = "SELECT * FROM workflows;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query)).fetchall()
            workflows = []
            for row in results:
                data = self._row_to_dict(row)
                data["steps"] = json.loads(data["steps"])
                workflows.append(Workflow(**data))
            return workflows

    def add_trade(self, trade: TradeData) -> None:
        query = """
        INSERT INTO trades (id, token, action, amount, price, timestamp, profit, status)
        VALUES (:id, :token, :action, :amount, :price, :timestamp, :profit, :status)
        """
        params = {
            "id": trade.id,
            "token": trade.token,
            "action": trade.action,
            "amount": float(trade.amount), # CAST DECIMAL TO FLOAT
            "price": float(trade.price),
            "timestamp": trade.timestamp.isoformat(),
            "profit": float(trade.profit) if trade.profit is not None else 0.0,
            "status": trade.status,
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_recent_trades(self, limit: int) -> List[TradeData]:
        query = "SELECT * FROM trades ORDER BY timestamp DESC LIMIT :limit;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query), {"limit": limit}).fetchall()
            return [TradeData(**self._row_to_dict(row)) for row in results]

    def add_activity(self, activity: ActivityData) -> None:
        query = """
        INSERT INTO activities (id, timestamp, type, message, details)
        VALUES (:id, :timestamp, :type, :message, :details)
        """
        params = {
            "id": activity.id,
            "timestamp": activity.timestamp.isoformat(),
            "type": activity.type,
            "message": activity.message,
            "details": json.dumps(activity.details),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_recent_activities(self, limit: int) -> List[ActivityData]:
        query = "SELECT * FROM activities ORDER BY timestamp DESC LIMIT :limit;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query), {"limit": limit}).fetchall()
            activities = []
            for row in results:
                data = self._row_to_dict(row)
                data["details"] = json.loads(data["details"])
                activities.append(ActivityData(**data))
            return activities

    def get_portfolio_positions(self) -> List[PortfolioPosition]:
        query = "SELECT * FROM portfolio_positions;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query)).fetchall()
            positions = []
            for row in results:
                data = self._row_to_dict(row)
                if data.get("updated_at"):
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                positions.append(PortfolioPosition(**data))
            return positions

    def upsert_portfolio_position(self, position: PortfolioPosition) -> None:
        query = """
        INSERT INTO portfolio_positions (
            token_address, symbol, chain, coingecko_id, amount,
            average_price, last_price, last_valuation_usd, updated_at
        ) VALUES (
            :token_address, :symbol, :chain, :coingecko_id, :amount,
            :average_price, :last_price, :last_valuation_usd, :updated_at
        )
        ON CONFLICT(token_address) DO UPDATE SET
            symbol = excluded.symbol,
            chain = excluded.chain,
            coingecko_id = excluded.coingecko_id,
            amount = excluded.amount,
            average_price = excluded.average_price,
            last_price = excluded.last_price,
            last_valuation_usd = excluded.last_valuation_usd,
            updated_at = excluded.updated_at;
        """
        params = {
            "token_address": position.token_address.lower(),
            "symbol": position.symbol,
            "chain": position.chain,
            "coingecko_id": position.coingecko_id,
            "amount": float(position.amount),
            "average_price": float(position.average_price),
            "last_price": float(position.last_price) if position.last_price else None,
            "last_valuation_usd": float(position.last_valuation_usd) if position.last_valuation_usd else None,
            "updated_at": position.updated_at.isoformat(),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def record_alert(self, alert: AlertRecord) -> None:
        query = """
        INSERT INTO alerts (id, timestamp, recipient, channel, message, status, metadata)
        VALUES (:id, :timestamp, :recipient, :channel, :message, :status, :metadata)
        ON CONFLICT(id) DO UPDATE SET
            timestamp = excluded.timestamp,
            recipient = excluded.recipient,
            channel = excluded.channel,
            message = excluded.message,
            status = excluded.status,
            metadata = excluded.metadata;
        """
        params = {
            "id": alert.id,
            "timestamp": alert.timestamp.isoformat(),
            "recipient": alert.recipient,
            "channel": alert.channel,
            "message": alert.message,
            "status": alert.status,
            "metadata": json.dumps(alert.metadata),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_recent_alerts(self, limit: int) -> List[AlertRecord]:
        query = "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT :limit;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query), {"limit": limit}).fetchall()
            alerts = []
            for row in results:
                data = self._row_to_dict(row)
                data["metadata"] = json.loads(data["metadata"]) if data["metadata"] else {}
                if data.get("timestamp"):
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                alerts.append(AlertRecord(**data))
            return alerts

    def record_agent_message(self, message: AgentMessageRecord) -> None:
        query = """
        INSERT INTO agent_messages (id, timestamp, sender, recipient, content, status, correlation_id)
        VALUES (:id, :timestamp, :sender, :recipient, :content, :status, :correlation_id)
        ON CONFLICT(id) DO UPDATE SET
            timestamp = excluded.timestamp,
            sender = excluded.sender,
            recipient = excluded.recipient,
            content = excluded.content,
            status = excluded.status,
            correlation_id = excluded.correlation_id;
        """
        params = {
            "id": message.id,
            "timestamp": message.timestamp.isoformat(),
            "sender": message.sender,
            "recipient": message.recipient,
            "content": json.dumps(message.content),
            "status": message.status,
            "correlation_id": message.correlation_id,
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_recent_agent_messages(self, limit: int) -> List[AgentMessageRecord]:
        query = "SELECT * FROM agent_messages ORDER BY timestamp DESC LIMIT :limit;"
        with self.engine.connect() as conn:
            results = conn.execute(text(query), {"limit": limit}).fetchall()
            messages = []
            for row in results:
                data = self._row_to_dict(row)
                data["content"] = json.loads(data["content"]) if data["content"] else {}
                if data.get("timestamp"):
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                messages.append(AgentMessageRecord(**data))
            return messages

    def set_state_value(self, namespace: str, key: str, value: Dict[str, Any]) -> None:
        query = """
        INSERT INTO state_store (namespace, key, value, updated_at)
        VALUES (:namespace, :key, :value, :updated_at)
        ON CONFLICT(namespace, key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at;
        """
        params = {
            "namespace": namespace,
            "key": key,
            "value": json.dumps(value),
            "updated_at": datetime.utcnow().isoformat(),
        }
        with self.engine.connect() as conn:
            conn.execute(text(query), params)
            conn.commit()

    def get_state_value(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        query = "SELECT value FROM state_store WHERE namespace = :namespace AND key = :key;"
        with self.engine.connect() as conn:
            result = conn.execute(text(query), {"namespace": namespace, "key": key}).fetchone()
            if not result:
                return None
            return json.loads(result[0])
