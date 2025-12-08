# Tasklist: Resurrection & Purification

## Phase 1: Structural Repairs (Critical)

### 1.1 Architecture & State
- [ ] **Fix Global Agent State (`backend/agents.py`)**
    - Refactor `get_crypto_trading_team` to instantiate `Agent` objects inside the function, not import global instances.
    - Ensure `Team` receives a unique session ID.
- [ ] **Fix Asset Management (`backend/tools/asset_management.py`)**
    - Delete the overwriting `AssetManagementToolkit` class at the bottom of the file.
    - Ensure the functional class/methods are properly registered.

### 1.2 Performance & Async
- [ ] **Fix Blocking DEX Calls (`backend/tools/dex.py`)**
    - Replace `WalletManager` per-call instantiation with a Singleton/Pool.
    - Replace `w3.eth.wait_for_transaction_receipt` with an async polling loop or background task.
    - Fix Native Token handling (Sentinel check).
- [ ] **Fix Market Data Loops (`backend/tools/market_data.py`)**
    - Refactor `fetch_market_data` to use `asyncio.gather` for parallel requests.

### 1.3 Security Hardening
- [ ] **Fix Hardcoded Secrets (`backend/main.py`)**
    - Raise `RuntimeError` if `API_KEY` is default.
    - Remove hardcoded Logging Level.
- [ ] **Fix Frontend Mockery (`src/components/WalletConnection.tsx`)**
    - (Low Priority) Mark as "UI Only" or implement `wagmi`.

## Phase 2: Intelligent Agents (TradingAgents Integration)

### 2.1 Adversarial Debate
- [ ] **Implement Researchers (`backend/agents/researchers.py`)**
    - [Scavenger] Port `BullResearcher` prompt and logic from `TradingAgents`.
    - [Scavenger] Port `BearResearcher` prompt and logic from `TradingAgents`.
- [ ] **Implement Debators (`backend/agents/debators.py`)**
    - [Scavenger] Port `RiskDebator` (Conservative/Aggressive) logic from `TradingAgents`.
- [ ] **Implement Debate Coordinator (`backend/agents/coordinator.py`)**
    - Create a workflow (Thesis -> Antithesis -> Synthesis) using Agno.

### 2.2 Memory Integration
- [ ] **Upgrade Khala Toolkit**
    - Implement `store_market_situation` in `backend/khala_integration.py`.

## Phase 3: Quantitative Analysis (AgentQuant, StockPredictionAI, SquareQuant)

### 3.1 Regime Detection
- [ ] **Implement `MarketRegimeToolkit` (`backend/tools/regime.py`)**
    - [Scavenger] Port `RegimeDetection` logic (VIX/Momentum) from `AgentQuant`.
    - Create tool `detect_market_regime(symbol)`.

### 3.2 Technical Tools
- [ ] **Implement `TechnicalAnalysisToolkit` (`backend/tools/technical_analysis.py`)**
    - [Scavenger] Port `get_technical_indicators` from `stockpredictionai` / `ai-hedge-fund-crypto`.
- [ ] **Implement `MarketCorrelationToolkit` (`backend/tools/market_correlation.py`)**
    - Create tools to fetch BTC/ETH trends as context.

### 3.3 Quantitative Metrics
- [ ] **Implement `QuantitativeAnalysisToolkit` (`backend/tools/quant_metrics.py`)**
    - [Scavenger] Port `Sharpe`, `Sortino`, `Calmar` logic from `SquareQuant`.
    - [Scavenger] Port `ValueAtRisk` (VaR) logic from `SquareQuant`.
- [ ] **Implement `FourierToolkit` (`backend/tools/math_tools.py`)**
    - [Scavenger] Implement FFT-based trend extraction from `stockpredictionai`.

## Phase 4: Security & Optimization (AI Memecoin Bot)

### 4.1 Zero Trust Security
- [ ] **Implement `SecurityToolkit` (`backend/tools/security.py`)**
    - [Scavenger] Port "Honeypot Detection" logic (Renounced, Liquidity Locked) from `ai-memecoin-trading-bot` (Go -> Python).
    - Implement `calculate_safety_score`.
