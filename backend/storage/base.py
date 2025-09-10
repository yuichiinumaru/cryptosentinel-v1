from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Team, Workflow, TradeData, ActivityData


class Storage(ABC):
    """
    Abstract base class for storage implementations.
    """

    @abstractmethod
    def __init__(self, url: str):
        """
        Initializes the storage with a connection URL.
        """
        raise NotImplementedError

    @abstractmethod
    def save_team(self, team: "Team") -> None:
        """
        Saves a team to the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_team(self, name: str) -> Optional["Team"]:
        """
        Retrieves a team from the storage by name.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_team(self, name: str) -> None:
        """
        Deletes a team from the storage by name.
        """
        raise NotImplementedError

    @abstractmethod
    def save_workflow(self, workflow: "Workflow") -> None:
        """
        Saves a workflow to the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_workflow(self, name: str) -> Optional["Workflow"]:
        """
        Retrieves a workflow from the storage by name.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_workflow(self, name: str) -> None:
        """
        Deletes a workflow from the storage by name.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all_workflows(self) -> List["Workflow"]:
        """
        Retrieves all workflows from the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def add_trade(self, trade: "TradeData") -> None:
        """
        Saves a trade to the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_recent_trades(self, limit: int) -> List["TradeData"]:
        """
        Retrieves recent trades from the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def add_activity(self, activity: "ActivityData") -> None:
        """
        Saves an activity to the storage.
        """
        raise NotImplementedError

    @abstractmethod
    def get_recent_activities(self, limit: int) -> List["ActivityData"]:
        """
        Retrieves recent activities from the storage.
        """
        raise NotImplementedError
