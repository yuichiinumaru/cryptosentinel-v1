import pytest
from backend.tools.traffic_rules import TrafficRuleToolkit

def test_traffic_rule_toolkit_initialization():
    toolkit = TrafficRuleToolkit()
    assert toolkit.name == "traffic_rule_toolkit"

def test_get_market_congestion_score():
    toolkit = TrafficRuleToolkit()

    # Test case 1: No congestion
    score = toolkit.get_market_congestion_score(rsi=50, price=100, upper_band=110, lower_band=90)
    assert score == 1.0

    # Test case 2: High RSI congestion
    score = toolkit.get_market_congestion_score(rsi=85, price=105, upper_band=110, lower_band=90)
    assert score < 1.0

    # Test case 3: Low RSI congestion
    score = toolkit.get_market_congestion_score(rsi=15, price=95, upper_band=110, lower_band=90)
    assert score < 1.0

    # Test case 4: High Bollinger Band congestion
    score = toolkit.get_market_congestion_score(rsi=50, price=115, upper_band=110, lower_band=90)
    assert score < 1.0

    # Test case 5: Low Bollinger Band congestion
    score = toolkit.get_market_congestion_score(rsi=50, price=85, upper_band=110, lower_band=90)
    assert score < 1.0

    # Test case 6: Combined congestion
    score = toolkit.get_market_congestion_score(rsi=80, price=112, upper_band=110, lower_band=90)
    assert score < 0.7
