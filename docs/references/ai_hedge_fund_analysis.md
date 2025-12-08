# Scavenger Analysis: AI Hedge Fund Crypto

**Source Repository:** [51bitquant/ai-hedge-fund-crypto](https://github.com/51bitquant/ai-hedge-fund-crypto)
**Analysis Date:** 2024-05-22
**Analyst:** Jules (The Tech Scavenger)

## 1. Executive Summary
*   **Core Value:** **Workflow Engineering.** This repo implements a clean, graph-based workflow (Nodes, Edges) for trading agents, similar to LangGraph but custom. It also has a nice library of **Strategies** (MACD, RSI).
*   **Tech Stack:** Python, Custom Graph Engine.
*   **Verdict:** **REFERENCE ARCHITECTURE.** Good to see how they structure "Nodes" (DataNode, StrategyNode). Useful for verifying our own "Agent Team" structure.

## 2. Architecture Breakdown
*   **Graph Nodes:** `BaseNode`, `DataNode`, `StrategyNode`, `RiskManagementNode`.
*   **Strategies:** Modular implementations of MACD, RSI.

## 3. The Gem List (Extractable Features)

### Feature A: Node-Based Logic
*   **Description:** Clear separation of concerns (Data -> Strategy -> Risk).
*   **Complexity:** Medium.
*   **Integration:** Ensure our `DeepTraderManager` follows this flow. We are using Agno, so we don't need their Graph engine, but the *sequence* is valid.

### Feature B: Technical Indicators (`src/indicators`)
*   **Description:** Clean implementations of Momentum/Volatility.
*   **Complexity:** Low.
*   **Integration:** Compare with `stockpredictionai`'s indicators. Pick the cleanest implementation for our `TechnicalAnalysisToolkit`.

## 4. Integration Strategy
1.  **Review Indicators:** Check `src/indicators/momentum.py` vs our planned `TechnicalAnalysisToolkit`.
2.  **Workflow Check:** Verify our `DeepTraderManager` includes explicit "Risk Management" and "Portfolio Management" steps, as their graph does.
