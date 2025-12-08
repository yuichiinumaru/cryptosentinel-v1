# Scavenger Analysis: AgentQuant

**Source Repository:** [OnePunchMonk/AgentQuant](https://github.com/OnePunchMonk/AgentQuant)
**Analysis Date:** 2024-05-22
**Analyst:** Jules (The Tech Scavenger)

## 1. Executive Summary
*   **Core Value:** **Scientific Rigor**. While many bots just "trade", this one validates strategies using **Regime Detection** and **Walk-Forward Analysis**. It turns trading into a science.
*   **Tech Stack:** Python, Google Gemini 2.5 Flash (Compatible!), Streamlit, VectorBT.
*   **Verdict:** **EXTRACT LOGIC, DISCARD UI.** The validation frameworks and regime detection logic are critical for Phase 3/4.

## 2. Architecture Breakdown
*   **Regime Detection:** Classifies market into 'Bull', 'Bear', 'Sideways', 'Crisis' using VIX and Momentum.
*   **Strategy Planner:** Uses LLM (Gemini) to propose parameters *based on the regime*.
*   **Validation Engine:** Runs `Ablation Studies` (Did context help?) and `Walk-Forward` (Does it hold up over time?).

## 3. The Gem List (Extractable Features)

### Feature A: Regime Detection (`src/features/regime.py`)
*   **Description:** Mathematical logic to classify market state.
*   **Complexity:** Medium.
*   **Integration:** Implement `MarketRegimeToolkit` in `backend/tools/`. Use it to inject context into every trade decision.

### Feature B: Walk-Forward Validation (`experiments/walk_forward.py`)
*   **Description:** A framework to re-optimize parameters on a rolling window.
*   **Complexity:** High (Requires Backtesting Engine).
*   **Integration:** Create a `SimulationToolkit` or a standalone script in `backend/simulation/` to run this on our strategies.

### Feature C: Context-Aware Prompts (`src/agent/`)
*   **Description:** Prompts that feed the "Regime" into the "Strategy Planner".
*   **Complexity:** Low.
*   **Integration:** Update `DeepTraderManager` instructions to request and respect "Market Regime".

## 4. Integration Strategy
1.  **Immediate:** Implement `RegimeDetection` tool. This adds immediate "IQ" to our agents.
2.  **Later:** Implement the full `Walk-Forward` validation pipeline when we have a solid Backtesting engine.
