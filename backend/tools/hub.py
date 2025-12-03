import os
from typing import Dict, Any

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class HubOverviewOutput(BaseModel):
    risk: Dict[str, Any] = Field(..., description="Global risk configuration.")
    trading: Dict[str, Any] = Field(..., description="Trading status information.")
    blacklist_entries: int = Field(..., description="Number of blacklist entries.")


def get_hub_overview() -> HubOverviewOutput:
    storage = _get_storage()
    risk = storage.get_state_value("risk", "global_parameters") or {}
    trading = storage.get_state_value("risk", "trading_status") or {"paused": False}
    blacklist = storage.get_state_value("blacklist", "entries") or []
    return HubOverviewOutput(risk=risk, trading=trading, blacklist_entries=len(blacklist))


hub_toolkit = Toolkit(name="hub")
hub_toolkit.register(get_hub_overview)
