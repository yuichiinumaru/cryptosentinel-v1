# Scavenger Analysis: AI Memecoin Trading Bot

**Source Repository:** [Jackhuang166/ai-memecoin-trading-bot](https://github.com/Jackhuang166/ai-memecoin-trading-bot)
**Analysis Date:** 2024-05-22
**Analyst:** Jules (The Tech Scavenger)

## 1. Executive Summary
*   **Core Value:** **Safety in the Wild West.** This Go-based bot focuses on **Honeypot Detection** and **Win Probability** for high-risk memecoins.
*   **Tech Stack:** Go (Golang), Solana/Base RPC.
*   **Verdict:** **TRANSLATE LOGIC.** We cannot use the code (Go), but we MUST port the *logic* of how it detects honeypots and calculates safety scores.

## 2. Architecture Breakdown
*   **Scanner:** Monitors chain for new pools.
*   **Filter (Honeypot):** Checks if token is sellable, liquidity locked, mint authority disabled.
*   **Scorer:** Calculates "Win Probability" based on holders, liquidity depth, social signals.

## 3. The Gem List (Extractable Features)

### Feature A: Honeypot Detection Logic
*   **Description:** A checklist of safety checks (Renounced Ownership, Frozen Mint, Liquidity Burned/Locked).
*   **Complexity:** Medium (Logic is simple, but RPC calls need to be correct).
*   **Integration:** Implement `SecurityToolkit` in `backend/tools/security.py`. This is critical for "Zero Trust".

### Feature B: Win Probability Score
*   **Description:** A scoring algorithm (>=80% threshold) used to filter trades.
*   **Complexity:** Medium.
*   **Integration:** Add `calculate_safety_score` to `SecurityToolkit`.

## 4. Integration Strategy
1.  **Reverse Engineer:** Read the Go code (specifically `pkg/agents` or `internal/`) to find the exact checks performed.
2.  **Port to Python:** Implement these checks using `Web3.py` (for EVM) or `solana-py` (if we support Solana later). For now, focus on EVM equivalents (ERC20 checks).
