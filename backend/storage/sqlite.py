import sqlite3
import json
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from datetime import datetime

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


class SqliteStorage(Storage):
    def __init__(self, url: str):
        parsed_url = urlparse(url)
        # The path will be '/path/to/db.sqlite' for sqlite:///path/to/db.sqlite
        # or 'path/to/db.sqlite' for sqlite://path/to/db.sqlite
        # or ':memory:' for sqlite:///:memory:
        db_path = parsed_url.path
        if parsed_url.scheme == "sqlite" and db_path.startswith("/"):
            db_path = db_path[1:]

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = self._dict_factory
        self._create_tables()

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS teams (
                    name TEXT PRIMARY KEY,
                    team_id TEXT,
                    members TEXT,
                    description TEXT,
                    instructions TEXT
                );
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    name TEXT PRIMARY KEY,
                    id TEXT,
                    description TEXT,
                    steps TEXT
                );
                """
            )
            self.conn.execute(
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
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS activities (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    type TEXT,
                    message TEXT,
                    details TEXT
                );
                """
            )
            self.conn.execute(
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
                """
            )
            self.conn.execute(
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
                """
            )
            self.conn.execute(
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
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS state_store (
                    namespace TEXT,
                    key TEXT,
                    value TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (namespace, key)
                );
                """
            )

    def save_team(self, team: Team) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO teams (name, team_id, members, description, instructions)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (name) DO UPDATE
                SET team_id = excluded.team_id,
                    members = excluded.members,
                    description = excluded.description,
                    instructions = excluded.instructions;
                """,
                (
                    team.name,
                    team.team_id,
                    json.dumps(team.members),
                    team.description,
                    json.dumps(team.instructions),
                ),
            )

    def get_team(self, name: str) -> Optional[Team]:
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM teams WHERE name = ?;", (name,))
            data = cursor.fetchone()
            if data:
                data["members"] = json.loads(data["members"])
                data["instructions"] = json.loads(data["instructions"])
                return Team(**data)
            return None

    def delete_team(self, name: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM teams WHERE name = ?;", (name,))

    def save_workflow(self, workflow: Workflow) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO workflows (name, id, description, steps)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (name) DO UPDATE
                SET id = excluded.id,
                    description = excluded.description,
                    steps = excluded.steps;
                """,
                (
                    workflow.name,
                    workflow.id,
                    workflow.description,
                    json.dumps(workflow.steps),
                ),
            )

    def get_workflow(self, name: str) -> Optional[Workflow]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM workflows WHERE name = ?;", (name,)
            )
            data = cursor.fetchone()
            if data:
                data["steps"] = json.loads(data["steps"])
                return Workflow(**data)
            return None

    def delete_workflow(self, name: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM workflows WHERE name = ?;", (name,))

    def get_all_workflows(self) -> List[Workflow]:
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM workflows;")
            data = cursor.fetchall()
            workflows = []
            for row in data:
                row["steps"] = json.loads(row["steps"])
                workflows.append(Workflow(**row))
            return workflows

    def add_trade(self, trade: TradeData) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO trades (id, token, action, amount, price, timestamp, profit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade.id,
                    trade.token,
                    trade.action,
                    trade.amount,
                    trade.price,
                    trade.timestamp.isoformat(),
                    trade.profit,
                    trade.status,
                ),
            )

    def get_recent_trades(self, limit: int) -> List[TradeData]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?;", (limit,)
            )
            data = cursor.fetchall()
            return [TradeData(**row) for row in data]

    def add_activity(self, activity: ActivityData) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO activities (id, timestamp, type, message, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    activity.id,
                    activity.timestamp.isoformat(),
                    activity.type,
                    activity.message,
                    json.dumps(activity.details),
                ),
            )

    def get_recent_activities(self, limit: int) -> List[ActivityData]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM activities ORDER BY timestamp DESC LIMIT ?;", (limit,)
            )
            data = cursor.fetchall()
            for row in data:
                row["details"] = json.loads(row["details"])
            return [ActivityData(**row) for row in data]

    def get_portfolio_positions(self) -> List[PortfolioPosition]:
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM portfolio_positions;")
            rows = cursor.fetchall()
            positions: List[PortfolioPosition] = []
            for row in rows:
                if row.get("updated_at"):
                    row["updated_at"] = datetime.fromisoformat(row["updated_at"])
                positions.append(PortfolioPosition(**row))
            return positions

    def upsert_portfolio_position(self, position: PortfolioPosition) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO portfolio_positions (
                    token_address,
                    symbol,
                    chain,
                    coingecko_id,
                    amount,
                    average_price,
                    last_price,
                    last_valuation_usd,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(token_address) DO UPDATE SET
                    symbol = excluded.symbol,
                    chain = excluded.chain,
                    coingecko_id = excluded.coingecko_id,
                    amount = excluded.amount,
                    average_price = excluded.average_price,
                    last_price = excluded.last_price,
                    last_valuation_usd = excluded.last_valuation_usd,
                    updated_at = excluded.updated_at;
                """,
                (
                    position.token_address.lower(),
                    position.symbol,
                    position.chain,
                    position.coingecko_id,
                    position.amount,
                    position.average_price,
                    position.last_price,
                    position.last_valuation_usd,
                    position.updated_at.isoformat(),
                ),
            )

    def record_alert(self, alert: AlertRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO alerts (
                    id,
                    timestamp,
                    recipient,
                    channel,
                    message,
                    status,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    recipient = excluded.recipient,
                    channel = excluded.channel,
                    message = excluded.message,
                    status = excluded.status,
                    metadata = excluded.metadata;
                """,
                (
                    alert.id,
                    alert.timestamp.isoformat(),
                    alert.recipient,
                    alert.channel,
                    alert.message,
                    alert.status,
                    json.dumps(alert.metadata),
                ),
            )

    def get_recent_alerts(self, limit: int) -> List[AlertRecord]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?;",
                (limit,),
            )
            rows = cursor.fetchall()
            alerts: List[AlertRecord] = []
            for row in rows:
                row["metadata"] = json.loads(row["metadata"]) if row["metadata"] else {}
                if row.get("timestamp"):
                    row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                alerts.append(AlertRecord(**row))
            return alerts

    def record_agent_message(self, message: AgentMessageRecord) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO agent_messages (
                    id,
                    timestamp,
                    sender,
                    recipient,
                    content,
                    status,
                    correlation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    sender = excluded.sender,
                    recipient = excluded.recipient,
                    content = excluded.content,
                    status = excluded.status,
                    correlation_id = excluded.correlation_id;
                """,
                (
                    message.id,
                    message.timestamp.isoformat(),
                    message.sender,
                    message.recipient,
                    json.dumps(message.content),
                    message.status,
                    message.correlation_id,
                ),
            )

    def get_recent_agent_messages(self, limit: int) -> List[AgentMessageRecord]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT * FROM agent_messages ORDER BY timestamp DESC LIMIT ?;",
                (limit,),
            )
            rows = cursor.fetchall()
            messages: List[AgentMessageRecord] = []
            for row in rows:
                row["content"] = json.loads(row["content"]) if row["content"] else {}
                if row.get("timestamp"):
                    row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                messages.append(AgentMessageRecord(**row))
            return messages

    def set_state_value(self, namespace: str, key: str, value: Dict[str, Any]) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO state_store (namespace, key, value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(namespace, key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at;
                """,
                (
                    namespace,
                    key,
                    json.dumps(value),
                    datetime.utcnow().isoformat(),
                ),
            )

    def get_state_value(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        with self.conn:
            cursor = self.conn.execute(
                "SELECT value FROM state_store WHERE namespace = ? AND key = ?;",
                (namespace, key),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return json.loads(row["value"])
