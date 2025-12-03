# Fake Volume Detection

## Description
Detect tokens with artificially inflated trading volume, which is often used to lure investors into scams.

## Implementation Details
- **Heuristics**:
    - **Volume/Transaction Ratio**: High volume with few transactions is suspicious.
    - **Price/Volume Divergence**: Volume spikes without corresponding price action.
- **External Tools**:
    - **Pocket Universe API**: If available, use to score transaction legitimacy.
- **Responsibility**: `MarketAnalyst` or `RiskAnalyst` runs `_detect_fake_volume`.
