# System Architecture

## Overview
CryptoSentinel is a multi-agent autonomous cryptocurrency trading system. It utilizes the **Agno** framework for agent orchestration and **FastAPI** for the backend interface. The system is designed to run persistently, reacting to market data and user inputs.

## High-Level Diagram

```mermaid
graph TD
    User[User / Frontend] -->|API Request| API[FastAPI (backend/main.py)]
    API -->|Chat/Command| Team[Agno Team (backend/agents.py)]

    subgraph "Agent Team"
        Manager[DeepTraderManager]
        Market[MarketAnalyst]
        Fund[AnalistaFundamentalista]
        Sent[AnalistaDeSentimento]
        Risk[RiskAnalyst]
        Trader[TraderAgent]
        Learner[LearningCoordinator]
        Dev[DevAgent]
        Comp[ComplianceOfficer]
    end

    Team --> Manager
    Manager -->|Delegates| Market
    Manager -->|Delegates| Fund
    Manager -->|Delegates| Sent
    Manager -->|Consults| Risk
    Manager -->|Orders| Trader

    subgraph "External Services"
        Memory[Khala Agent Memory (SurrealDB)]
        Search[DuckDuckGo]
        CryptoData[CoinGecko / DexTools]
    end

    Market --> Search
    Market --> CryptoData
    Fund --> Search
    Sent --> Search
    Trader -->|Executes| CryptoData

    Learner -->|Reflects| Memory
    Manager -->|Queries| Memory
```

## Component Details

### 1. Backend (`backend/`)
*   **Entry Point:** `main.py` - Initializes FastAPI app and defines endpoints.
*   **Agent Definitions:** `agents.py` - Instantiates all agents and the `Team`.
*   **Agent Implementations:** Each agent has its own directory (e.g., `backend/MarketAnalyst/`) containing:
    *   `MarketAnalyst.py`: Agent instantiation.
    *   `instructions.md`: System prompt.
*   **Tools:** `backend/tools/` - Library of tools (functions) available to agents.
*   **Memory:** `khala_integration.py` - Interface to `khala-agentmemory`.

### 2. Frontend (`src/`)
*   React/Vite application that interacts with the FastAPI backend.
*   Displays chat interface, charts, and agent activities.

### 3. Data Flow
1.  **User Request:** User asks "Should I buy BTC?".
2.  **Orchestration:** `DeepTraderManager` receives the request.
3.  **Analysis:** Manager calls `MarketAnalyst` (Price/Tech) and `AnalistaDeSentimento` (News).
4.  **Decision:** Manager synthesizes info. (Currently lacks a formal debate step).
5.  **Execution:** If a trade is decided, `Trader` is invoked.
6.  **Response:** Final answer sent back to API -> User.

## Current Limitations vs. TradingAgents
*   **Linear Flow:** Decisions are often linear (Ask -> Analyze -> Decide) rather than adversarial (Bull vs. Bear).
*   **Memory Usage:** Memory is available but not strictly enforced as a "Step 0" (Recall) and "Step N+1" (Reflect) in every loop.
*   **Data Sources:** Reliance on basic CoinGecko/DDG data; could benefit from deeper fundamental data.
