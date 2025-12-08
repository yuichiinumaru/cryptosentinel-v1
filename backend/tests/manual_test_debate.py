import os
import sys
import asyncio
# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from backend.config import Config
from backend.agents.researchers import get_bull_researcher, get_bear_researcher, get_debate_coordinator

load_dotenv()

async def run_debate():
    print("Initializing Debate Team...")
    try:
        model = Config.get_model()
    except Exception as e:
        print(f"Skipping test due to configuration error: {e}")
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
    asyncio.run(run_debate())
