# Benjamin Graham Intelligent Investor Agent

Analyze stocks using Benjamin Graham's classic value investing criteria from "The Intelligent Investor".

## Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set xAI (Grok) API key for AI-generated explanations
export XAI_API_KEY=your_xai_api_key_here
```

## Usage

### Interactive Mode
```bash
python main.py
```

### Analyze Single Stock
```bash
# Defensive investor analysis (stricter criteria)
python main.py --ticker AAPL --strategy defensive

# Enterprising investor analysis (more aggressive)
python main.py --ticker AAPL --strategy enterprising

# Skip AI explanation (faster, no API key needed)
python main.py --ticker AAPL --no-llm
```

### Compare Multiple Stocks
```bash
python main.py --tickers AAPL,JNJ,KO,WMT --strategy defensive
```

## Investment Strategies

### Defensive Investor (7 Criteria)
For conservative investors seeking maximum safety:

1. **Adequate Size**: Revenue > $500M
2. **Strong Financials (Current Ratio)**: Current Ratio > 2.0
3. **Strong Financials (Debt)**: Long-term Debt < Net Current Assets
4. **Earnings Stability**: Positive earnings for 10 consecutive years
5. **Dividend Record**: Uninterrupted dividends for 20 years
6. **Earnings Growth**: 33%+ growth over 10 years (using 3-year averages)
7. **Moderate Valuation**: P/E < 15 AND P/B < 1.5, OR P/E × P/B < 22.5

### Enterprising Investor (6 Criteria)
For active investors seeking bargains:

1. **Financial Condition**: Current Ratio > 1.5
2. **Debt Level**: Total Debt < 110% of Net Current Assets
3. **Earnings Stability**: No deficit in last 5 years
4. **Dividend Record**: Currently pays any dividend
5. **Earnings Growth**: Current earnings > earnings 5 years ago
6. **Price**: Price < 120% of Net Tangible Assets per share

## Output

The tool provides:
- Financial summary with key metrics
- Pass/fail status for each criterion
- Overall score and recommendation
- AI-generated narrative verdict (if API key is set)

## Data Source

Financial data is fetched from Yahoo Finance via the `yfinance` library. Note that:
- Historical data availability varies by company
- Some metrics may be missing for certain companies (e.g., insurance companies)
- Data is real-time and may differ slightly between runs

## Disclaimer

This tool is for educational purposes only. It is not financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

