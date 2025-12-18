import os
import logging
from typing import List

from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team

# Import Toolkits (Classes, not instances)
from backend.tools.dex import DexToolkit
from backend.tools.portfolio import portfolio_toolkit
from backend.agentspec.parser import AgentSpecParser
from backend.agentspec.enforcement import AgentSpecEnforcement
import backend.agentspec.predicates as predicates
import backend.agentspec.enforcement as enforcements
from agno.tools.toolkit import Toolkit
from functools import wraps
from backend.tools.market_data import market_data_toolkit
# from backend.tools.asset_management import asset_management_toolkit # To be fixed in Rite 3
from backend.tools.risk_management import risk_management_toolkit
from backend.tools.traffic_rules import TrafficRuleToolkit
from backend.khala_integration import KhalaMemoryToolkit

# Import storage and config
from backend.storage.sqlite import SqliteStorage
from backend.storage.base import Storage
from backend.config import Config
from backend.factory import create_agent
from backend.agents.researchers import get_bull_researcher, get_bear_researcher, get_debate_coordinator
from backend.tools.agentspec import create_agentspec_tool
from backend.agentspec.wrapper import apply_enforcement_to_toolkit

load_dotenv()
logger = logging.getLogger(__name__)

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

# Initialize storage
storage = get_storage()

def get_crypto_trading_team(session_id: str) -> Team:
    """
    Factory function to create a Team instance for a specific user session.
    Ensures isolation of conversation history and context by creating NEW Agent instances.

    Args:
        session_id: Unique identifier for the user session.
    """
    if not session_id:
        raise ValueError("Session ID is required to create a trading team.")

    model = Config.get_model()

    # Define base path for instructions
    # Adjusted for package structure: backend/agents/__init__.py -> backend/
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # --- Instantiate Agents Freshly ---

    # 1. Deep Trader Manager (Leader)
    deep_trader_manager = create_agent(
        name="DeepTraderManager",
        role="Trading Team Leader",
        instructions_path=os.path.join(base_dir, "DeepTraderManager/instructions.md"),
        tools=[KhalaMemoryToolkit(), TrafficRuleToolkit()], # Manager delegates, doesn't use tools directly usually
        model_id=model.id
    )

    # 2. Market Analyst
    market_analyst = create_agent(
        name="MarketAnalyst",
        role="Market Analyst",
        instructions_path=os.path.join(base_dir, "MarketAnalyst/instructions.md"),
        tools=[market_data_toolkit, KhalaMemoryToolkit()],
        model_id=model.id
    )

    # --- AgentSpec Integration ---
    # 1. Define predicate and enforcement maps
    predicate_map = {
        "is_large_trade": predicates.is_large_trade,
    }
    enforcement_map = {
        "user_inspection": enforcements.user_inspection,
        "stop": enforcements.stop,
    }

    # 2. Load and parse rules
    dex_toolkit_instance = DexToolkit()
    agentspec_tool = None
    try:
        rules_path = os.path.join(os.path.dirname(__file__), '..', 'agentspec', 'rules.ags')
        with open(rules_path, 'r') as f:
            rule_string = f.read()

        parser = AgentSpecParser()
        parsed_rules = parser.parse(rule_string)

        enforcement_engine = AgentSpecEnforcement(parsed_rules, predicate_map, enforcement_map)

        # Wrap the toolkit with the enforcement engine
        dex_toolkit_instance = apply_enforcement_to_toolkit(dex_toolkit_instance, enforcement_engine)
        agentspec_tool = create_agentspec_tool(enforcement_engine)

    except FileNotFoundError:
        logger.warning("AgentSpec rules file not found. Skipping enforcement.")
    except Exception as e:
        logger.error(f"Error initializing AgentSpec, enforcement disabled: {e}")

    # 3. Trader
    trader_tools = [dex_toolkit_instance, portfolio_toolkit, KhalaMemoryToolkit()]
    if agentspec_tool:
        trader_tools.append(agentspec_tool)

    trader_agent = create_agent(
        name="Trader",
        role="Execution Trader",
        instructions_path=os.path.join(base_dir, "Trader/instructions.md"),
        tools=trader_tools,
        model_id=model.id
    )

    # 4. Risk Analyst
    risk_analyst = create_agent(
        name="RiskAnalyst",
        role="Risk Manager",
        instructions_path=os.path.join(base_dir, "RiskAnalyst/instructions.md"),
        tools=[risk_management_toolkit, KhalaMemoryToolkit()],
        model_id=model.id
    )

    # ... (Instantiate other agents similarly as needed) ...
    # For brevity in this resurrection, we focus on the core team.
    # To fully replicate the previous team, we would add all 12.

    # 5. Asset Manager (Placeholder for Rite 3 fix)
    # asset_manager = create_agent(...)

    # 6. Debate Team (Scavenged from TradingAgents)
    bull_researcher = get_bull_researcher(model, session_id)
    bear_researcher = get_bear_researcher(model, session_id)
    debate_coordinator = get_debate_coordinator(model, session_id)

    team = Team(
        members=[
            deep_trader_manager,
            market_analyst,
            trader_agent,
            risk_analyst,
            bull_researcher,
            bear_researcher,
            debate_coordinator,
        ],
        name=f"CryptoSentinelTeam-{session_id}",
        session_id=session_id,
        model=model,
    )

    return team
