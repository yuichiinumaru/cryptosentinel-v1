import os

import backend.compat  # noqa: F401  # Ensure Agno compatibility hooks are registered
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team
from agno.models.google import Gemini

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

load_dotenv()

def get_storage() -> Storage:
    storage_type = os.getenv("STORAGE_TYPE", "sqlite")
    storage_url = os.getenv("STORAGE_URL", "sqlite.db")
    if storage_type == "sqlite":
        return SqliteStorage(storage_url)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")

storage = get_storage()

class KeyManager:
    def __init__(self):
        self.api_keys = self._load_keys()
        if not self.api_keys:
            raise ValueError("No Gemini API keys found in .env file.")
        self.current_key_index = 0

    def _load_keys(self) -> list[str]:
        keys_str = os.getenv("gemini_api_keys")
        if keys_str:
            return [key.strip() for key in keys_str.split(',')]
        return []

    def get_key(self) -> str:
        return self.api_keys[self.current_key_index]

    def rotate_key(self) -> str:
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.get_key()

key_manager = KeyManager()

# Define the team with all 12 agents
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
    # The model for the team itself, if it needs to reason about routing.
    # We can use the shared_model from one of the agent files as a template.
    model=Gemini(
        id=os.getenv("gemini_model", "gemini-1.5-flash-latest"),
        api_key=key_manager.get_key(),
        temperature=float(os.getenv("temperature", 0.7)),
    )
)

# It seems the individual agent files define their own models.
# This is inefficient. It's better to have one shared model instance.
# However, for now, I will keep the structure as it is to avoid more refactoring.
# The `crypto_trading_team` model is just for the team's own reasoning.
