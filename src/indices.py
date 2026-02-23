"""
Index ticker lists for batch analysis.
All lists are hardcoded — no scraping, no external APIs at runtime.
Last updated: February 2026. Minor quarterly additions/removals are handled
gracefully (failed tickers are retried then skipped).
"""

from typing import List


# ---------------------------------------------------------------------------
# Dow Jones Industrial Average — 30 components (as of Feb 2026)
# ---------------------------------------------------------------------------
DOW_30: List[str] = [
    "AAPL", "AMGN", "AMZN", "AXP",  "BA",
    "CAT",  "CRM",  "CSCO", "CVX",  "DIS",
    "GS",   "HD",   "HON",  "IBM",  "JNJ",
    "JPM",  "KO",   "MCD",  "MMM",  "MRK",
    "MSFT", "NKE",  "NVDA", "PG",   "SHW",
    "TRV",  "UNH",  "V",    "VZ",   "WMT",
]


# ---------------------------------------------------------------------------
# NASDAQ 100 — 100 components (as of Feb 2026)
# ---------------------------------------------------------------------------
NASDAQ_100: List[str] = [
    # Tech
    "AAPL", "MSFT", "NVDA", "AVGO", "CSCO", "ADBE", "INTU", "AMD",  "QCOM", "TXN",
    "AMAT", "LRCX", "KLAC", "SNPS", "CDNS", "MRVL", "NXPI", "MU",   "PANW", "FTNT",
    "WDAY", "ANSS", "DDOG", "ZS",   "TEAM", "OKTA", "CRWD", "GDDY", "CDW",  "AKAM",
    "VRSN", "ROP",  "PTC",  "TRMB", "NTAP", "WDC",  "STX",
    # Communication
    "GOOGL","GOOG", "META", "NFLX", "CMCSA","T",    "TMUS", "WBD",  "EA",   "TTWO",
    "MTCH", "SIRI",
    # Consumer Discretionary
    "AMZN", "TSLA", "BKNG", "MAR",  "SBUX", "ORLY", "AZO",  "ROST", "DLTR", "LULU",
    "MELI", "EBAY", "EXPE", "CPRT", "CSGP", "FAST",
    # Consumer Staples
    "PEP",  "COST", "MDLZ", "KHC",  "MNST", "KDP",
    # Healthcare
    "AMGN", "GILD", "VRTX", "REGN", "BIIB", "ISRG", "IDXX", "ILMN", "MRNA", "DXCM",
    "GEHC",
    # Financials
    "PYPL",
    # Industrials
    "HON",  "PCAR", "ODFL", "CTAS", "PAYX", "XEL",  "VRSK",
    # Energy / Utilities
    "CEG",  "AEP",  "EXC",
    # International (listed on NASDAQ)
    "ASML", "AZN",  "CCEP", "PDD",  "MCHP", "ON",   "GFS",
]


# ---------------------------------------------------------------------------
# S&P 500 — ~500 components (as of Feb 2026)
# ---------------------------------------------------------------------------
SP_500: List[str] = [
    # --- Information Technology ---
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM",  "ACN",  "IBM",  "TXN",  "QCOM",
    "AMD",  "INTC", "INTU", "ADBE", "NOW",  "CSCO", "AMAT", "MU",   "LRCX", "KLAC",
    "SNPS", "CDNS", "PANW", "WDAY", "FTNT", "IT",   "CTSH", "GLW",  "HPQ",  "HPE",
    "CDW",  "KEYS", "TER",  "AKAM", "VRSN", "EPAM", "NTAP", "ZBRA", "STX",  "WDC",
    "ENPH", "MPWR", "TRMB", "PTC",  "ANSS", "TDY",  "GDDY", "ROP",  "FICO", "ANET",
    "MRVL", "DDOG", "ZS",   "HUBS", "SMCI", "LDOS", "SAIC", "BAH",  "GEN",
    "FFIV", "FSLR", "JNPR", "SWKS",

    # --- Communication Services ---
    "GOOGL","GOOG", "META", "NFLX", "DIS",  "CMCSA","T",    "VZ",   "TMUS", "CHTR",
    "WBD",  "PARA", "LYV",  "OMC",  "IPG",  "NWSA", "NWS",  "FOX",  "FOXA", "MTCH",
    "EA",   "TTWO",

    # --- Consumer Discretionary ---
    "AMZN", "TSLA", "HD",   "MCD",  "NKE",  "LOW",  "SBUX", "TJX",  "BKNG", "MAR",
    "HLT",  "ABNB", "GM",   "F",    "ORLY", "AZO",  "TSCO", "ROST", "ULTA", "DRI",
    "YUM",  "CMG",  "ETSY", "EBAY", "EXPE", "DHI",  "LEN",  "PHM",  "NVR",  "TOL",
    "DECK", "HAS",  "MAT",  "NCLH", "RCL",  "CCL",  "MGM",  "WYNN", "LVS",  "RL",
    "PVH",  "TPR",  "KSS",  "M",    "BBWI", "CPRI", "GPC",  "AAP",  "KMX",  "AN",
    "APTV", "BWA",  "LULU", "WSM",  "POOL", "RH",   "GRMN", "UBER",

    # --- Consumer Staples ---
    "WMT",  "PG",   "KO",   "PEP",  "COST", "MDLZ", "PM",   "MO",   "STZ",  "CL",
    "KMB",  "GIS",  "K",    "HSY",  "SJM",  "CAG",  "CPB",  "MKC",  "CHD",  "CLX",
    "EL",   "KHC",  "WBA",  "CVS",  "MNST", "TAP",  "BF-B", "HRL",  "TSN",  "LW",
    "INGR",

    # --- Healthcare ---
    "UNH",  "LLY",  "JNJ",  "ABBV", "MRK",  "ABT",  "TMO",  "DHR",  "BMY",  "AMGN",
    "GILD", "CI",   "HUM",  "CNC",  "MOH",  "ELV",  "MDT",  "BSX",  "SYK",  "ZBH",
    "BAX",  "BDX",  "HOLX", "ISRG", "EW",   "IDXX", "IQV",  "A",    "RMD",  "VRTX",
    "REGN", "BIIB", "ILMN", "MRNA", "EXAS", "ALGN", "DXCM", "MTD",  "WAT",  "PKI",
    "GEHC", "TECH", "HSIC", "CAH",  "MCK",  "COR",  "ABC",  "VTRS", "PFE",  "PODD",
    "TFX",  "MASI", "INCY", "BMRN",

    # --- Financials ---
    "JPM",  "BAC",  "WFC",  "GS",   "MS",   "BLK",  "C",    "AXP",  "SPGI", "MCO",
    "ICE",  "CME",  "SCHW", "TROW", "BEN",  "IVZ",  "FDS",  "MSCI", "COF",  "DFS",
    "SYF",  "AIG",  "MET",  "PRU",  "AFL",  "HIG",  "ALL",  "TRV",  "CB",   "RE",
    "RJF",  "RF",   "CFG",  "MTB",  "STT",  "BK",   "NTRS", "FITB", "HBAN", "KEY",
    "USB",  "PNC",  "BRK-B","CINF", "LNC",  "UNM",  "GL",   "FNF",  "FAF",  "CBOE",
    "NDAQ", "MKTX", "IBKR", "FIS",  "FI",   "GPN",  "MA",   "V",    "PYPL",
    "PGR",  "MMC",  "AON",  "WTW",  "AJG",  "ACGL", "ALLY", "TRU",  "ERIE",

    # --- Energy ---
    "XOM",  "CVX",  "COP",  "EOG",  "SLB",  "MPC",  "VLO",  "PSX",  "OXY",  "HAL",
    "BKR",  "DVN",  "HES",  "CTRA", "EQT",  "APA",  "FANG", "MRO",  "OKE",  "WMB",
    "KMI",  "LNG",  "TRGP",

    # --- Materials ---
    "LIN",  "APD",  "SHW",  "ECL",  "NEM",  "FCX",  "NUE",  "STLD", "RS",   "ALB",
    "BALL", "PKG",  "IP",   "WRK",  "SEE",  "MOS",  "CF",   "FMC",  "EMN",  "CE",
    "IFF",  "RPM",  "PPG",  "AVY",  "DOW",  "LYB",  "CTVA", "VMC",  "MLM",  "CRH",
    "AMCR", "AXTA", "TDY",

    # --- Industrials ---
    "HON",  "GE",   "RTX",  "CAT",  "DE",   "BA",   "UPS",  "FDX",  "WM",   "RSG",
    "LMT",  "NOC",  "GD",   "LHX",  "HII",  "TDG",  "CARR", "OTIS", "CPRT", "FAST",
    "GWW",  "PH",   "ITW",  "EMR",  "ROK",  "AME",  "TT",   "JCI",  "XYL",  "PCAR",
    "WAB",  "CSX",  "NSC",  "UNP",  "EXPD", "CHRW", "XPO",  "ODFL", "SAIA", "RXO",
    "IR",   "RRX",  "MAS",  "LII",  "GNRC", "ALLE", "SWK",  "SNA",  "PNR",  "AME",
    "DOV",  "FTV",  "IEX",  "IDEX", "HWM",  "TXT",  "HXL",

    # --- Real Estate ---
    "AMT",  "PLD",  "CCI",  "EQIX", "PSA",  "EQR",  "AVB",  "SPG",  "VTR",  "EXR",
    "MAA",  "O",    "VICI", "BXP",  "KIM",  "REG",  "FRT",  "CPT",  "ESS",  "UDR",
    "IRM",  "SUI",  "ELS",  "HST",  "DLR",  "ARE",  "WY",   "SBAC", "GLPI", "WELL",
    "CSGP", "CBRE", "NNN",  "AMH",

    # --- Utilities ---
    "NEE",  "DUK",  "SO",   "D",    "AEP",  "EXC",  "PCG",  "SRE",  "ED",   "XEL",
    "ES",   "WEC",  "ETR",  "FE",   "CNP",  "CMS",  "NI",   "ATO",  "LNT",  "PNW",
    "NRG",  "VST",  "CEG",  "AWK",  "AES",  "PEG",  "EIX",  "PPL",  "DTE",  "EVRG",
]

# Remove any accidental duplicates while preserving order
_seen: set = set()
_deduped: List[str] = []
for _t in SP_500:
    if _t not in _seen:
        _seen.add(_t)
        _deduped.append(_t)
SP_500 = _deduped


def get_sp500_tickers() -> List[str]:
    return list(SP_500)


def get_nasdaq100_tickers() -> List[str]:
    return list(NASDAQ_100)


INDEX_CONFIGS = {
    "Dow Jones 30": {
        "tickers_fn": lambda: list(DOW_30),
        "count": len(DOW_30),
        "est_minutes": 3,
        "description": "30 blue-chip US companies that make up the DJIA",
    },
    "S&P 500": {
        "tickers_fn": get_sp500_tickers,
        "count": len(SP_500),
        "est_minutes": 6,
        "description": "~500 largest US companies by market cap",
    },
    "NASDAQ 100": {
        "tickers_fn": get_nasdaq100_tickers,
        "count": len(NASDAQ_100),
        "est_minutes": 5,
        "description": "100 largest non-financial companies listed on the NASDAQ",
    },
}
