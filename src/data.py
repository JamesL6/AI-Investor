"""
Data Layer for Benjamin Graham Intelligent Investor Agent.
Fetches financial data from Yahoo Finance using yfinance.
"""

import yfinance as yf
import pandas as pd
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class FinancialData:
    """Container for all financial data needed for Graham and Buffett analysis."""
    
    ticker: str
    company_name: str
    
    # Current Price Data
    current_price: float
    market_cap: float
    
    # Balance Sheet Items
    total_current_assets: float
    total_current_liabilities: float
    total_long_term_debt: float
    total_debt: float
    total_stockholder_equity: float
    book_value_per_share: float
    net_tangible_assets: float
    intangible_assets: float
    total_assets: float
    
    # Income Statement Items
    total_revenue: float
    net_income: float
    earnings_per_share: float
    gross_profit: float
    operating_income: float  # EBIT
    interest_expense: float
    depreciation_amortization: float
    sga_expense: float  # Selling, General & Administrative
    
    # Historical Data
    earnings_history: List[float]  # Last 10 years of net income
    dividend_history: List[float]  # Last 20 years of dividends
    revenue_history: List[float]   # Last 10 years of revenue
    roe_history: List[float]       # Last 10 years of ROE (for Buffett)
    
    # Calculated Ratios - Graham
    current_ratio: float
    pe_ratio: float
    pb_ratio: float
    dividend_yield: float
    
    # Calculated Ratios - Buffett
    roe: float                    # Return on Equity
    roic: float                   # Return on Invested Capital
    gross_margin: float           # Gross Profit / Revenue
    net_margin: float             # Net Income / Revenue
    debt_to_equity: float         # Total Debt / Equity
    interest_coverage: float      # EBIT / Interest Expense
    owner_earnings: float         # Net Income + D&A - Maintenance CapEx
    free_cash_flow: float         # Operating Cash Flow - CapEx
    fcf_yield: float              # FCF / Market Cap
    
    # Metadata
    data_date: str
    years_of_earnings_data: int
    years_of_dividend_data: int


def get_financial_data(ticker_symbol: str) -> Optional[FinancialData]:
    """
    Fetch all financial data needed for Benjamin Graham analysis.
    
    Args:
        ticker_symbol: Stock ticker (e.g., 'AAPL', 'JNJ')
        
    Returns:
        FinancialData object or None if data cannot be fetched
    """
    import time
    
    try:
        # Create ticker object (disable cache to ensure fresh data)
        ticker = yf.Ticker(ticker_symbol)
        
        # Fetch info (this makes an API call)
        print(f"[{ticker_symbol}] Fetching company info from Yahoo Finance...")
        import time
        time.sleep(0.5)  # Small delay to avoid rate limiting
        info = ticker.info
        
        # Wait a moment for API to respond
        if not info:
            time.sleep(1)
            info = ticker.info
        
        # Validate we got real info
        if not info or len(info) < 10:
            print(f"[{ticker_symbol}] Error: Invalid or empty info data")
            return None
        
        # Get financial statements (these make API calls)
        print(f"[{ticker_symbol}] Fetching balance sheet from Yahoo Finance...")
        time.sleep(0.5)  # Rate limiting protection
        balance_sheet = ticker.balance_sheet
        
        print(f"[{ticker_symbol}] Fetching income statement from Yahoo Finance...")
        time.sleep(0.5)  # Rate limiting protection
        income_stmt = ticker.income_stmt
        
        # Validate we have data
        if balance_sheet.empty:
            print(f"[{ticker_symbol}] Error: Balance sheet is empty")
            return None
        
        if income_stmt.empty:
            print(f"[{ticker_symbol}] Error: Income statement is empty")
            return None
        
        print(f"[{ticker_symbol}] Successfully fetched financial statements")
        print(f"[{ticker_symbol}] Balance sheet columns: {list(balance_sheet.columns)}")
        print(f"[{ticker_symbol}] Income statement columns: {list(income_stmt.columns)}")
        
        # Extract company name
        company_name = info.get('longName', info.get('shortName', ticker_symbol))
        
        # Current price and market cap
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        market_cap = info.get('marketCap', 0)
        
        # Validate we got real price data
        if current_price <= 0:
            print(f"[{ticker_symbol}] Warning: Invalid price data (price={current_price})")
            # Try alternative price sources
            current_price = info.get('regularMarketPreviousClose', info.get('previousClose', 0))
            if current_price <= 0:
                print(f"[{ticker_symbol}] Error: No valid price data found")
                return None
        
        print(f"[{ticker_symbol}] Price: ${current_price:.2f}, Market Cap: ${market_cap:,.0f}")
        
        # Balance sheet items (most recent)
        total_current_assets = _safe_get_value(balance_sheet, 'Current Assets')
        total_current_liabilities = _safe_get_value(balance_sheet, 'Current Liabilities')
        total_long_term_debt = _safe_get_value(balance_sheet, 'Long Term Debt')
        total_debt = _safe_get_value(balance_sheet, 'Total Debt')
        total_stockholder_equity = (
            _safe_get_value(balance_sheet, 'Stockholders Equity') or
            _safe_get_value(balance_sheet, 'Common Stock Equity')
        )
        total_assets = _safe_get_value(balance_sheet, 'Total Assets')
        total_liabilities = _safe_get_value(balance_sheet, 'Total Liabilities Net Minority Interest')

        # Use yfinance's pre-calculated Net Tangible Assets (assets minus goodwill/intangibles minus liabilities)
        net_tangible_assets = _safe_get_value(balance_sheet, 'Net Tangible Assets')
        if net_tangible_assets == 0:
            # Fallback: compute manually (less accurate — intangibles may not be captured)
            intangible_assets = _safe_get_value(balance_sheet, 'Intangible Assets')
            net_tangible_assets = total_assets - intangible_assets - total_liabilities
        intangible_assets = total_assets - total_liabilities - net_tangible_assets
        
        # Book value per share
        shares_outstanding = info.get('sharesOutstanding', 1)
        book_value_per_share = total_stockholder_equity / shares_outstanding if shares_outstanding > 0 else 0
        
        # Income statement items
        total_revenue = _safe_get_value(income_stmt, 'Total Revenue')
        net_income = _safe_get_value(income_stmt, 'Net Income')
        earnings_per_share = info.get('trailingEps', 0)
        gross_profit = _safe_get_value(income_stmt, 'Gross Profit')
        operating_income = _safe_get_value(income_stmt, 'Operating Income')  # EBIT
        interest_expense = _safe_get_interest_expense(income_stmt)
        depreciation_amortization = _safe_get_value(income_stmt, 'Depreciation And Amortization')
        sga_expense = _safe_get_value(income_stmt, 'Selling General And Administration')
        
        # Historical earnings (up to 10 years)
        earnings_history = _get_historical_values(income_stmt, 'Net Income')
        revenue_history = _get_historical_values(income_stmt, 'Total Revenue')
        
        # Historical dividends (up to 20 years)
        print(f"[{ticker_symbol}] Fetching dividend history from Yahoo Finance...")
        time.sleep(0.5)  # Rate limiting protection
        dividend_history = _get_dividend_history(ticker)
        
        # Calculate ratios - Graham
        current_ratio = (total_current_assets / total_current_liabilities 
                        if total_current_liabilities > 0 else 0)
        
        pe_ratio = info.get('trailingPE', 0) or 0
        pb_ratio = info.get('priceToBook', 0) or 0
        # trailingAnnualDividendYield is a proper decimal (e.g., 0.0039 = 0.39%)
        # dividendYield in yfinance is a scaled value (0.39 = 0.39%) — do NOT use it
        dividend_yield = info.get('trailingAnnualDividendYield', 0) or 0
        
        # Calculate ratios - Buffett
        # ROE = Net Income / Shareholders Equity
        roe = (net_income / total_stockholder_equity * 100) if total_stockholder_equity > 0 else 0
        
        # ROIC = EBIT * (1 - Tax Rate) / Invested Capital
        tax_rate = 0.21  # Approximate corporate tax rate
        nopat = operating_income * (1 - tax_rate) if operating_income > 0 else 0
        # Use yfinance's Invested Capital directly if available, else calculate
        invested_capital = _safe_get_value(balance_sheet, 'Invested Capital')
        if invested_capital == 0:
            cash = _safe_get_value(balance_sheet, 'Cash And Cash Equivalents')
            invested_capital = total_assets - total_current_liabilities - cash
        roic = (nopat / invested_capital * 100) if invested_capital > 0 else 0
        
        # Gross Margin = Gross Profit / Revenue
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Net Margin = Net Income / Revenue
        net_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # Debt to Equity
        debt_to_equity = (total_debt / total_stockholder_equity) if total_stockholder_equity > 0 else float('inf')
        
        # Interest Coverage = EBIT / Interest Expense
        interest_coverage = (operating_income / interest_expense) if interest_expense > 0 else float('inf')
        
        # Owner Earnings = Net Income + D&A - Maintenance CapEx (estimate as 80% of D&A)
        maintenance_capex = depreciation_amortization * 0.8  # Conservative estimate
        owner_earnings = net_income + depreciation_amortization - maintenance_capex
        
        # Free Cash Flow (from info if available, otherwise estimate)
        free_cash_flow = info.get('freeCashflow', 0) or 0
        if free_cash_flow == 0:
            operating_cash_flow = info.get('operatingCashflow', 0) or 0
            capex = abs(info.get('capitalExpenditures', 0) or 0)
            free_cash_flow = operating_cash_flow - capex
        
        # FCF Yield = FCF / Market Cap
        fcf_yield = (free_cash_flow / market_cap * 100) if market_cap > 0 else 0
        
        # Historical ROE for Buffett analysis
        roe_history = _calculate_historical_roe(income_stmt, balance_sheet)
        
        # Final validation - ensure we have meaningful data
        if total_revenue <= 0:
            print(f"[{ticker_symbol}] Error: Invalid revenue data (revenue={total_revenue})")
            return None
        
        if total_current_assets <= 0 and total_current_liabilities <= 0:
            print(f"[{ticker_symbol}] Warning: Missing balance sheet data")
        
        print(f"[{ticker_symbol}] Data validation complete:")
        print(f"[{ticker_symbol}]   Revenue: ${total_revenue:,.0f}")
        print(f"[{ticker_symbol}]   Net Income: ${net_income:,.0f}")
        print(f"[{ticker_symbol}]   Current Assets: ${total_current_assets:,.0f}")
        print(f"[{ticker_symbol}]   Earnings History Years: {len(earnings_history)}")
        print(f"[{ticker_symbol}]   Dividend History Years: {len(dividend_history)}")
        
        return FinancialData(
            ticker=ticker_symbol.upper(),
            company_name=company_name,
            current_price=current_price,
            market_cap=market_cap,
            total_current_assets=total_current_assets,
            total_current_liabilities=total_current_liabilities,
            total_long_term_debt=total_long_term_debt,
            total_debt=total_debt,
            total_stockholder_equity=total_stockholder_equity,
            book_value_per_share=book_value_per_share,
            net_tangible_assets=net_tangible_assets,
            intangible_assets=intangible_assets,
            total_assets=total_assets,
            total_revenue=total_revenue,
            net_income=net_income,
            earnings_per_share=earnings_per_share,
            gross_profit=gross_profit,
            operating_income=operating_income,
            interest_expense=interest_expense,
            depreciation_amortization=depreciation_amortization,
            sga_expense=sga_expense,
            earnings_history=earnings_history,
            dividend_history=dividend_history,
            revenue_history=revenue_history,
            roe_history=roe_history,
            current_ratio=current_ratio,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            dividend_yield=dividend_yield,
            roe=roe,
            roic=roic,
            gross_margin=gross_margin,
            net_margin=net_margin,
            debt_to_equity=debt_to_equity,
            interest_coverage=interest_coverage,
            owner_earnings=owner_earnings,
            free_cash_flow=free_cash_flow,
            fcf_yield=fcf_yield,
            data_date=datetime.now().strftime("%Y-%m-%d"),
            years_of_earnings_data=len(earnings_history),
            years_of_dividend_data=len(dividend_history)
        )
        
    except Exception as e:
        import traceback
        print(f"[{ticker_symbol}] Error fetching data: {e}")
        print(f"[{ticker_symbol}] Traceback:")
        traceback.print_exc()
        return None


def _safe_get_value(df: pd.DataFrame, row_name: str, column_idx: int = 0) -> float:
    """Safely extract a value from a DataFrame."""
    try:
        if row_name in df.index:
            value = df.loc[row_name].iloc[column_idx]
            return float(value) if pd.notna(value) else 0.0
        return 0.0
    except (IndexError, KeyError):
        return 0.0


def _safe_get_interest_expense(income_stmt: pd.DataFrame) -> float:
    """
    Get interest expense, trying multiple field names and column indices.
    yfinance sometimes has NaN for the most recent year(s) for this field.
    """
    field_names = ['Interest Expense', 'Interest Expense Non Operating']
    for col_idx in range(min(4, len(income_stmt.columns))):
        for field in field_names:
            value = abs(_safe_get_value(income_stmt, field, col_idx))
            if value > 0:
                return value
    return 0.0


def _get_historical_values(df: pd.DataFrame, row_name: str) -> List[float]:
    """Get all historical values for a row (up to available columns)."""
    try:
        if row_name in df.index:
            values = df.loc[row_name].dropna().tolist()
            return [float(v) for v in values]
        return []
    except Exception:
        return []


def _get_dividend_history(ticker: yf.Ticker) -> List[float]:
    """Get annual dividend history for up to 20 years."""
    try:
        dividends = ticker.dividends
        if dividends.empty:
            return []
        
        # Group by year and sum
        dividends.index = pd.to_datetime(dividends.index)
        annual_dividends = dividends.groupby(dividends.index.year).sum()
        
        # Get last 20 years
        return annual_dividends.tail(20).tolist()
    except Exception:
        return []


def _calculate_historical_roe(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> List[float]:
    """Calculate historical ROE values for each available year."""
    roe_history = []
    try:
        # Get the number of years we have data for
        years = min(len(income_stmt.columns), len(balance_sheet.columns))
        
        for i in range(years):
            net_income = _safe_get_value(income_stmt, 'Net Income', i)
            equity = _safe_get_value(balance_sheet, 'Stockholders Equity', i)
            
            if equity > 0:
                roe = (net_income / equity) * 100
                roe_history.append(roe)
            else:
                roe_history.append(0)
        
        return roe_history
    except Exception:
        return []


def format_currency(value: float) -> str:
    """Format large numbers in readable format (e.g., $1.5B)."""
    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

