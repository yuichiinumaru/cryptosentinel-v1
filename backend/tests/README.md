# Backend Tests

## Running Tests

The test suite uses `pytest` and `unittest.mock`. To run the tests correctly, you must set the `PYTHONPATH` to the project root.

```bash
# From the project root
export PYTHONPATH=$PYTHONPATH:.
python -m pytest backend/tests/
```

## Test Structure

*   `test_agents_factory.py`: Verifies the Agent Factory (`get_crypto_trading_team`).
*   `test_toolkits.py`: Unit tests for Scavenger toolkits (Technical, Quant, Regime, Correlation).
*   `test_dex_tools.py`: Unit tests for DEX interaction (AsyncWeb3).
*   `test_asset_management.py`: Unit tests for asset monitoring.
*   `test_market_data.py`: Unit tests for market data fetching.
*   `manual_test_debate.py`: A script for manual end-to-end verification of the Debate workflow (requires API Keys).
