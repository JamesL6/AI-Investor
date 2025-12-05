"""
Debug and verification tools for Benjamin Graham analysis.
Shows exact prompts, calculations, and data flow.
"""

from src.analyzer import AnalysisResult, InvestorType
from src.agent import _build_prompt, GRAHAM_SYSTEM_PROMPT
from src.data import FinancialData


def show_analysis_breakdown(analysis: AnalysisResult, financial_data: FinancialData) -> str:
    """
    Generate a detailed breakdown showing all calculations and data.
    Useful for verifying accuracy.
    """
    lines = [
        "=" * 80,
        f"DETAILED ANALYSIS BREAKDOWN: {analysis.ticker}",
        "=" * 80,
        "",
        "📊 RAW FINANCIAL DATA FROM YAHOO FINANCE:",
        "-" * 80,
        f"Company: {financial_data.company_name}",
        f"Current Price: ${financial_data.current_price:,.2f}",
        f"Market Cap: ${financial_data.market_cap:,.0f}",
        "",
        "Balance Sheet:",
        f"  Current Assets: ${financial_data.total_current_assets:,.0f}",
        f"  Current Liabilities: ${financial_data.total_current_liabilities:,.0f}",
        f"  Long-term Debt: ${financial_data.total_long_term_debt:,.0f}",
        f"  Total Debt: ${financial_data.total_debt:,.0f}",
        f"  Stockholders Equity: ${financial_data.total_stockholder_equity:,.0f}",
        f"  Net Tangible Assets: ${financial_data.net_tangible_assets:,.0f}",
        "",
        "Income Statement:",
        f"  Total Revenue: ${financial_data.total_revenue:,.0f}",
        f"  Net Income: ${financial_data.net_income:,.0f}",
        f"  Earnings per Share: ${financial_data.earnings_per_share:.2f}",
        "",
        "Calculated Ratios:",
        f"  Current Ratio: {financial_data.current_ratio:.2f} = {financial_data.total_current_assets:,.0f} / {financial_data.total_current_liabilities:,.0f}",
        f"  P/E Ratio: {financial_data.pe_ratio:.2f}",
        f"  P/B Ratio: {financial_data.pb_ratio:.2f}",
        f"  Dividend Yield: {financial_data.dividend_yield*100:.2f}%",
        "",
        "Historical Data:",
        f"  Earnings History ({financial_data.years_of_earnings_data} years): {[f'${e:,.0f}' for e in financial_data.earnings_history[:5]]}",
        f"  Dividend History ({financial_data.years_of_dividend_data} years): {[f'${d:.2f}' for d in financial_data.dividend_history[:5]]}",
        "",
        "=" * 80,
        "🔍 CRITERIA EVALUATION:",
        "=" * 80,
        "",
    ]
    
    strategy = "Defensive" if analysis.investor_type == InvestorType.DEFENSIVE else "Enterprising"
    lines.append(f"Strategy: {strategy} Investor ({analysis.total_count} criteria)")
    lines.append("")
    
    for i, cr in enumerate(analysis.criteria_results, 1):
        status = "✅ PASS" if cr.passed else "❌ FAIL"
        lines.append(f"{i}. {cr.name}: {status}")
        lines.append(f"   Actual Value: {cr.actual_value}")
        lines.append(f"   Required: {cr.required_value}")
        lines.append(f"   Explanation: {cr.explanation}")
        lines.append("")
    
    lines.extend([
        "=" * 80,
        "📈 SCORING:",
        "-" * 80,
        f"Passed: {analysis.passed_count}/{analysis.total_count}",
        f"Score: {analysis.score_percentage:.1f}%",
        f"Recommendation: {analysis.overall_recommendation}",
        "",
    ])
    
    # Show calculations for key criteria
    lines.extend([
        "=" * 80,
        "🧮 MANUAL CALCULATION VERIFICATION:",
        "-" * 80,
    ])
    
    if analysis.investor_type == InvestorType.DEFENSIVE:
        # Current Ratio calculation
        current_ratio = financial_data.current_ratio
        lines.append(f"1. Current Ratio Check:")
        lines.append(f"   Formula: Current Assets / Current Liabilities")
        lines.append(f"   Calculation: ${financial_data.total_current_assets:,.0f} / ${financial_data.total_current_liabilities:,.0f} = {current_ratio:.2f}")
        lines.append(f"   Required: > 2.0")
        lines.append(f"   Result: {'✅ PASS' if current_ratio >= 2.0 else '❌ FAIL'} ({current_ratio:.2f} {'>=' if current_ratio >= 2.0 else '<'} 2.0)")
        lines.append("")
        
        # Debt vs Working Capital
        working_capital = financial_data.total_current_assets - financial_data.total_current_liabilities
        lines.append(f"2. Debt vs Working Capital:")
        lines.append(f"   Working Capital = Current Assets - Current Liabilities")
        lines.append(f"   Calculation: ${financial_data.total_current_assets:,.0f} - ${financial_data.total_current_liabilities:,.0f} = ${working_capital:,.0f}")
        lines.append(f"   Long-term Debt: ${financial_data.total_long_term_debt:,.0f}")
        lines.append(f"   Required: LT Debt < Working Capital")
        lines.append(f"   Result: {'✅ PASS' if financial_data.total_long_term_debt < working_capital else '❌ FAIL'} (${financial_data.total_long_term_debt:,.0f} {'<' if financial_data.total_long_term_debt < working_capital else '>='} ${working_capital:,.0f})")
        lines.append("")
        
        # P/E and P/B
        pe = financial_data.pe_ratio
        pb = financial_data.pb_ratio
        pe_pb_product = pe * pb if pe > 0 and pb > 0 else 0
        traditional_pass = pe < 15 and pb < 1.5
        combined_pass = pe_pb_product < 22.5
        lines.append(f"3. Valuation Check:")
        lines.append(f"   P/E Ratio: {pe:.2f} (Required: < 15)")
        lines.append(f"   P/B Ratio: {pb:.2f} (Required: < 1.5)")
        lines.append(f"   P/E × P/B: {pe_pb_product:.2f} (Required: < 22.5)")
        lines.append(f"   Traditional Rule: P/E < 15 AND P/B < 1.5 = {'✅' if traditional_pass else '❌'}")
        lines.append(f"   Combined Rule: P/E × P/B < 22.5 = {'✅' if combined_pass else '❌'}")
        lines.append(f"   Result: {'✅ PASS' if (traditional_pass or combined_pass) else '❌ FAIL'}")
        lines.append("")
    
    return "\n".join(lines)


def show_ai_prompt(analysis: AnalysisResult) -> str:
    """
    Show the exact prompt being sent to the AI.
    """
    prompt = _build_prompt(analysis)
    
    return f"""
{'=' * 80}
AI PROMPT BREAKDOWN
{'=' * 80}

SYSTEM PROMPT (sent first to set AI personality):
{'-' * 80}
{GRAHAM_SYSTEM_PROMPT}

{'-' * 80}

USER PROMPT (the actual question/data):
{'-' * 80}
{prompt}

{'-' * 80}

This prompt is sent to the xAI Grok API, which responds with a narrative
explanation in Benjamin Graham's voice analyzing the stock.
"""

