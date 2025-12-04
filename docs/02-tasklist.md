# Tasklist: Implementation of TradingAgents Enhancements

## Phase 1: Foundation & Memory (Plan B)

### 1.1. Upgrade Memory Toolkit
- [ ] **Task:** Update `backend/khala_integration.py` to support vector search or structured tagging for "Situations".
    - *Subtask:* Check if `SurrealDBClient` has `search_vectors`. If not, implement a workaround using tagged collections.
    - *Subtask:* Add `store_market_situation` and `retrieve_similar_situations` methods to `KhalaMemoryToolkit`.
    - *Test:* `tests/test_memory_integration.py` (Mocked DB).

### 1.2. Define Situation Schema
- [ ] **Task:** Create `backend/storage/schemas.py` (or update `models.py`).
    - *Subtask:* Define Pydantic model `MarketSituation` (timestamp, ticker, indicators_snapshot, news_summary, decision, outcome).

## Phase 2: Enhanced Prompts (Plan C)

### 2.1. Refactor Market Analyst
- [ ] **Task:** Update `backend/MarketAnalyst/instructions.md`.
    - *Source:* Adapt from `reference/TradingAgents/tradingagents/agents/analysts/market_analyst.py`.
    - *Action:* Expand current prompt to include technical analysis specifics (MACD, RSI requirements).

### 2.2. Refactor Fundamental Analyst
- [ ] **Task:** Update `backend/AnalistaFundamentalista/instructions.md`.
    - *Source:* Adapt from `reference/TradingAgents/tradingagents/agents/analysts/fundamentals_analyst.py`.
    - *Action:* Focus on "Growth," "Financial Health," and "Management" sections.

### 2.3. Refactor Sentiment Analyst
- [ ] **Task:** Update `backend/AnalistaDeSentimento/instructions.md`.
    - *Source:* Adapt from `reference/TradingAgents/tradingagents/agents/analysts/social_media_analyst.py`.

## Phase 3: Adversarial Debate (Plan A)

### 3.1. Create Researchers
- [ ] **Task:** Create `backend/BullResearcher/` and `backend/BearResearcher/`.
    - *Subtask:* Create `BullResearcher.py` and `instructions.md`.
    - *Source:* Copy prompt logic from `reference/TradingAgents/tradingagents/agents/researchers/bull_researcher.py`.
    - *Subtask:* Create `BearResearcher.py` and `instructions.md`.
    - *Source:* Copy prompt logic from `reference/TradingAgents/tradingagents/agents/researchers/bear_researcher.py`.

### 3.2. Implement Debate Workflow
- [ ] **Task:** Update `backend/DeepTraderManager/DeepTraderManager.py` (or create a new `DebateCoordinator.py`).
    - *Subtask:* Implement a function `conduct_debate(ticker, data)` that:
        1. Calls Bull Agent with data.
        2. Calls Bear Agent with data.
        3. Calls Bull Agent with Bear's response (Rebuttal).
        4. Calls Bear Agent with Bull's response (Rebuttal).
    - *Test:* `tests/test_debate_flow.py`.

## Phase 4: Reflection Loop (Plan D)

### 4.1. Activate Learning Coordinator
- [ ] **Task:** Update `backend/LearningCoordinator/LearningCoordinator.py`.
    - *Action:* Ensure it has tools to *read* past trades (`backend/storage/sqlite.py`) and *write* to `KhalaMemoryToolkit`.
    - *Prompt:* Adapt reflection logic from `reference/TradingAgents/tradingagents/graph/reflection.py`.

### 4.2. Hook into Main Loop
- [ ] **Task:** Modify `backend/main.py` (Chat endpoint) or the background scheduler.
    - *Action:* When a trade is finalized (or queried), trigger an async task for `LearningCoordinator` to review it.
