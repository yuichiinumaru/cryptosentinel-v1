# Risk Management Rules

## Description
Quantitative limits imposed by the `DeepTraderManager` and `RiskAnalyst` to protect capital.

## Implementation Details
- **Capital Allocation**: Max 2% of total portfolio value per trade. (Alternatively 1% position size mentioned in some contexts).
- **Daily Loss Limit**: Stop trading if portfolio drops by > 5% in a single day.
- **Stop Loss / Take Profit**:
    - **Stop Loss**: 10% (from entry price).
    - **Take Profit**: 20% (from entry price).
- **Enforcement**: Hard constraints checked by `DeepTraderManager` before approving any `TradeRecommendation`.
