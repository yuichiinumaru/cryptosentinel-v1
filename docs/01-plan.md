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

## Phase 2: Intelligent Agent Architecture (Source: TradingAgents)
**Goal:** Implement the "Debate" architecture to reduce hallucination and risk.

1.  **Adversarial Debate Workflow:**
    *   **Source:** `TauricResearch/TradingAgents`
    *   Implement `BullResearcher` and `BearResearcher` agents with conflicting system prompts.
    *   Create a `DebateCoordinator` (Risk Debator) to moderate the discussion and force a synthesis.

2.  **Situation-Aware Memory:**
    *   Schema for `MarketSituation`.
    *   Vector Search integration in `KhalaMemoryToolkit`.

3.  **Deep Thinking Prompts:**
    *   Refactor Agent instructions to "Role-Task-Constraint-Output" format.

## Phase 3: Scientific Validation & Analysis (Source: AgentQuant & StockPredictionAI)
**Goal:** Incorporate advanced quantitative strategies and regime detection.

1.  **Regime Detection Engine:**
    *   **Source:** `OnePunchMonk/AgentQuant`
    *   Implement `MarketRegimeToolkit` to classify market state (Bull/Bear/Sideways/Crisis) using VIX and Momentum.
    *   Inject "Regime" context into all agent prompts.

2.  **Technical Analysis Engine:**
    *   **Source:** `borisbanushev/stockpredictionai` & `ai-hedge-fund-crypto`
    *   Implement `TechnicalAnalysisToolkit` (MA, MACD, Bollinger, Momentum).
    *   Implement `FourierToolkit` for trend denoising.

3.  **Market Context Awareness:**
    *   Implement `MarketCorrelationToolkit` (BTC/ETH context).
    *   Implement `SentimentToolkit` (News Analysis).

## Phase 4: Advanced Security & Optimization (Source: AI Memecoin Bot)
**Goal:** Zero-Trust execution and simulation.

1.  **Honeypot Protection:**
    *   **Source:** `Jackhuang166/ai-memecoin-trading-bot`
    *   Port "Honeypot Detection" logic (Go -> Python) to `SecurityToolkit`.
    *   Implement "Win Probability" safety checks.

2.  **MEV Protection:**
    *   Flashbots integration.

3.  **Simulation:**
    *   Pre-trade simulation (Tenderly/Forked Mainnet).
