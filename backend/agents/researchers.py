from agno.agent import Agent
from agno.models.google import Gemini

from backend.tools.technical_analysis import TechnicalAnalysisToolkit
from backend.tools.regime import MarketRegimeToolkit
from backend.tools.quant_metrics import QuantitativeAnalysisToolkit
from backend.tools.market_data import MarketDataToolkit

def get_bull_researcher(model: Gemini, session_id: str = None) -> Agent:
    return Agent(
        name="BullResearcher",
        role="Optimistic Market Researcher",
        model=model,
        tools=[
            TechnicalAnalysisToolkit(),
            MarketRegimeToolkit(),
            QuantitativeAnalysisToolkit(),
            MarketDataToolkit() # Needed? Tech/Regime/Quant usually self-fetch now.
        ],
        instructions=[
            "You are the Bullish Researcher. Your goal is to find reasons to BUY.",
            "Analyze the asset using your tools. Focus on:",
            "1. Positive Trends (SMA50 > SMA200, Uptrends).",
            "2. Bullish Momentum (RSI recovering, MACD crossovers).",
            "3. High Sharpe/Sortino ratios indicating good risk-adjusted returns.",
            "4. Bullish Regime identification.",
            "Construct a strong THESIS for a long position.",
            "Do not ignore risks, but frame them as 'manageable' or 'priced in'.",
            "Use data to back up your claims."
        ],
        session_id=session_id,
        markdown=True,
    )

def get_bear_researcher(model: Gemini, session_id: str = None) -> Agent:
    return Agent(
        name="BearResearcher",
        role="Pessimistic Market Researcher",
        model=model,
        tools=[
            TechnicalAnalysisToolkit(),
            MarketRegimeToolkit(),
            QuantitativeAnalysisToolkit(),
            MarketDataToolkit()
        ],
        instructions=[
            "You are the Bearish Researcher. Your goal is to find reasons to SELL or AVOID.",
            "Analyze the asset using your tools. Focus on:",
            "1. Negative Trends (Price < SMA200, Downtrends).",
            "2. Bearish Momentum (Overbought RSI, MACD divergence).",
            "3. High VaR (Value at Risk) or Max Drawdown risks.",
            "4. Bearish or Crisis Regime identification.",
            "Construct a strong ANTITHESIS against buying.",
            "Highlight the worst-case scenarios.",
            "Use data to back up your claims."
        ],
        session_id=session_id,
        markdown=True,
    )

def get_debate_coordinator(model: Gemini, session_id: str = None) -> Agent:
    return Agent(
        name="DebateCoordinator",
        role="Impartial Judge & Risk Manager",
        model=model,
        tools=[
            QuantitativeAnalysisToolkit() # Double check risk metrics
        ],
        instructions=[
            "You are the Debate Coordinator and Chief Risk Officer.",
            "Your job is to synthesize the arguments from the BullResearcher and BearResearcher.",
            "1. Review the Bull Case and Bear Case.",
            "2. check the Quantitative Risk Metrics yourself (VaR, Sharpe).",
            "3. Decide on a final recommendation: BUY, SELL, or HOLD/WAIT.",
            "4. Assign a Confidence Score (0-100%).",
            "5. If risks (VaR/Drawdown) are too high, favor the Bear.",
            "Be objective. Do not hallucinate data."
        ],
        session_id=session_id,
        markdown=True,
    )
