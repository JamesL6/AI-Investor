"""
Index ticker lists for batch analysis.
Dow 30 is hardcoded. S&P 500 and NASDAQ 100 are fetched from Wikipedia at runtime.
"""

import io
import requests
import pandas as pd
from typing import List

# Wikipedia blocks requests without a browser-like User-Agent
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _fetch_wiki_tables(url: str) -> list:
    """Fetch Wikipedia page and parse all HTML tables. Raises on failure."""
    response = requests.get(url, headers=_HEADERS, timeout=15)
    response.raise_for_status()
    return pd.read_html(io.StringIO(response.text))


# Dow Jones Industrial Average — 30 components (as of early 2026)
# AMZN replaced WBA (Feb 2024), SHW replaced DOW (Aug 2024), NVDA replaced INTC (Nov 2024)
DOW_30 = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA",
    "CAT",  "CRM",  "CSCO", "CVX", "DIS",
    "GS",   "HD",   "HON",  "IBM", "JNJ",
    "JPM",  "KO",   "MCD",  "MMM", "MRK",
    "MSFT", "NKE",  "NVDA", "PG",  "SHW",
    "TRV",  "UNH",  "V",    "VZ",  "WMT",
]


def get_sp500_tickers() -> List[str]:
    """Fetch current S&P 500 tickers from Wikipedia."""
    try:
        tables = _fetch_wiki_tables("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        result = [str(t).strip() for t in tickers if t and str(t) != "nan"]
        print(f"[Indices] Loaded {len(result)} S&P 500 tickers")
        return result
    except Exception as e:
        print(f"[Indices] Error fetching S&P 500 tickers: {e}")
        return []


def get_nasdaq100_tickers() -> List[str]:
    """Fetch current NASDAQ 100 tickers from Wikipedia."""
    try:
        tables = _fetch_wiki_tables("https://en.wikipedia.org/wiki/Nasdaq-100")
        for df in tables:
            cols_lower = [str(c).lower() for c in df.columns]
            for candidate in ["ticker", "symbol"]:
                if candidate in cols_lower:
                    col = df.columns[cols_lower.index(candidate)]
                    tickers = df[col].tolist()
                    cleaned = [str(t).strip() for t in tickers if t and str(t) != "nan"]
                    if len(cleaned) >= 90:
                        print(f"[Indices] Loaded {len(cleaned)} NASDAQ 100 tickers")
                        return cleaned
        print("[Indices] Could not find NASDAQ 100 ticker column in Wikipedia tables.")
        return []
    except Exception as e:
        print(f"[Indices] Error fetching NASDAQ 100 tickers: {e}")
        return []


INDEX_CONFIGS = {
    "Dow Jones 30": {
        "tickers_fn": lambda: list(DOW_30),
        "count": 30,
        "est_minutes": 3,
        "description": "30 blue-chip US companies that make up the DJIA",
    },
    "S&P 500": {
        "tickers_fn": get_sp500_tickers,
        "count": 503,
        "est_minutes": 6,
        "description": "~500 largest US companies by market cap",
    },
    "NASDAQ 100": {
        "tickers_fn": get_nasdaq100_tickers,
        "count": 100,
        "est_minutes": 5,
        "description": "100 largest non-financial companies listed on the NASDAQ",
    },
}
