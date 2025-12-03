import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

from agno.tools.toolkit import Toolkit
from pydantic import BaseModel, Field

from backend.storage.sqlite import SqliteStorage
from backend.storage.models import ActivityData


def _get_storage() -> SqliteStorage:
    return SqliteStorage(os.getenv("STORAGE_URL", "sqlite.db"))


class BlacklistEntry(BaseModel):
    entry_type: str = Field(..., description="Type of entry (token or developer).")
    identifier: str = Field(..., description="Token address or developer wallet.")
    reason: str = Field(..., description="Reason for blacklisting.")
    added_at: datetime = Field(default_factory=datetime.utcnow)


class AddBlacklistInput(BaseModel):
    entry_type: str = Field(..., description="Entry type (token or developer).")
    identifier: str = Field(..., description="Identifier to blacklist.")
    reason: str = Field(..., description="Reason for blacklisting.")


class RemoveBlacklistInput(BaseModel):
    entry_type: str = Field(..., description="Entry type (token or developer).")
    identifier: str = Field(..., description="Identifier to remove.")


class ListBlacklistOutput(BaseModel):
    entries: List[Dict[str, Any]] = Field(..., description="Current blacklist entries.")


def _load_entries(storage: SqliteStorage) -> List[Dict[str, Any]]:
    return storage.get_state_value("blacklist", "entries") or []


def _persist_entries(storage: SqliteStorage, entries: List[Dict[str, Any]]) -> None:
    storage.set_state_value("blacklist", "entries", entries)


def add_to_blacklist(input: AddBlacklistInput) -> BlacklistEntry:
    storage = _get_storage()
    entries = _load_entries(storage)
    entry = BlacklistEntry(**input.dict())
    entries = [e for e in entries if not (e.get("entry_type") == entry.entry_type and e.get("identifier") == entry.identifier)]
    entries.append(entry.dict())
    _persist_entries(storage, entries)
    activity = ActivityData(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        type="blacklist_add",
        message=f"Added {entry.identifier} to {entry.entry_type} blacklist",
        details=entry.dict(),
    )
    storage.add_activity(activity)
    return entry


def remove_from_blacklist(input: RemoveBlacklistInput) -> bool:
    storage = _get_storage()
    entries = _load_entries(storage)
    updated = [e for e in entries if not (e.get("entry_type") == input.entry_type and e.get("identifier") == input.identifier)]
    _persist_entries(storage, updated)
    activity = ActivityData(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        type="blacklist_remove",
        message=f"Removed {input.identifier} from {input.entry_type} blacklist",
        details=input.dict(),
    )
    storage.add_activity(activity)
    return len(updated) != len(entries)


def list_blacklist(entry_type: str | None = None) -> ListBlacklistOutput:
    storage = _get_storage()
    entries = _load_entries(storage)
    if entry_type:
        entries = [e for e in entries if e.get("entry_type") == entry_type]
    return ListBlacklistOutput(entries=entries)


blacklist_toolkit = Toolkit(name="blacklist")
blacklist_toolkit.register(add_to_blacklist)
blacklist_toolkit.register(remove_from_blacklist)
blacklist_toolkit.register(list_blacklist)
