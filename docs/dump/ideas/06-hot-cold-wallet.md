# Hot/Cold Wallet Separation

## Description
Security architecture to minimize the risk of total fund loss in case of a compromise.

## Implementation Details
- **Hot Wallet**: Contains a limited amount of capital (e.g., 5-10%) used for active trading. Keys are accessible to the `Trader` agent (via secure env vars or Secret Manager).
- **Cold Wallet**: Hardware wallet (e.g., Ledger) holding the majority of funds. Offline and secure.
- **Operations**:
    - **Top-up**: Logic to transfer funds from Cold to Hot when needed (requires manual approval or semi-automated process).
    - **Profit Skimming**: Excess profits in Hot Wallet should be moved to Cold Wallet periodically.
