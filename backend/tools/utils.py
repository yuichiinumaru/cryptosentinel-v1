import httpx
import pandas as pd
from typing import Optional

async def fetch_coingecko_prices(client: httpx.AsyncClient, symbol: str, days: int) -> pd.DataFrame:
    """
    Fetches historical price data from CoinGecko and returns a DataFrame with 'price' column indexed by 'timestamp'.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
    resp = await client.get(url, timeout=10.0)
    if resp.status_code == 429:
        raise RuntimeError("Rate Limit Exceeded")
    resp.raise_for_status()
    data = resp.json()
    if "prices" not in data or not data["prices"]:
        raise ValueError("No price data found")

    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df
