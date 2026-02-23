"""
Index ticker lists for batch analysis.
All lists are hardcoded — no scraping, no external APIs at runtime.
Last updated: February 2026. Minor additions/removals are handled gracefully
(failed tickers are skipped with retries).
"""

from typing import List


# ---------------------------------------------------------------------------
# Dow Jones Industrial Average — 30 components (as of Feb 2026)
# ---------------------------------------------------------------------------
DOW_30: List[str] = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA",
    "CAT",  "CRM",  "CSCO", "CVX", "DIS",
    "GS",   "HD",   "HON",  "IBM", "JNJ",
    "JPM",  "KO",   "MCD",  "MMM", "MRK",
    "MSFT", "NKE",  "NVDA", "PG",  "SHW",
    "TRV",  "UNH",  "V",    "VZ",  "WMT",
]


# ---------------------------------------------------------------------------
# NASDAQ 100 — 100 components (as of Feb 2026)
# ---------------------------------------------------------------------------
NASDAQ_100: List[str] = [
    "ADBE", "ADI",  "ADP",  "ADSK", "AEP",
    "AKAM", "AMAT", "AMD",  "AMGN", "AMZN",
    "ANSS", "APP",  "ASML", "AVGO", "AZN",
    "BIIB", "BKNG", "BKR",  "CCEP", "CDNS",
    "CDW",  "CEG",  "CHTR", "CMCSA","COST",
    "CPRT", "CRWD", "CSCO", "CSGP", "CSX",
    "CTAS", "CTSH", "DASH", "DDOG", "DLTR",
    "DXCM", "EA",   "EXC",  "FANG", "FAST",
    "FTNT", "GEHC", "GFS",  "GILD", "GOOG",
    "GOOGL","HON",  "IDXX", "ILMN", "INTC",
    "INTU", "ISRG", "KDP",  "KHC",  "KLAC",
    "LOGI", "LRCX", "LULU", "MAR",  "MCHP",
    "MDB",  "MDLZ", "MELI", "META", "MNST",
    "MRNA", "MRVL", "MSFT", "MU",   "NFLX",
    "NVDA", "NXPI", "ODFL", "ON",   "ORLY",
    "PANW", "PAYX", "PCAR", "PDD",  "PEP",
    "PYPL", "QCOM", "REGN", "ROP",  "ROST",
    "SBUX", "SIRI", "SNPS", "TEAM", "TMUS",
    "TSLA", "TTWO", "TXN",  "VRSK", "VRSN",
    "VRTX", "WBA",  "WBD",  "WDAY", "XEL",
]


# ---------------------------------------------------------------------------
# S&P 500 — ~503 components (as of Feb 2026)
# ---------------------------------------------------------------------------
SP_500: List[str] = [
    # Information Technology
    "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ACN",  "IBM",  "TXN",  "QCOM",
    "AMD",  "INTC", "INTU", "ADBE", "NOW",  "CSCO", "AMAT", "MU",  "LRCX", "KLAC",
    "SNPS", "CDNS", "PANW", "WDAY", "FTNT", "IT",   "CTSH", "GLW", "HPQ",  "HPE",
    "CDW",  "JNPR", "KEYS", "TER",  "SWKS", "QRVO", "AKAM", "VRSN","FSLR", "EPAM",
    "GEN",  "NTAP", "ZBRA", "FFIV", "STX",  "WDC",  "ENPH", "SEDG","MPWR", "TRMB",
    "PTC",  "ANSS", "TDY",  "GDDY", "ROP",

    # Communication Services
    "GOOGL","GOOG", "META", "NFLX", "DIS",  "CMCSA","T",    "VZ",  "TMUS", "CHTR",
    "WBD",  "PARA", "LYV",  "OMC",  "IPG",  "NWSA", "NWS",  "FOX", "FOXA", "MTCH",
    "ZM",   "SNAP", "PINS", "RBLX", "EA",   "TTWO", "ATVI",

    # Consumer Discretionary
    "AMZN", "TSLA", "HD",   "MCD",  "NKE",  "LOW",  "SBUX", "TJX", "BKNG", "MAR",
    "HLT",  "ABNB", "GM",   "F",    "ORLY", "AZO",  "TSCO", "ROST","ULTA", "DRI",
    "YUM",  "CMG",  "ETSY", "EBAY", "EXPE", "DHI",  "LEN",  "PHM", "NVR",  "TOL",
    "DECK", "HAS",  "MAT",  "NCLH", "RCL",  "CCL",  "MGM",  "WYNN","LVS",  "RL",
    "PVH",  "TPR",  "VFC",  "KSS",  "M",    "JWN",  "GPS",  "ANF", "BBWI", "CPRI",
    "GPC",  "AAP",  "KMX",  "AN",   "PAG",  "LAD",  "APTV", "BWA",

    # Consumer Staples
    "WMT",  "PG",   "KO",   "PEP",  "COST", "MDLZ", "PM",   "MO",  "STZ",  "CL",
    "KMB",  "GIS",  "K",    "HSY",  "SJM",  "CAG",  "CPB",  "MKC", "CHD",  "CLX",
    "EL",   "KHC",  "WBA",  "CVS",  "MNST", "TAP",  "BF-B", "HRL", "TSN",  "LW",
    "INGR", "FLO",  "POST", "SMPL",

    # Healthcare
    "UNH",  "LLY",  "JNJ",  "ABBV", "MRK",  "ABT",  "TMO",  "DHR", "BMY",  "AMGN",
    "GILD", "CI",   "HUM",  "CNC",  "MOH",  "ELV",  "MDT",  "BSX", "SYK",  "ZBH",
    "BAX",  "BDX",  "HOLX", "ISRG", "EW",   "IDXX", "IQV",  "A",   "BIO",  "RMD",
    "VRTX", "REGN", "BIIB", "ILMN", "MRNA", "EXAS", "ALGN", "DXCM","MTD",  "WAT",
    "PKI",  "GEHC", "TECH", "HSIC", "CAH",  "MCK",  "COR",  "ABC", "VTRS", "PFE",
    "AZN",  "SNY",  "RGEN", "INCY", "SGEN", "BMRN", "EXEL", "RARE","ACAD",

    # Financials
    "JPM",  "BAC",  "WFC",  "GS",   "MS",   "BLK",  "C",    "AXP", "SPGI", "MCO",
    "ICE",  "CME",  "SCHW", "TROW", "BEN",  "IVZ",  "FDS",  "MSCI","COF",  "DFS",
    "SYF",  "AIG",  "MET",  "PRU",  "AFL",  "HIG",  "ALL",  "TRV", "CB",   "RE",
    "RJF",  "RF",   "CFG",  "MTB",  "STT",  "BK",   "NTRS", "FITB","HBAN", "KEY",
    "USB",  "PNC",  "BRK-B","CINF", "LNC",  "UNM",  "GL",   "FNF", "FAF",  "CBOE",
    "NDAQ", "MKTX", "IBKR", "SF",   "EVR",  "LAZ",  "GHL",  "WEX", "FIS",  "FI",
    "GPN",  "MA",   "V",    "PYPL", "SQ",   "AFRM", "SOFI",

    # Energy
    "XOM",  "CVX",  "COP",  "EOG",  "SLB",  "MPC",  "VLO",  "PSX", "OXY",  "HAL",
    "BKR",  "DVN",  "HES",  "CTRA", "EQT",  "APA",  "FANG", "MRO", "OKE",  "WMB",
    "KMI",  "LNG",  "TRGP", "AM",   "DT",

    # Materials
    "LIN",  "APD",  "SHW",  "ECL",  "NEM",  "FCX",  "NUE",  "STLD","RS",   "ALB",
    "BALL", "PKG",  "IP",   "WRK",  "SEE",  "MOS",  "CF",   "FMC", "EMN",  "CE",
    "IFF",  "RPM",  "PPG",  "AVY",  "CC",   "OLN",  "ATR",  "SLGN","GEF",

    # Industrials
    "HON",  "GE",   "RTX",  "CAT",  "DE",   "BA",   "UPS",  "FDX", "WM",   "RSG",
    "LMT",  "NOC",  "GD",   "LHX",  "HII",  "TDG",  "CARR", "OTIS","CPRT", "FAST",
    "GWW",  "PH",   "ITW",  "EMR",  "ROK",  "AME",  "TT",   "JCI", "XYL",  "PCAR",
    "WAB",  "CSX",  "NSC",  "UNP",  "EXPD", "CHRW", "XPO",  "ODFL","SAIA", "RXO",
    "AXTA", "IR",   "RRX",  "MAS",  "LII",  "GNRC", "ALLE", "SWK", "SNA",  "PNR",
    "AMETEK","DOV", "FTV",  "BW",   "WTS",  "IEX",  "IDEX",

    # Real Estate
    "AMT",  "PLD",  "CCI",  "EQIX", "PSA",  "EQR",  "AVB",  "SPG", "VTR",  "EXR",
    "MAA",  "O",    "VICI", "BXP",  "KIM",  "REG",  "FRT",  "CPT", "ESS",  "UDR",
    "IRM",  "SUI",  "ELS",  "HST",  "PEAK", "DLR",  "ARE",  "SLG", "WY",   "SBAC",
    "GLPI", "GAMING","MPW",

    # Utilities
    "NEE",  "DUK",  "SO",   "D",    "AEP",  "EXC",  "PCG",  "SRE", "ED",   "XEL",
    "ES",   "WEC",  "ETR",  "FE",   "CNP",  "CMS",  "NI",   "ATO", "LNT",  "PNW",
    "NRG",  "VST",  "CEG",  "AWK",  "WTRG", "SJW",  "YORW",
]


def get_sp500_tickers() -> List[str]:
    return list(SP_500)


def get_nasdaq100_tickers() -> List[str]:
    return list(NASDAQ_100)


INDEX_CONFIGS = {
    "Dow Jones 30": {
        "tickers_fn": lambda: list(DOW_30),
        "count": 30,
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
