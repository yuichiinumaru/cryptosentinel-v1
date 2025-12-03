# CEX Integration & Arbitrage

## Description
Extend the system to trade on Centralized Exchanges (CEXs) and exploit price differences between CEXs and DEXs (Arbitrage).

## Implementation Details
- **Library**: `ccxt` (CryptoCurrency eXchange Trading Library).
- **Functionality**:
    - Unified API for Binance, Kraken, Coinbase, etc.
    - Fetch order books and execute market/limit orders.
- **Arbitrage**: `CheckArbitrageOpportunities` tool compares prices across venues and signals risk-free profit opportunities.
