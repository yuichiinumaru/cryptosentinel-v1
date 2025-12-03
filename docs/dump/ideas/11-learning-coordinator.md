# Learning Coordinator (Self-Improvement)

## Description
An agent dedicated to analyzing the system's performance and "learning" from it to improve future decisions.

## Implementation Details
- **Cycle**: Runs periodically (e.g., daily).
- **Process**:
    1. Fetch trade history and performance metrics (ROI, Win Rate).
    2. Analyze `Chain of Thought` (CoT) logs of successful vs. failed trades.
    3. Identify patterns or biases.
- **Actions**:
    - **Adjust Instructions**: Modify the system prompt of `MarketAnalyst` or `Trader` (e.g., "Be more conservative in high volatility").
    - **Adjust Parameters**: Tune RSI thresholds or Risk limits.
