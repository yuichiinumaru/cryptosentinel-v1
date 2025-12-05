import os

import backend.compat  # noqa: F401  # Ensure Agno compatibility hooks are registered
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team

# Import all agent definitions
from backend.AnalistaDeSentimento.AnalistaDeSentimento import analista_de_sentimento
from backend.AnalistaFundamentalista.AnalistaFundamentalista import analista_fundamentalista
from backend.AssetManager.AssetManager import asset_manager
from backend.ComplianceOfficer.ComplianceOfficer import compliance_officer
from backend.DeepTraderManager.DeepTraderManager import deep_trader_manager
from backend.Dev.Dev import dev_agent
from backend.LearningCoordinator.LearningCoordinator import learning_coordinator
from backend.MarketAnalyst.MarketAnalyst import market_analyst
from backend.PortfolioManager.PortfolioManager import portfolio_manager
from backend.RiskAnalyst.RiskAnalyst import risk_analyst
from backend.StrategyAgent.StrategyAgent import strategy_agent
from backend.Trader.Trader import trader_agent

# Import storage and key manager for shared resources
from backend.storage.sqlite import SqliteStorage
from backend.storage.base import Storage
from backend.config import Config

load_dotenv()

# Singleton storage instance
_storage = None

def get_storage() -> Storage:
    """
    Returns the singleton storage instance.
    Initializes safely using SQLAlchemy pooling (configured with WAL in sqlite.py).
    """
    global _storage
    if _storage is None:
        storage_type = os.getenv("STORAGE_TYPE", "sqlite")
        storage_url = os.getenv("STORAGE_URL", "sqlite.db")
        if storage_type == "sqlite":
            _storage = SqliteStorage(storage_url)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    return _storage

# Initialize storage (lazy-ish, but accessible globally)
storage = get_storage()

def get_crypto_trading_team(session_id: str) -> Team:
    """
    Factory function to create a Team instance for a specific user session.
    Ensures isolation of conversation history and context.

    Args:
        session_id: Unique identifier for the user session (e.g. from API Key hash).
    """
    if not session_id:
        raise ValueError("Session ID is required to create a trading team.")

    # We recreate the team structure for each request/session.

    return Team(
        members=[
            deep_trader_manager,
            market_analyst,
            trader_agent,
            portfolio_manager,
            analista_fundamentalista,
            analista_de_sentimento,
            risk_analyst,
            strategy_agent,
            asset_manager,
            compliance_officer,
            learning_coordinator,
            dev_agent,
        ],
        name=f"CryptoSentinelTeam-{session_id}",
        session_id=session_id, # Scopes the memory in storage
        model=Config.get_model(),
        # storage=storage, # Removed as Team doesn't accept it directly or incompatible type
    )
