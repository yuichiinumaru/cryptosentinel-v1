# Scavenger Analysis: SquareQuant Package

**Source Repository:** [SquareQuant/squarequant-package](https://github.com/SquareQuant/squarequant-package)
**Analysis Date:** 2024-05-22
**Analyst:** Jules (The Tech Scavenger)

## 1. Executive Summary
*   **Core Value:** **Risk Metrics Library.** This is a clean, modular Python library for calculating financial risk metrics: Value at Risk (VaR), Sharpe Ratio, Sortino Ratio, Calmar Ratio, and Monte Carlo simulations.
*   **Tech Stack:** Python, Pandas, NumPy, SciPy.
*   **Verdict:** **EXTRACT UTILS.** Instead of reinventing the math for `RiskManagement`, we should port these classes directly into our `RiskManagementToolkit`.

## 2. Architecture Breakdown
*   **Core:** `squarequant/core/metrics.py` (Basic metrics).
*   **VaR:** `squarequant/var/valueatrisk.py` (Historical & Parametric VaR).
*   **Monte Carlo:** `squarequant/monte_carlo/montecarlo.py`.

## 3. The Gem List (Extractable Features)

### Feature A: Risk Metrics (`squarequant/core/metrics.py`)
*   **Description:** implementations of Sharpe, Sortino, Calmar, MaxDrawdown.
*   **Complexity:** Low (Math formulas).
*   **Integration:** Add to `backend/tools/risk_management.py`. Essential for evaluating our Agent's performance.

### Feature B: Value at Risk (VaR)
*   **Description:** Logic to calculate "How much can I lose with 95% confidence?".
*   **Complexity:** Medium (Statistical).
*   **Integration:** Use in `RiskDebator` (TradingAgents) to reject high-risk trades.

## 4. Integration Strategy
1.  **Create Toolkit:** `QuantitativeAnalysisToolkit`.
2.  **Port:** Copy the logic from `metrics.py` and `valueatrisk.py`.
3.  **Usage:** When `DebateCoordinator` asks for a risk assessment, run these metrics on the asset's history.
