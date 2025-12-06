# Implementation Plans

This document outlines the strategic plans to enhance CryptoSentinel, moving from a fragile prototype to a production-grade system.

## Phase 1: Structural Stabilization (Operation Ironclad)
**Goal:** Fix critical architectural and security flaws identified in the Autopsy.

1.  **Secure Architecture:**
    *   Implement **Factory Pattern** for Agent instantiation to fix global state leaks.
    *   Enforce **Async-Only** I/O for Web3 and HTTP calls to fix thread blocking.
    *   Secure `API_KEY` handling (Env vars, strict validation).

2.  **Resource Management:**
    *   Refactor `DexToolkit` to use a shared/pooled Web3 connection.
    *   Fix N+1 database write issues in `PortfolioToolkit`.

3.  **Governance Compliance:**
    *   Enforce `AGENTS.md` and FORGE file structure.

## Phase 2: Feature Enhancement (TradingAgents Integration)

1.  **Adversarial Debate Workflow:**
    *   Implement `BullResearcher` and `BearResearcher`.
    *   Create a `DebateCoordinator` to moderate thesis/antithesis loops before trading.

2.  **Situation-Aware Memory:**
    *   Schema for `MarketSituation`.
    *   Vector Search integration in `KhalaMemoryToolkit`.

3.  **Deep Thinking Prompts:**
    *   Refactor Agent instructions to "Role-Task-Constraint-Output" format.

## Phase 3: Quantitative Analysis Integration (StockPredictionAI)
**Goal:** Incorporate advanced quantitative strategies extracted from the `stockpredictionai` reference.

1.  **Technical Analysis Engine:**
    *   Implement `TechnicalAnalysisToolkit` using Pandas to calculate Moving Averages, MACD, Bollinger Bands, and Momentum.
    *   Provide these indicators as tools to the Trading Agents.

2.  **Market Context Awareness:**
    *   Implement `MarketCorrelationToolkit` to fetch and analyze correlated assets (BTC, ETH, SP500, VIX) alongside the target asset.
    *   Implement `SentimentToolkit` to score news sentiment using LLMs (adapting the BERT logic).

3.  **Mathematical Signal Processing:**
    *   Implement `FourierToolkit` to perform trend analysis and denoising using FFT.
    *   (Optional) Implement ARIMA forecasting tools.

## Phase 4: Advanced Security & Optimization

1.  **MEV Protection:**
    *   Flashbots integration.
2.  **Simulation:**
    *   Pre-trade simulation (Tenderly/Forked Mainnet) to verify outcomes before execution.
