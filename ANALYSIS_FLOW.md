# Analysis Flow Explanation

## Complete Flow: Data → Analysis → AI Verdict

### Step 1: Data Fetching (`src/data.py`)
**What happens:**
1. Takes stock ticker (e.g., "AAPL")
2. Uses `yfinance` library to fetch from Yahoo Finance API:
   - Company info (name, price, market cap)
   - Balance sheet (assets, liabilities, debt)
   - Income statement (revenue, net income, earnings history)
   - Dividend history
3. Calculates ratios:
   - Current Ratio = Current Assets / Current Liabilities
   - P/E Ratio = Price / Earnings per Share
   - P/B Ratio = Price / Book Value per Share
4. Returns `FinancialData` object with all raw numbers

**Example Output:**
```
AAPL:
- Price: $279.67
- Revenue: $416.16B
- Current Assets: $147.96B
- Current Liabilities: $165.63B
- Current Ratio: 0.89
- P/E: 37.44
- Earnings History: [112B, 99B, 94B, 57B] (4 years)
```

---

### Step 2: Graham Criteria Analysis (`src/analyzer.py`)
**What happens:**
1. Takes `FinancialData` object
2. Runs each criterion check (mathematical comparisons):

**Defensive Investor (7 criteria):**
1. **Adequate Size**: Revenue > $500M? ✓ (AAPL: $416B)
2. **Current Ratio**: Current Ratio > 2.0? ✗ (AAPL: 0.89)
3. **Debt vs Working Capital**: LT Debt < Working Capital? ✗ (AAPL: LT Debt $78B > Working Capital -$17B)
4. **Earnings Stability**: 10 years positive? ✗ (AAPL: Only 4 years data)
5. **Dividend Record**: 20 years dividends? ✓ (AAPL: 20 years)
6. **Earnings Growth**: 33% growth over 10yr? ✗ (AAPL: Insufficient data)
7. **Valuation**: P/E < 15 AND P/B < 1.5? ✗ (AAPL: P/E 37.4, P/B 56.0)

3. Creates `CriteriaResult` for each:
   - `passed`: True/False
   - `actual_value`: "0.89"
   - `required_value`: "> 2.0"
   - `explanation`: "Graham requires 2:1 ratio for safety..."

4. Calculates score: 2/7 = 29%
5. Returns `AnalysisResult` with all criteria results

**Example Output:**
```
AnalysisResult:
- ticker: "AAPL"
- passed_count: 2
- total_count: 7
- score_percentage: 28.6%
- criteria_results: [
    CriteriaResult(name="Adequate Size", passed=True, actual_value="$416.16B", ...),
    CriteriaResult(name="Current Ratio", passed=False, actual_value="0.89", ...),
    ...
  ]
```

---

### Step 3: AI Verdict Generation (`src/agent.py`)
**What happens:**
1. Takes `AnalysisResult` object
2. Builds prompt with all the data
3. Sends to xAI/Grok API

**System Prompt (sent first):**
```
You are Benjamin Graham, the father of value investing and author of 
'The Intelligent Investor'. You speak with authority on investment principles, 
emphasizing margin of safety, fundamental analysis, and disciplined investing. 
You explain your criteria clearly, referencing your philosophy throughout. 
Be direct, educational, and avoid unnecessary jargon.
```

**User Prompt (the actual question):**
```
Analyze this stock using my Defensive Investor criteria and provide a comprehensive verdict.

STOCK: AAPL (Apple Inc.)
STRATEGY: Defensive Investor
SCORE: 2/7 criteria passed (29%)
RECOMMENDATION: AVOID - Does not meet Graham's safety standards

DETAILED CRITERIA RESULTS:
- Adequate Size of Enterprise: ✓ PASS
  Actual: $416.16B
  Required: > $500.00M
- Strong Financials: Current Ratio: ✗ FAIL
  Actual: 0.89
  Required: > 2.0
- Strong Financials: Debt vs Working Capital: ✗ FAIL
  Actual: LT Debt: $78.33B, Working Capital: $-17.67B
  Required: Long-term Debt < Net Current Assets
- Earnings Stability (10 Years): ✗ FAIL
  Actual: 4 positive years out of 4 available
  Required: 10 consecutive years of positive earnings
- Dividend Record (20 Years): ✓ PASS
  Actual: 20 years of dividends (data for 20 years)
  Required: 20 consecutive years of dividend payments
- Earnings Growth (10-Year): ✗ FAIL
  Actual: Insufficient data
  Required: > 33% growth using 3-year averages
- Moderate Valuation (P/E & P/B): ✗ FAIL
  Actual: P/E: 37.4, P/B: 56.03, Product: 2097.7
  Required: P/E < 15 AND P/B < 1.5, OR P/E × P/B < 22.5

Please provide:
1. An overall assessment (2-3 sentences) on whether this stock meets my standards
2. For each FAILED criterion, explain WHY it matters and what the risk is
3. For significant PASSED criteria, acknowledge the strength
4. A final verdict: Would I, Benjamin Graham, consider this a suitable investment for a defensive investor?

Be specific about the numbers and ratios. Reference my philosophy from 'The Intelligent Investor' where relevant.
```

4. AI responds with narrative explanation
5. Returns the text verdict

---

## Why Many Stocks Fail

**Graham's criteria are VERY strict** - designed for 1970s value investing:

1. **Current Ratio > 2.0**: Most modern companies don't hold that much cash
2. **P/E < 15**: Most growth stocks trade at 20-40+ P/E
3. **10 years earnings history**: Many companies are newer
4. **20 years dividends**: Many tech companies don't pay dividends

**This is EXPECTED!** Graham's criteria were designed to find:
- Undervalued, stable, dividend-paying companies
- Companies trading below book value
- Companies with strong balance sheets

Modern tech stocks (AAPL, GOOGL, etc.) fail because they:
- Trade at high multiples (growth premium)
- Don't hold excess cash (they reinvest)
- Are relatively new companies

---

## How to Verify Accuracy

1. **Check Raw Data**: Use "Data Verification" expandable section
2. **Verify Calculations**: Check each criterion manually
3. **Compare to Known Graham Stocks**: Test with classic value stocks (BRK-B, KO, JNJ)
4. **Check Yahoo Finance**: Verify numbers match what Yahoo shows

