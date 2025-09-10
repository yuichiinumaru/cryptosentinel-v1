# Backend Architecture

## Folder Organization

The backend code is organized into the following structure:

- `backend/`: The root directory for the backend code.
    - `main.py`: The main entry point for the FastAPI application.
    - `agents.py`: Contains the `get_storage` function and the `KeyManager` class.
    - `protocol.py`: Defines the Pydantic schemas for the messages exchanged between agents.
    - `storage/`: Contains the storage layer for data persistence.
        - `base.py`: Defines the abstract `Storage` class.
        - `models.py`: Defines the Pydantic models for the data.
        - `sqlite.py`: Implements the `SqliteStorage` class.
    - `tools/`: Contains the implementation of the tools used by the agents.
    - `MarketAnalyst/`, `Trader/`, etc.: Each agent has its own directory containing:
        - `[AgentName].py`: The implementation of the agent.
        - `instructions.md`: The instructions for the agent.
        - `files/`: A directory for files used by the agent.
        - `schemas/`: A directory for schemas used by the agent.
    - `tests/`: Contains the tests for the agents and tools.

## Main Files and Functions

- **`main.py`**:
    - Initializes the FastAPI application.
    - Initializes the `Agency` with all the agents.
    - Defines the API endpoints for interacting with the system.
- **`agents.py`**:
    - `get_storage()`: Returns a storage instance based on environment variables.
    - `KeyManager`: Manages the API keys for the language models.
- **`protocol.py`**:
    - Defines the Pydantic models for all the messages exchanged between agents, such as `TradeRecommendation`, `TradeApprovalResponse`, etc.

## Connections

- The agents are connected through the `Agency` class from the `agno` library.
- The agents communicate with each other by sending messages that conform to the schemas defined in `protocol.py`.
- The agents use the tools defined in the `tools/` directory to interact with the outside world (e.g., fetch market data, execute trades).
- The storage layer is used by the agents to persist data.

## Data Flow

The data flow in the system is as follows:

1.  The `MarketAnalyst` agent scans the market and identifies a trading opportunity.
2.  The `MarketAnalyst` sends a `TradeRecommendation` message to the `DeepTraderManager`.
3.  The `DeepTraderManager` receives the recommendation and decides whether to approve or reject it.
4.  If the trade is approved, the `DeepTraderManager` sends a `TradeApprovalResponse` message to the `Trader`.
5.  The `Trader` receives the approval and executes the trade using the appropriate tools.
6.  After executing the trade, the `Trader` sends a `PortfolioUpdate` message to the `PortfolioManager`.
7.  The `PortfolioManager` updates the portfolio in the database.
