# Testing Guide - Verify App Accuracy

## Quick Answer: Why So Many "AVOID" Results?

**This is CORRECT and EXPECTED!** Graham's criteria are extremely strict:
- Designed for 1970s conservative investing
- Most modern stocks trade at valuations he would reject
- Growth stocks (AAPL, TSLA) will almost always fail
- Even good dividend stocks may only score 40-60%

A stock scoring **70%+ is rare** in today's market!

---

## Automated Test Scripts

### 1. Accuracy Validation Test (`test_accuracy.py`)

Tests 6 diverse stocks with expected behaviors:

```bash
cd "/Users/jameslarosa/Benjamin Graham AI"
source venv/bin/activate
python test_accuracy.py
```

**What it does:**
- Tests growth stocks (AAPL, TSLA) - expects 0-40% scores
- Tests dividend stocks (KO, JNJ) - expects 40-70% scores  
- Tests value stocks (WMT, BRK-B) - expects 30-60% scores
- Validates data quality (price > 0, revenue > 0, etc.)
- Shows detailed criteria breakdown for each stock

**Expected output:**
```
✅ TEST PASSED - 6/6 stocks analyzed successfully
Growth stocks scored low (correct)
Value stocks scored higher (correct)
```

### 2. Quick Single-Stock Validation

```bash
python test_accuracy.py AAPL
```

**What it does:**
- Fetches data for the ticker
- Shows all raw numbers
- Validates data quality
- Provides Yahoo Finance link to manually verify

### 3. Batch Test (30+ Stocks) (`batch_test.py`)

Tests the app with 30+ stocks in parallel:

```bash
python batch_test.py
```

**What it does:**
- Analyzes 30+ diverse stocks (tech, dividends, value, financials)
- Runs in parallel (5 workers) to test concurrent processing
- Shows score distribution
- Identifies top and bottom performers
- Validates success rate (should be 80%+)

**Expected output:**
```
✅ BATCH TEST PASSED - 28/30 stocks analyzed successfully
Average Score: 35% (Expected - modern stocks fail Graham's criteria)
Top Performer: KO (68%) - Dividend stock
Bottom Performer: TSLA (14%) - Growth stock
```

### 4. Custom Ticker Batch Test

```bash
python batch_test.py "AAPL,MSFT,GOOGL,KO,PEP,JNJ"
```

---

## Manual Verification Steps

### Step 1: Test with Known Stock

Pick a stock you know well:

```bash
python test_accuracy.py AAPL
```

Compare output to Yahoo Finance:
1. Go to https://finance.yahoo.com/quote/AAPL
2. Check if **price** matches
3. Check if **P/E ratio** matches
4. Check if **market cap** is close

### Step 2: Run the UI Test

1. Open the Streamlit UI (http://localhost:8501)
2. Test with these stocks (paste in text area):
   ```
   AAPL
   KO
   JNJ
   ```
3. Click **"Run Graham Analysis"**
4. Check results:
   - **AAPL**: Should score low (20-40%) - Growth stock
   - **KO**: Should score higher (40-60%) - Dividend stock
   - **JNJ**: Should score higher (40-60%) - Healthcare dividend
5. Click **"🔍 Data Verification"** to verify raw numbers
6. Click **"🤖 AI Prompt Debug"** to see exact prompt sent to Grok

### Step 3: Verify Calculations

For any stock, manually verify key calculations:

**Current Ratio:**
```
Formula: Current Assets / Current Liabilities
AAPL: $147.96B / $165.63B = 0.89
Required: > 2.0
Result: FAIL ✓ (Correct)
```

**P/E Ratio:**
```
AAPL P/E: 37.4 (from Yahoo Finance)
Required: < 15
Result: FAIL ✓ (Correct)
```

---

## What to Expect

### Growth/Tech Stocks (AAPL, MSFT, GOOGL, NVDA, TSLA)
- **Expected Score**: 0-40%
- **Expected Recommendation**: AVOID or CAUTION
- **Why**: High P/E ratios, low current ratios, focused on growth not dividends
- **Graham's View**: Too expensive, insufficient margin of safety

### Dividend Aristocrats (KO, PEP, JNJ, PG, MMM)
- **Expected Score**: 40-70%
- **Expected Recommendation**: HOLD or BUY (rare)
- **Why**: Better fundamentals, consistent dividends, more stable
- **Graham's View**: More aligned with defensive investing

### Value/Financial Stocks (JPM, BAC, WMT)
- **Expected Score**: 30-60%
- **Expected Recommendation**: CAUTION or HOLD
- **Why**: Lower multiples but may have debt issues
- **Graham's View**: Mixed - some strengths, some concerns

### True Graham Stocks
- **Expected Score**: 70%+
- **Expected Recommendation**: STRONG BUY or BUY
- **Reality**: Very rare in today's market!

---

## Troubleshooting

### Issue: All stocks showing 0% score

**Problem**: Data not being fetched
**Solution**: 
1. Check internet connection
2. Run `python test_accuracy.py AAPL` to see detailed logs
3. Verify Yahoo Finance is accessible

### Issue: Scores seem too high/low

**Problem**: Criteria might be misconfigured
**Solution**:
1. Check `src/analyzer.py` for threshold values
2. Run `python test_accuracy.py` to see expected vs actual
3. Compare calculations manually using "Data Verification" in UI

### Issue: Data fetch takes forever

**Problem**: Rate limiting or network issues
**Solution**:
1. Reduce parallel workers in UI (from 5 to 2-3)
2. Add delays between requests
3. Check if Yahoo Finance is blocking requests

### Issue: AI verdicts don't match criteria

**Problem**: AI not understanding the rules
**Solution**:
1. Check `src/agent.py` - rules should be in prompt
2. Click "AI Prompt Debug" in UI to verify full rules are sent
3. Verify system prompt sets Benjamin Graham persona

---

## Success Criteria

The app is working correctly if:

1. ✅ **Data fetches successfully** (80%+ success rate)
2. ✅ **Growth stocks score low** (0-40%)
3. ✅ **Value/dividend stocks score higher** (40-70%)
4. ✅ **Calculations are accurate** (verified against Yahoo Finance)
5. ✅ **Batch processing works** (30+ stocks complete without crashes)
6. ✅ **Most stocks show AVOID/CAUTION** (Graham's criteria are strict!)

---

## Run All Tests

```bash
cd "/Users/jameslarosa/Benjamin Graham AI"
source venv/bin/activate

# Test 1: Accuracy validation (6 stocks)
python test_accuracy.py

# Test 2: Single stock verification
python test_accuracy.py AAPL

# Test 3: Batch test (30+ stocks)
python batch_test.py

# Test 4: Custom tickers
python batch_test.py "AAPL,MSFT,KO,PEP,JNJ,WMT,JPM,BAC"
```

Expected total time: 2-5 minutes for all tests

