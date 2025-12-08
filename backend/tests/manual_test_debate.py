import os
import sys
import asyncio
# Add project root to sys.path to allow imports
# We need to go up two levels: backend/tests/ -> backend/ -> root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
from backend.config import Config
from backend.agents.researchers import get_bull_researcher, get_bear_researcher, get_debate_coordinator

# Tool Imports for direct verification
from backend.tools.security import SecurityToolkit, CheckSecurityInput
from backend.tools.math_tools import FourierToolkit, FourierTrendInput
from backend.tools.market_correlation import MarketCorrelationToolkit, GetCorrelationInput

load_dotenv()

async def verify_tools():
    print("\n=== VERIFYING NEW TOOLS ===")

    # 1. Market Correlation
    print("Testing MarketCorrelationToolkit...")
    corr_tool = MarketCorrelationToolkit()
    try:
        corr = await corr_tool.get_market_correlations(GetCorrelationInput(symbol="solana"))
        print(f"Correlation (SOL): {corr}")
    except Exception as e:
        print(f"Correlation Failed: {e}")

    # 2. Fourier Trend
    print("Testing FourierToolkit...")
    fourier_tool = FourierToolkit()
    try:
        fourier = await fourier_tool.get_fourier_trend(FourierTrendInput(symbol="bitcoin"))
        print(f"Fourier (BTC): {fourier}")
    except Exception as e:
        print(f"Fourier Failed: {e}")

    # 3. Security Check (WETH)
    print("Testing SecurityToolkit...")
    sec_tool = SecurityToolkit()
    try:
        # WETH Mainnet
        sec = await sec_tool.check_token_security(CheckSecurityInput(token_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", chain="ethereum"))
        print(f"Security (WETH): {sec}")
    except Exception as e:
        print(f"Security Check Failed: {e}")


async def run_debate():
    print("\n=== INITIALIZING DEBATE TEAM ===")
    try:
        model = Config.get_model()
    except Exception as e:
        print(f"Skipping agent test due to configuration error: {e}")
        return

    bull = get_bull_researcher(model)
    bear = get_bear_researcher(model)
    judge = get_debate_coordinator(model)

    print("\n=== BULL RESEARCHER ===")
    bull_resp = None
    try:
        bull_resp = await bull.arun("Analyze bitcoin")
        print(bull_resp.content)
    except Exception as e:
        print(f"Bull failed: {e}")

    print("\n=== BEAR RESEARCHER ===")
    bear_resp = None
    try:
        bear_resp = await bear.arun("Analyze bitcoin")
        print(bear_resp.content)
    except Exception as e:
        print(f"Bear failed: {e}")

    if bull_resp and bear_resp:
        print("\n=== DEBATE COORDINATOR ===")
        try:
            judge_resp = await judge.arun(f"Bull Thesis:\n{bull_resp.content}\n\nBear Antithesis:\n{bear_resp.content}\n\nReview the data and decide.")
            print(judge_resp.content)
        except Exception as e:
            print(f"Judge failed: {e}")

if __name__ == "__main__":
    # Run tool verification first
    asyncio.run(verify_tools())
    # Then run debate
    asyncio.run(run_debate())
