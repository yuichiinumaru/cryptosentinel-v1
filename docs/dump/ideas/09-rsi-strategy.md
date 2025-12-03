# RSI Trading Strategy (MVP)

## Description
A simple, quantitative strategy for the Minimum Viable Product to validate the execution pipeline without complex logic.

## Implementation Details
- **Indicator**: Relative Strength Index (RSI) with 14 periods.
- **Rules**:
    - **Buy Signal**: RSI < 30 (Oversold).
    - **Sell Signal**: RSI > 70 (Overbought).
- **Scope**: Focus on Top 50 Market Cap tokens to ensure liquidity and reduce rug risk during initial testing.
- **Agent**: `MarketAnalyst` calculates RSI using `CalculateTechnicalIndicator` tool and generates recommendations.
