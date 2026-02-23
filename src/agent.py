"""
AI Agent for Benjamin Graham Intelligent Investor.
Generates narrative explanations using an LLM (supports Grok and Gemini).
"""

import os
import time
from typing import Optional
from src.analyzer import AnalysisResult, InvestorType
from src.models import get_llm_response, AVAILABLE_MODELS

# System prompt for Benjamin Graham persona
GRAHAM_SYSTEM_PROMPT = (
    "You are Benjamin Graham, the father of value investing and author of "
    "'The Intelligent Investor'. You speak with authority on investment principles, "
    "emphasizing margin of safety, fundamental analysis, and disciplined investing. "
    "You explain your criteria clearly, referencing your philosophy throughout. "
    "Be direct, educational, and avoid unnecessary jargon."
)

# System prompt for Warren Buffett persona
BUFFETT_SYSTEM_PROMPT = (
    "You are Warren Buffett, the Oracle of Omaha and Chairman of Berkshire Hathaway. "
    "You are Benjamin Graham's most famous student but have evolved his teachings to focus on "
    "wonderful businesses at fair prices rather than fair businesses at wonderful prices. "
    "You emphasize durable competitive advantages (moats), owner earnings over GAAP metrics, "
    "and long-term holding periods. You speak plainly, use folksy analogies, and reference "
    "your annual shareholder letters. You despise EBITDA ('bullshit earnings'), excessive debt, "
    "and management that doesn't think like owners. Be direct, wise, and occasionally witty."
)

# System prompt for Devil's Advocate contrarian persona
CONTRARIAN_DEVIL_SYSTEM_PROMPT = (
    "You are a contrarian investment analyst. Your job is to argue the exact opposite of the "
    "prevailing verdict on a stock — if the analysis says BUY, you argue SELL; if it says SELL, "
    "you argue BUY. Base your argument strictly on the quantitative data provided. Do not speculate "
    "about news, macro events, or information not present in the numbers. Be concise, direct, and "
    "analytical. No buzzwords. No hedging. Make the strongest possible opposing case in 3-5 short "
    "paragraphs, covering past performance, present condition, and future trajectory implied by the data."
)

# System prompt for Skeptic contrarian persona
CONTRARIAN_SKEPTIC_SYSTEM_PROMPT = (
    "You are a rigorous skeptic reviewing an investment analysis. Your job is to find the holes, "
    "the hidden risks, the assumptions that might be wrong, and the things the analysis glosses over. "
    "You are not arguing for or against the investment — you are asking hard questions and exposing "
    "weaknesses in the methodology and the data. Base your critique strictly on the quantitative data "
    "provided. Do not speculate about news or events not present in the numbers. Be concise, precise, "
    "and unsparing. Identify 3-5 specific concerns in short, direct paragraphs."
)


def get_llm_verdict(
    analysis: AnalysisResult, 
    model_id: str = "grok-3-fast",
    api_key: Optional[str] = None
) -> str:
    """
    Generate a narrative verdict explaining the analysis results.
    
    Args:
        analysis: The complete analysis result from GrahamValidator
        model_id: Which model to use (from AVAILABLE_MODELS)
        api_key: API key (uses env var if not provided)
        
    Returns:
        A narrative explanation of the analysis
    """
    # Build the prompt with analysis data
    prompt = _build_prompt(analysis)
    
    # Choose system prompt based on investor type
    if analysis.investor_type == InvestorType.BUFFETT:
        system_prompt = BUFFETT_SYSTEM_PROMPT
    else:
        system_prompt = GRAHAM_SYSTEM_PROMPT
    
    try:
        return get_llm_response(
            model_id=model_id,
            system_prompt=system_prompt,
            user_prompt=prompt,
            api_key=api_key
        )
        
    except Exception as e:
        print(f"Warning: LLM call failed ({e}). Using fallback verdict.")
        return _generate_fallback_verdict(analysis)


def get_contrarian_analysis(
    analysis: AnalysisResult,
    model_id: str = "grok-3-fast",
    api_key: Optional[str] = None
) -> dict:
    """
    Generate Devil's Advocate and Skeptic contrarian perspectives on an analysis.

    Args:
        analysis: The complete analysis result from GrahamValidator
        model_id: Which model to use (from AVAILABLE_MODELS)
        api_key: API key (uses env var if not provided)

    Returns:
        Dict with keys 'devil' (str) and 'skeptic' (str)
    """
    prompt = _build_contrarian_prompt(analysis)

    result = {"devil": None, "skeptic": None}

    try:
        result["devil"] = get_llm_response(
            model_id=model_id,
            system_prompt=CONTRARIAN_DEVIL_SYSTEM_PROMPT,
            user_prompt=prompt,
            api_key=api_key
        )
    except Exception as e:
        result["devil"] = f"Devil's Advocate unavailable: {str(e)}"

    time.sleep(0.5)

    try:
        result["skeptic"] = get_llm_response(
            model_id=model_id,
            system_prompt=CONTRARIAN_SKEPTIC_SYSTEM_PROMPT,
            user_prompt=prompt,
            api_key=api_key
        )
    except Exception as e:
        result["skeptic"] = f"Skeptic unavailable: {str(e)}"

    return result


def _build_contrarian_prompt(analysis: AnalysisResult) -> str:
    """Build the shared prompt for both contrarian personas."""
    if analysis.investor_type == InvestorType.DEFENSIVE:
        strategy_name = "Defensive Investor"
    elif analysis.investor_type == InvestorType.ENTERPRISING:
        strategy_name = "Enterprising Investor"
    else:
        strategy_name = "Buffett Quality Investor"

    criteria_details = []
    for r in analysis.criteria_results:
        status = "PASS" if r.passed else "FAIL"
        criteria_details.append(
            f"- {r.name}: {status} | Actual: {r.actual_value} | Required: {r.required_value}"
        )
    criteria_text = "\n".join(criteria_details)

    return f"""STOCK: {analysis.ticker} ({analysis.company_name})
STRATEGY: {strategy_name}
SCORE: {analysis.passed_count}/{analysis.total_count} criteria passed ({analysis.score_percentage:.0f}%)
CURRENT VERDICT: {analysis.overall_recommendation}

CRITERIA RESULTS:
{criteria_text}

Use only the quantitative data above. Do not introduce outside information."""


def _build_prompt(analysis: AnalysisResult) -> str:
    """Build the prompt for the LLM with analysis data."""
    
    # Determine strategy name
    if analysis.investor_type == InvestorType.DEFENSIVE:
        strategy_name = "Defensive Investor"
    elif analysis.investor_type == InvestorType.ENTERPRISING:
        strategy_name = "Enterprising Investor"
    else:
        strategy_name = "Buffett Quality Investor"
    
    # Build criteria summary
    criteria_details = []
    for result in analysis.criteria_results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        criteria_details.append(
            f"- {result.name}: {status}\n"
            f"  Actual: {result.actual_value}\n"
            f"  Required: {result.required_value}"
        )
    
    criteria_text = "\n".join(criteria_details)
    
    # Explicit definitions of the strategies to ensure AI uses exact criteria
    defensive_rules = """
    DEFENSIVE INVESTOR CRITERIA (Strict Safety):
    1. Adequate Size: Sales > $500M (inflation adjusted)
    2. Strong Financials: Current Ratio > 2.0
    3. Financial Stability: Long-term Debt < Working Capital
    4. Earnings Stability: Positive earnings for last 10 consecutive years
    5. Dividend Record: Uninterrupted dividends for last 20 years
    6. Earnings Growth: At least 33% growth over last 10 years (using 3yr averages)
    7. Moderate Valuation: P/E < 15 AND P/B < 1.5 (or P/E*P/B < 22.5)
    """
    
    enterprising_rules = """
    ENTERPRISING INVESTOR CRITERIA (Aggressive/Bargain):
    1. Financial Condition: Current Ratio > 1.5
    2. Debt Stability: Total Debt < 110% of Net Current Assets (Working Capital)
    3. Earnings Stability: No earnings deficit in last 5 years
    4. Dividend Record: Currently pays some dividend
    5. Earnings Growth: Current earnings > Earnings 5 years ago
    6. Price: Price < 120% of Net Tangible Assets
    """
    
    buffett_rules = """
    BUFFETT QUALITY INVESTOR CRITERIA (Wonderful Businesses at Fair Prices):
    
    BUSINESS TENETS:
    1. Economic Moat: Gross Margin > 40% AND ROIC > 15% (durable competitive advantage)
    2. Consistent Earnings: No more than 2 negative earnings years (predictable business)
    3. Revenue Growth: CAGR > 5% (favorable long-term prospects)
    
    MANAGEMENT TENETS:
    4. High ROE (Not Debt-Driven): ROE > 15% average with Debt/Equity < 1.0 (rational capital allocation)
    5. Efficient Operations: SG&A < 30% of Gross Profit (lean, disciplined management)
    
    FINANCIAL TENETS:
    6. High Margins: Net Margin > 20% (pricing power from moat)
    7. Owner Earnings: Positive and Yield > 4.5% (true cash generation, not GAAP games)
    8. Low Debt: Debt/Equity < 0.5 AND can pay off debt in < 4 years (financial strength)
    9. Interest Coverage: > 5x (ample buffer for debt service)
    
    VALUE TENET:
    10. Reasonable Valuation: P/E < 15 OR FCF Yield > 4.5% (margin of safety)
    """
    
    # Select rules based on investor type
    if analysis.investor_type == InvestorType.DEFENSIVE:
        rules_text = defensive_rules
    elif analysis.investor_type == InvestorType.ENTERPRISING:
        rules_text = enterprising_rules
    else:
        rules_text = buffett_rules
    
    # Create appropriate prompt based on investor type
    if analysis.investor_type == InvestorType.BUFFETT:
        return f"""
Analyze this stock using my investment criteria and provide a comprehensive verdict.

CONTEXT:
{rules_text}

STOCK: {analysis.ticker} ({analysis.company_name})
STRATEGY: {strategy_name}
SCORE: {analysis.passed_count}/{analysis.total_count} criteria passed ({analysis.score_percentage:.0f}%)
RECOMMENDATION: {analysis.overall_recommendation}

DETAILED CRITERIA RESULTS:
{criteria_text}

Please provide:
1. An overall assessment (2-3 sentences) on whether this is a wonderful business I'd want to own forever
2. Evaluate the MOAT: Does this company have a durable competitive advantage? What kind (brand, cost, network, switching costs)?
3. For each FAILED criterion, explain WHY it matters from my perspective as an owner
4. For significant PASSED criteria, acknowledge why this makes it a quality business
5. A final verdict: Would I, Warren Buffett, consider adding this to my portfolio? Why or why not?

Remember: I look for businesses I understand, with honest and able management, and at a fair price. 
I'd rather buy a wonderful company at a fair price than a fair company at a wonderful price.
Reference my letters to shareholders where relevant.
"""
    else:
        return f"""
Analyze this stock using my {strategy_name} criteria and provide a comprehensive verdict.

CONTEXT:
{rules_text}

STOCK: {analysis.ticker} ({analysis.company_name})
STRATEGY: {strategy_name}
SCORE: {analysis.passed_count}/{analysis.total_count} criteria passed ({analysis.score_percentage:.0f}%)
RECOMMENDATION: {analysis.overall_recommendation}

DETAILED CRITERIA RESULTS:
{criteria_text}

Please provide:
1. An overall assessment (2-3 sentences) on whether this stock meets my standards
2. For each FAILED criterion, explain WHY it matters and what the risk is
3. For significant PASSED criteria, acknowledge the strength
4. A final verdict: Would I, Benjamin Graham, consider this a suitable investment for a {strategy_name.lower()}?

Be specific about the numbers and ratios. Reference my philosophy from 'The Intelligent Investor' where relevant.
"""


def _generate_fallback_verdict(analysis: AnalysisResult) -> str:
    """Generate a verdict without LLM when API is unavailable."""
    
    if analysis.investor_type == InvestorType.DEFENSIVE:
        strategy_name = "Defensive Investor"
        analyst_name = "GRAHAM"
    elif analysis.investor_type == InvestorType.ENTERPRISING:
        strategy_name = "Enterprising Investor"
        analyst_name = "GRAHAM"
    else:
        strategy_name = "Buffett Quality Investor"
        analyst_name = "BUFFETT"
    
    lines = [
        f"\n{'='*60}",
        f"{analyst_name} ANALYSIS VERDICT: {analysis.ticker}",
        f"{'='*60}",
        f"\nStrategy: {strategy_name}",
        f"Score: {analysis.passed_count}/{analysis.total_count} criteria passed ({analysis.score_percentage:.0f}%)",
        f"\nRecommendation: {analysis.overall_recommendation}",
        f"\n{'-'*60}",
        "CRITERIA BREAKDOWN:",
        f"{'-'*60}"
    ]
    
    # Group by passed/failed
    passed = [r for r in analysis.criteria_results if r.passed]
    failed = [r for r in analysis.criteria_results if not r.passed]
    
    if passed:
        lines.append("\n✓ STRENGTHS (Criteria Passed):")
        for r in passed:
            lines.append(f"\n  • {r.name}")
            lines.append(f"    Value: {r.actual_value}")
            lines.append(f"    → {r.explanation[:150]}...")
    
    if failed:
        lines.append("\n✗ CONCERNS (Criteria Failed):")
        for r in failed:
            lines.append(f"\n  • {r.name}")
            lines.append(f"    Value: {r.actual_value} (Required: {r.required_value})")
            lines.append(f"    → {r.explanation[:150]}...")
    
    lines.append(f"\n{'='*60}")
    
    # Final summary based on score and investor type
    if analysis.investor_type == InvestorType.BUFFETT:
        if analysis.score_percentage >= 70:
            lines.append(
                "\nWARREN BUFFETT'S VIEW: This appears to be a wonderful business with "
                "a durable competitive moat. The quality indicators suggest it could be "
                "a candidate for our portfolio if the price is right."
            )
        elif analysis.score_percentage >= 50:
            lines.append(
                "\nWARREN BUFFETT'S VIEW: This business has some quality characteristics, "
                "but missing criteria raise questions about the durability of its moat. "
                "I'd want to understand these weaknesses better before committing capital."
            )
        else:
            lines.append(
                "\nWARREN BUFFETT'S VIEW: This doesn't meet my standards for a quality business. "
                "I look for wonderful companies with durable moats, and this one has too many "
                "red flags. I'd rather pass and wait for a better opportunity."
            )
    else:
        if analysis.score_percentage >= 70:
            lines.append(
                "\nBENJAMIN GRAHAM'S VIEW: This stock shows strong adherence to value "
                "investing principles. The fundamentals suggest a reasonable margin of safety."
            )
        elif analysis.score_percentage >= 50:
            lines.append(
                "\nBENJAMIN GRAHAM'S VIEW: This stock has mixed characteristics. While some "
                "fundamentals are sound, the failed criteria introduce risk that a "
                f"{strategy_name.lower()} should carefully consider."
            )
        else:
            lines.append(
                "\nBENJAMIN GRAHAM'S VIEW: This stock does not meet my standards for a "
                f"{strategy_name.lower()}. The multiple failed criteria suggest insufficient "
                "margin of safety. Consider looking elsewhere or waiting for better conditions."
            )
    
    return "\n".join(lines)


def generate_comparison_report(analyses: list[AnalysisResult], api_key: Optional[str] = None) -> str:
    """
    Generate a comparison report when analyzing multiple stocks.
    
    Args:
        analyses: List of AnalysisResult objects
        api_key: OpenAI API key
        
    Returns:
        A ranked comparison report
    """
    if not analyses:
        return "No analyses to compare."
    
    # Sort by score
    sorted_analyses = sorted(analyses, key=lambda x: x.score_percentage, reverse=True)
    
    lines = [
        "\n" + "="*70,
        "BENJAMIN GRAHAM STOCK COMPARISON",
        "="*70,
        f"\nRanked by adherence to Graham's {sorted_analyses[0].investor_type.value.title()} Investor criteria:\n"
    ]
    
    for i, analysis in enumerate(sorted_analyses, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        lines.append(
            f"{medal} {analysis.ticker} ({analysis.company_name}): "
            f"{analysis.score_percentage:.0f}% ({analysis.passed_count}/{analysis.total_count})"
        )
        lines.append(f"   → {analysis.overall_recommendation}")
        lines.append("")
    
    lines.append("="*70)
    
    if len(sorted_analyses) > 1:
        best = sorted_analyses[0]
        lines.append(
            f"\nTOP PICK: {best.ticker} best aligns with Graham's principles "
            f"with a {best.score_percentage:.0f}% score."
        )
    
    return "\n".join(lines)

