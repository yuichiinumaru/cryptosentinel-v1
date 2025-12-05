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

## Phase 3: Advanced Security & Optimization

1.  **MEV Protection:**
    *   Flashbots integration.
2.  **Simulation:**
    *   Pre-trade simulation (Tenderly/Forked Mainnet) to verify outcomes before execution.
