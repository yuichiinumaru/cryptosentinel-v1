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

## Phase 2: Feature Restoration

### 2.1 Memory Integration
- [ ] **Upgrade Khala Toolkit**
    - Implement `store_market_situation` in `backend/khala_integration.py`.

### 2.2 Trading Logic
- [ ] **Implement Adversarial Debate**
    - Create `DebateCoordinator` agent.

## Phase 3: Quantitative Analysis (StockPredictionAI)

### 3.1 Technical Tools
- [ ] **Implement `TechnicalAnalysisToolkit` (`backend/tools/technical_analysis.py`)**
    - Port logic from reference: `get_technical_indicators` (MA, MACD, Bollinger, Momentum).
    - Ensure methods return structured data for Agents.
- [ ] **Implement `MarketCorrelationToolkit` (`backend/tools/market_correlation.py`)**
    - Create tools to fetch BTC/ETH trends as context for altcoin trades.

### 3.2 Advanced Analysis
- [ ] **Implement `FourierToolkit` (`backend/tools/math_tools.py`)**
    - Implement FFT-based trend extraction.
- [ ] **Implement `SentimentToolkit` (`backend/tools/sentiment.py`)**
    - Create a tool that fetches news (via Search) and uses LLM to score sentiment (0-100).
