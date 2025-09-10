import sqlite3
import json
from typing import List, Optional

from .base import Storage
from .models import Team, Workflow, TradeData, ActivityData


class SqliteStorage(Storage):
    def __init__(self, url: str):
        self.conn = sqlite3.connect(url)
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
