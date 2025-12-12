# Tasklist: Resurrection & Purification

## Phase 1: Structural Repairs (Critical)

### 1.1 Architecture & State
- [x] **Fix Global Agent State (`backend/agents/__init__.py`)**
    - [x] Refactor `get_crypto_trading_team` to instantiate `Agent` objects inside the function, not import global instances.
    - [x] Ensure `Team` receives a unique session ID.
- [x] **Fix Asset Management (`backend/tools/asset_management.py`)**
    - [x] Delete the overwriting `AssetManagementToolkit` class at the bottom of the file.
    - [x] Ensure the functional class/methods are properly registered.

### 1.2 Performance & Async
- [x] **Fix Blocking DEX Calls (`backend/tools/dex.py`)**
    - [x] Replace `WalletManager` per-call instantiation with a Singleton/Pool.
    - [x] Replace `w3.eth.wait_for_transaction_receipt` with an async polling loop or background task.
    - [x] Fix Native Token handling (Sentinel check).
- [x] **Fix Market Data Loops (`backend/tools/market_data.py`)**
    - [x] Refactor `fetch_market_data` to use `asyncio.gather` for parallel requests.

### 1.3 Security Hardening
- [x] **Fix Hardcoded Secrets (`backend/main.py`)**
    - [x] Raise `RuntimeError` if `API_KEY` is default.
    - [x] Remove hardcoded Logging Level.
- [ ] **Fix Frontend Mockery (`src/components/WalletConnection.tsx`)**
    - [ ] (Low Priority) Mark as "UI Only" or implement `wagmi`.

## Phase 2: Intelligent Agents (TradingAgents Integration)

### 2.1 Adversarial Debate
- [x] **Implement Researchers (`backend/agents/researchers.py`)**
    - [x] [Scavenger] Port `BullResearcher` prompt and logic from `TradingAgents`.
    - [x] [Scavenger] Port `BearResearcher` prompt and logic from `TradingAgents`.
- [x] **Implement Debators (`backend/agents/debators.py`)**
    - [x] [Scavenger] Port `RiskDebator` (Conservative/Aggressive) logic from `TradingAgents`.
- [x] **Implement Debate Coordinator (`backend/agents/coordinator.py`)**
    - [x] Create a workflow (Thesis -> Antithesis -> Synthesis) using Agno.

### 2.2 Memory Integration
- [x] **Upgrade Khala Toolkit**
    - [x] Implement `store_market_situation` in `backend/khala_integration.py`.

## Phase 3: Quantitative Analysis (AgentQuant, StockPredictionAI, SquareQuant)

### 3.1 Regime Detection
- [x] **Implement `MarketRegimeToolkit` (`backend/tools/regime.py`)**
    - [x] [Scavenger] Port `RegimeDetection` logic (VIX/Momentum) from `AgentQuant`.
    - [x] Create tool `detect_market_regime(symbol)`.

### 3.2 Technical Tools
- [x] **Implement `TechnicalAnalysisToolkit` (`backend/tools/technical_analysis.py`)**
    - [x] [Scavenger] Port `get_technical_indicators` from `stockpredictionai` / `ai-hedge-fund-crypto`.
- [x] **Implement `MarketCorrelationToolkit` (`backend/tools/market_correlation.py`)**
    - [x] Create tools to fetch BTC/ETH trends as context.

### 3.3 Quantitative Metrics
- [x] **Implement `QuantitativeAnalysisToolkit` (`backend/tools/quant_metrics.py`)**
    - [x] [Scavenger] Port `Sharpe`, `Sortino`, `Calmar` logic from `SquareQuant`.
    - [x] [Scavenger] Port `ValueAtRisk` (VaR) logic from `SquareQuant`.
- [x] **Implement `FourierToolkit` (`backend/tools/math_tools.py`)**
    - [x] [Scavenger] Implement FFT-based trend extraction from `stockpredictionai`.

## Phase 3.5: The Harvest Integration (Multi-Repo Scavenger Hunt)

### 3.5.1 The Champions Integration
- [ ] **Refactor `QuantitativeAnalysisToolkit` (Metrics Champion: `ffn`)**
    - [ ] Enhance metrics with `ffn`-style vectorized calcs (Drawdown, Sortino).
    - [ ] Ensure functions are clean and decoupled.
- [ ] **Implement `OptionsMathToolkit` (Math Champion: `vollib`)**
    - [ ] Create `backend/tools/options_math.py`.
    - [ ] Implement Black-Scholes and Greeks using `vollib` (or rational approximation logic).
- [ ] **Standardize Technical Analysis (TA Champion: `pandas-ta`)**
    - [ ] Verify `backend/tools/technical_analysis.py` uses `pandas-ta` core logic.
    - [ ] Ensure consistent indicator naming conventions (as per OpenBB standard).
- [ ] **Market Data Provider Pattern (Architecture Champion: `OpenBB`)**
    - [ ] (Refactor) Ensure `MarketDataToolkit` separates "Source" from "Logic" (Interface pattern).

## Phase 4: Security & Optimization (AI Memecoin Bot)

### 4.1 Zero Trust Security
- [x] **Implement `SecurityToolkit` (`backend/tools/security.py`)**
    - [x] [Scavenger] Port "Honeypot Detection" logic (Renounced, Liquidity Locked) from `ai-memecoin-trading-bot` (Go -> Python).
    - [x] Implement `calculate_safety_score`.

### 4.2 Advanced Security
- [ ] **MEV Protection**
    - [ ] Integrate Flashbots.
- [ ] **Pre-Trade Simulation**
    - [ ] Implement simulation via Tenderly/Fork.

## Phase 5: Productization (The Final Mile)

### 5.1 Automation
- [ ] **Implement Scheduler (`backend/scheduler.py`)**
    - [ ] Run `DebateCoordinator` loop every X minutes.
    - [ ] Persist outcomes to `ActivityData` table.

### 5.2 Paper Trading
- [ ] **Implement `PaperTradingService` (`backend/services/paper_trading.py`)**
    - [ ] Create `PortfolioLedger` table.
    - [ ] Execute virtual trades based on Coordinator signals.

### 5.3 Frontend
- [ ] **Visualize Debate (`src/components/DebateView.tsx`)**
    - [ ] Show Bull vs Bear cards.
- [ ] **Visualize Regime (`src/components/RegimeIndicator.tsx`)**
    - [ ] Show "Bull/Bear" status.
