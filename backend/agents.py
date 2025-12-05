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
    Initializes safely using SQLAlchemy pooling.
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

# Define the team with all 12 agents
# We use a singleton team for now to maintain conversation state if held in-memory.
# In a robust system, state should be externalized (DB) and Team re-created per request/session.
crypto_trading_team = Team(
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
    name="CryptoSentinelTeam",
    model=Config.get_model(), # Use the safe Config
)
