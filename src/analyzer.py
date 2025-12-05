"""
Analysis Engine for Benjamin Graham Intelligent Investor Agent.
Implements Graham's specific mathematical rules as strict code checks.
"""

from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum
from src.data import FinancialData, format_currency


class InvestorType(Enum):
    DEFENSIVE = "defensive"
    ENTERPRISING = "enterprising"
    BUFFETT = "buffett"


@dataclass
class CriteriaResult:
    """Result of a single criteria check."""
    name: str
    passed: bool
    actual_value: str
    required_value: str
    explanation: str


@dataclass
class AnalysisResult:
    """Complete analysis result for a stock."""
    ticker: str
    company_name: str
    investor_type: InvestorType
    criteria_results: List[CriteriaResult]
    passed_count: int
    total_count: int
    score_percentage: float
    overall_recommendation: str


class GrahamValidator:
    """
    Validates stocks against Benjamin Graham's investment criteria.
    Supports both Defensive and Enterprising investor strategies.
    """
    
    # Configurable thresholds (can be adjusted for inflation)
    MIN_SALES_DEFENSIVE = 500_000_000  # $500M (inflation-adjusted from $100M in 1970s)
    
    def __init__(self, financial_data: FinancialData):
        self.data = financial_data
    
    def analyze(self, investor_type: InvestorType) -> AnalysisResult:
        """
        Run full analysis based on investor type.
        
        Args:
            investor_type: DEFENSIVE, ENTERPRISING, or BUFFETT
            
        Returns:
            Complete AnalysisResult with all criteria evaluations
        """
        if investor_type == InvestorType.DEFENSIVE:
            criteria_results = self._evaluate_defensive_criteria()
        elif investor_type == InvestorType.ENTERPRISING:
            criteria_results = self._evaluate_enterprising_criteria()
        else:  # BUFFETT
            criteria_results = self._evaluate_buffett_criteria()
        
        passed_count = sum(1 for c in criteria_results if c.passed)
        total_count = len(criteria_results)
        score_percentage = (passed_count / total_count * 100) if total_count > 0 else 0
        
        # Determine recommendation based on investor type
        if investor_type == InvestorType.BUFFETT:
            if score_percentage >= 80:
                recommendation = "STRONG BUY - Exceptional Buffett-style investment"
            elif score_percentage >= 65:
                recommendation = "BUY - Solid business with competitive moat"
            elif score_percentage >= 50:
                recommendation = "WATCH - Some quality characteristics, needs monitoring"
            elif score_percentage >= 35:
                recommendation = "CAUTION - Missing key Buffett criteria"
            else:
                recommendation = "PASS - Does not meet Buffett's quality standards"
        else:
            # Graham recommendations
            if score_percentage >= 85:
                recommendation = "STRONG BUY - Meets nearly all Graham criteria"
            elif score_percentage >= 70:
                recommendation = "BUY - Meets most Graham criteria with minor concerns"
            elif score_percentage >= 50:
                recommendation = "HOLD - Mixed results, requires further analysis"
            elif score_percentage >= 30:
                recommendation = "CAUTION - Fails multiple key criteria"
            else:
                recommendation = "AVOID - Does not meet Graham's safety standards"
        
        return AnalysisResult(
            ticker=self.data.ticker,
            company_name=self.data.company_name,
            investor_type=investor_type,
            criteria_results=criteria_results,
            passed_count=passed_count,
            total_count=total_count,
            score_percentage=score_percentage,
            overall_recommendation=recommendation
        )
    
    # =========================================================================
    # DEFENSIVE INVESTOR CRITERIA (7 criteria)
    # =========================================================================
    
    def _evaluate_defensive_criteria(self) -> List[CriteriaResult]:
        """Evaluate all 7 Defensive Investor criteria."""
        return [
            self._check_adequate_size(),
            self._check_strong_financials_current_ratio(),
            self._check_strong_financials_debt(),
            self._check_earnings_stability_10yr(),
            self._check_dividend_record_20yr(),
            self._check_earnings_growth_10yr(),
            self._check_moderate_pe_pb(),
        ]
    
    def _check_adequate_size(self) -> CriteriaResult:
        """
        Criterion 1: Adequate Size of Enterprise
        Sales > $500M (inflation-adjusted from Graham's original $100M)
        """
        revenue = self.data.total_revenue
        passed = revenue >= self.MIN_SALES_DEFENSIVE
        
        return CriteriaResult(
            name="Adequate Size of Enterprise",
            passed=passed,
            actual_value=format_currency(revenue),
            required_value=f"> {format_currency(self.MIN_SALES_DEFENSIVE)}",
            explanation=(
                "Graham required companies to be large and established to reduce risk. "
                "Large companies have more resources to weather economic downturns and "
                "are less likely to fail completely."
            )
        )
    
    def _check_strong_financials_current_ratio(self) -> CriteriaResult:
        """
        Criterion 2a: Strong Financial Condition - Current Ratio
        Current Ratio > 2.0 (Current Assets / Current Liabilities)
        """
        current_ratio = self.data.current_ratio
        passed = current_ratio >= 2.0
        
        return CriteriaResult(
            name="Strong Financials: Current Ratio",
            passed=passed,
            actual_value=f"{current_ratio:.2f}",
            required_value="> 2.0",
            explanation=(
                "A current ratio of 2:1 means the company has twice as many current assets "
                "as current liabilities. This provides a margin of safety against short-term "
                "financial difficulties and ensures the company can meet its obligations."
            )
        )
    
    def _check_strong_financials_debt(self) -> CriteriaResult:
        """
        Criterion 2b: Strong Financial Condition - Long-term Debt
        Long-term debt < Net Current Assets (Working Capital)
        """
        long_term_debt = self.data.total_long_term_debt
        net_current_assets = self.data.total_current_assets - self.data.total_current_liabilities
        passed = long_term_debt < net_current_assets
        
        return CriteriaResult(
            name="Strong Financials: Debt vs Working Capital",
            passed=passed,
            actual_value=f"LT Debt: {format_currency(long_term_debt)}, Working Capital: {format_currency(net_current_assets)}",
            required_value="Long-term Debt < Net Current Assets",
            explanation=(
                "Graham believed long-term debt should be less than working capital. "
                "This ensures the company could theoretically pay off all long-term debt "
                "using only its liquid assets, providing financial flexibility."
            )
        )
    
    def _check_earnings_stability_10yr(self) -> CriteriaResult:
        """
        Criterion 3: Earnings Stability
        Positive earnings for at least the last 10 years
        """
        earnings = self.data.earnings_history
        years_available = len(earnings)
        positive_years = sum(1 for e in earnings if e > 0)
        
        # Check if we have 10 years and all are positive
        passed = years_available >= 10 and all(e > 0 for e in earnings[:10])
        
        return CriteriaResult(
            name="Earnings Stability (10 Years)",
            passed=passed,
            actual_value=f"{positive_years} positive years out of {years_available} available",
            required_value="10 consecutive years of positive earnings",
            explanation=(
                "Consistent profitability over a decade demonstrates the company has a "
                "viable business model that can survive various economic conditions. "
                "Companies with erratic earnings are too unpredictable for defensive investors."
            )
        )
    
    def _check_dividend_record_20yr(self) -> CriteriaResult:
        """
        Criterion 4: Dividend Record
        Uninterrupted dividend payments for at least 20 years
        """
        dividends = self.data.dividend_history
        years_with_dividends = len([d for d in dividends if d > 0])
        years_available = len(dividends)
        
        # Need 20 years of uninterrupted dividends
        passed = years_available >= 20 and all(d > 0 for d in dividends)
        
        return CriteriaResult(
            name="Dividend Record (20 Years)",
            passed=passed,
            actual_value=f"{years_with_dividends} years of dividends (data for {years_available} years)",
            required_value="20 consecutive years of dividend payments",
            explanation=(
                "A long dividend history shows management's commitment to returning value "
                "to shareholders and indicates stable, predictable cash flows. "
                "Companies that maintain dividends through recessions demonstrate resilience."
            )
        )
    
    def _check_earnings_growth_10yr(self) -> CriteriaResult:
        """
        Criterion 5: Earnings Growth
        At least 33% increase in per-share earnings over the past 10 years
        using 3-year averages at beginning and end
        """
        earnings = self.data.earnings_history
        
        if len(earnings) < 10:
            return CriteriaResult(
                name="Earnings Growth (10-Year)",
                passed=False,
                actual_value="Insufficient data",
                required_value="> 33% growth using 3-year averages",
                explanation=(
                    "Graham required comparing the average of the first 3 years with the "
                    "average of the last 3 years to smooth out fluctuations. "
                    "A 33% increase (roughly 3% annually) shows the company is growing."
                )
            )
        
        # Calculate 3-year averages (earnings are most recent first)
        recent_avg = sum(earnings[0:3]) / 3  # Last 3 years
        old_avg = sum(earnings[-3:]) / 3     # First 3 years (oldest)
        
        if old_avg <= 0:
            growth_pct = 0
            passed = False
        else:
            growth_pct = ((recent_avg - old_avg) / abs(old_avg)) * 100
            passed = growth_pct >= 33
        
        return CriteriaResult(
            name="Earnings Growth (10-Year)",
            passed=passed,
            actual_value=f"{growth_pct:.1f}% growth",
            required_value="> 33% growth using 3-year averages",
            explanation=(
                "Graham required comparing the average of the first 3 years with the "
                "average of the last 3 years to smooth out fluctuations. "
                "A 33% increase (roughly 3% annually) shows the company is growing, "
                "not just maintaining, its earning power."
            )
        )
    
    def _check_moderate_pe_pb(self) -> CriteriaResult:
        """
        Criterion 6 & 7: Moderate P/E and P/B Ratios
        - P/E < 15 (based on 3-year average earnings)
        - P/B < 1.5
        - OR: P/E × P/B < 22.5
        """
        pe = self.data.pe_ratio
        pb = self.data.pb_ratio
        
        # Check the combined rule (P/E × P/B < 22.5) which is more flexible
        pe_pb_product = pe * pb if pe > 0 and pb > 0 else float('inf')
        
        # Pass if: (P/E < 15 AND P/B < 1.5) OR (P/E × P/B < 22.5)
        traditional_pass = pe < 15 and pb < 1.5
        combined_pass = pe_pb_product < 22.5
        passed = traditional_pass or combined_pass
        
        return CriteriaResult(
            name="Moderate Valuation (P/E & P/B)",
            passed=passed,
            actual_value=f"P/E: {pe:.1f}, P/B: {pb:.2f}, Product: {pe_pb_product:.1f}",
            required_value="P/E < 15 AND P/B < 1.5, OR P/E × P/B < 22.5",
            explanation=(
                "Graham believed in paying a reasonable price. A P/E under 15 means you're "
                "paying less than 15 years of earnings. A P/B under 1.5 means you're paying "
                "less than 1.5x the company's net asset value. The combined rule (22.5) "
                "allows flexibility: a company with P/E of 9 could have P/B up to 2.5."
            )
        )
    
    # =========================================================================
    # ENTERPRISING INVESTOR CRITERIA (6 criteria)
    # =========================================================================
    
    def _evaluate_enterprising_criteria(self) -> List[CriteriaResult]:
        """Evaluate all 6 Enterprising Investor criteria."""
        return [
            self._check_financial_condition_enterprising(),
            self._check_debt_enterprising(),
            self._check_earnings_stability_5yr(),
            self._check_current_dividend(),
            self._check_earnings_growth_5yr(),
            self._check_price_to_net_tangible_assets(),
        ]
    
    def _check_financial_condition_enterprising(self) -> CriteriaResult:
        """
        Criterion 1 (Enterprising): Financial Condition
        Current Ratio > 1.5 (less strict than defensive)
        """
        current_ratio = self.data.current_ratio
        passed = current_ratio >= 1.5
        
        return CriteriaResult(
            name="Financial Condition: Current Ratio",
            passed=passed,
            actual_value=f"{current_ratio:.2f}",
            required_value="> 1.5",
            explanation=(
                "For enterprising investors, Graham relaxed the current ratio requirement "
                "to 1.5:1. This still provides safety but allows for more aggressive "
                "opportunities in companies that may be in turnaround situations."
            )
        )
    
    def _check_debt_enterprising(self) -> CriteriaResult:
        """
        Criterion 2 (Enterprising): Debt Level
        Total Debt < 110% of Net Current Assets (Working Capital)
        """
        total_debt = self.data.total_debt
        net_current_assets = self.data.total_current_assets - self.data.total_current_liabilities
        
        if net_current_assets <= 0:
            passed = False
            ratio = float('inf')
        else:
            ratio = (total_debt / net_current_assets) * 100
            passed = ratio < 110
        
        return CriteriaResult(
            name="Debt Level vs Working Capital",
            passed=passed,
            actual_value=f"Debt is {ratio:.0f}% of Working Capital" if ratio != float('inf') else "Negative Working Capital",
            required_value="Total Debt < 110% of Net Current Assets",
            explanation=(
                "Graham allowed enterprising investors to accept higher debt levels "
                "(up to 110% of working capital vs. 100% for defensive). This opens up "
                "opportunities in leveraged companies that may offer bargain prices."
            )
        )
    
    def _check_earnings_stability_5yr(self) -> CriteriaResult:
        """
        Criterion 3 (Enterprising): Earnings Stability
        No earnings deficit in the last 5 years
        """
        earnings = self.data.earnings_history
        
        if len(earnings) < 5:
            # Use whatever data we have
            years_checked = len(earnings)
            deficit_free = all(e >= 0 for e in earnings)
        else:
            years_checked = 5
            deficit_free = all(e >= 0 for e in earnings[:5])
        
        passed = years_checked >= 5 and deficit_free
        
        return CriteriaResult(
            name="Earnings Stability (5 Years)",
            passed=passed,
            actual_value=f"No deficit in {years_checked} years checked" if deficit_free else f"Deficit found in last {years_checked} years",
            required_value="No earnings deficit in last 5 years",
            explanation=(
                "Unlike the defensive requirement of 10 years, enterprising investors "
                "only need to verify 5 years without losses. This allows investment in "
                "younger or recovering companies while still avoiding chronic money-losers."
            )
        )
    
    def _check_current_dividend(self) -> CriteriaResult:
        """
        Criterion 4 (Enterprising): Dividend Record
        Currently pays some dividend (any amount)
        """
        dividends = self.data.dividend_history
        current_dividend = dividends[0] if dividends else 0
        dividend_yield = self.data.dividend_yield
        
        passed = current_dividend > 0 or dividend_yield > 0
        
        # yfinance returns dividend yield as decimal (e.g., 0.0257 for 2.57%)
        div_yield_pct = dividend_yield * 100 if dividend_yield < 1 else dividend_yield
        
        return CriteriaResult(
            name="Current Dividend Payment",
            passed=passed,
            actual_value=f"Yield: {div_yield_pct:.2f}%" if dividend_yield > 0 else "No dividend",
            required_value="Currently pays any dividend",
            explanation=(
                "Graham required at least some dividend as proof the company generates "
                "real cash and is shareholder-friendly. Unlike the defensive 20-year "
                "requirement, any current dividend satisfies this criterion."
            )
        )
    
    def _check_earnings_growth_5yr(self) -> CriteriaResult:
        """
        Criterion 5 (Enterprising): Earnings Growth
        Current earnings greater than earnings 5 years ago
        """
        earnings = self.data.earnings_history
        
        if len(earnings) < 5:
            return CriteriaResult(
                name="Earnings Growth (5-Year)",
                passed=False,
                actual_value="Insufficient data",
                required_value="Current earnings > earnings 5 years ago",
                explanation=(
                    "Graham wanted evidence of growth over a meaningful period. "
                    "Comparing current earnings to 5 years ago shows the business "
                    "is moving in the right direction."
                )
            )
        
        current_earnings = earnings[0]
        old_earnings = earnings[4]  # 5 years ago
        
        passed = current_earnings > old_earnings and old_earnings > 0
        
        if old_earnings <= 0:
            growth_desc = "N/A (base year had no positive earnings)"
        else:
            growth_pct = ((current_earnings - old_earnings) / old_earnings) * 100
            growth_desc = f"{growth_pct:.1f}% growth"
        
        return CriteriaResult(
            name="Earnings Growth (5-Year)",
            passed=passed,
            actual_value=f"Current: {format_currency(current_earnings)}, 5yr ago: {format_currency(old_earnings)} ({growth_desc})",
            required_value="Current earnings > earnings 5 years ago",
            explanation=(
                "Unlike the defensive 33% threshold, enterprising investors simply need "
                "to see positive momentum. Any growth over 5 years is acceptable, "
                "allowing investment in companies at earlier stages of recovery."
            )
        )
    
    def _check_price_to_net_tangible_assets(self) -> CriteriaResult:
        """
        Criterion 6 (Enterprising): Price Relative to Assets
        Price < 120% of Net Tangible Assets per share
        """
        price = self.data.current_price
        nta = self.data.net_tangible_assets
        shares = self.data.market_cap / price if price > 0 else 1
        
        nta_per_share = nta / shares if shares > 0 else 0
        
        if nta_per_share <= 0:
            passed = False
            ratio_pct = float('inf')
        else:
            ratio_pct = (price / nta_per_share) * 100
            passed = ratio_pct < 120
        
        return CriteriaResult(
            name="Price vs Net Tangible Assets",
            passed=passed,
            actual_value=f"Price is {ratio_pct:.0f}% of NTA/share" if ratio_pct != float('inf') else "Negative NTA",
            required_value="Price < 120% of Net Tangible Assets per share",
            explanation=(
                "Graham's 'net-net' concept: buying at or below tangible asset value "
                "provides a margin of safety. Even at 120% of NTA, you're paying only "
                "a modest premium for tangible assets you could theoretically liquidate."
            )
        )
    
    # =========================================================================
    # WARREN BUFFETT CRITERIA (10 criteria organized into 4 tenets)
    # Based on his letters to shareholders and "The Intelligent Investor" philosophy
    # =========================================================================
    
    def _evaluate_buffett_criteria(self) -> List[CriteriaResult]:
        """Evaluate all 10 Warren Buffett investment criteria."""
        return [
            # Business Tenets (3)
            self._check_buffett_economic_moat(),
            self._check_buffett_consistent_earnings(),
            self._check_buffett_revenue_growth(),
            
            # Management Tenets (2)
            self._check_buffett_roe_consistency(),
            self._check_buffett_efficient_management(),
            
            # Financial Tenets (4)
            self._check_buffett_high_margins(),
            self._check_buffett_owner_earnings(),
            self._check_buffett_low_debt(),
            self._check_buffett_interest_coverage(),
            
            # Value Tenets (1)
            self._check_buffett_reasonable_valuation(),
        ]
    
    # --- Business Tenets ---
    
    def _check_buffett_economic_moat(self) -> CriteriaResult:
        """
        Business Tenet 1: Economic Moat (Durable Competitive Advantage)
        Gross Margin > 40% indicates pricing power and moat
        ROIC > 15% indicates efficient use of capital
        """
        gross_margin = self.data.gross_margin
        roic = self.data.roic
        
        # Pass if gross margin > 40% AND ROIC > 15%
        passed = gross_margin >= 40 and roic >= 15
        
        return CriteriaResult(
            name="Economic Moat (Gross Margin & ROIC)",
            passed=passed,
            actual_value=f"Gross Margin: {gross_margin:.1f}%, ROIC: {roic:.1f}%",
            required_value="Gross Margin > 40% AND ROIC > 15%",
            explanation=(
                "Buffett seeks businesses with durable competitive advantages. High gross margins "
                "(>40%) indicate pricing power from brand, patents, or network effects. "
                "ROIC >15% shows the company earns well above its cost of capital, "
                "suggesting a sustainable moat that competitors can't easily breach."
            )
        )
    
    def _check_buffett_consistent_earnings(self) -> CriteriaResult:
        """
        Business Tenet 2: Consistent Operating History
        No more than 2 negative earnings years in available history
        """
        earnings = self.data.earnings_history
        years_available = len(earnings)
        negative_years = sum(1 for e in earnings if e <= 0)
        
        # Allow max 2 negative years
        passed = years_available >= 4 and negative_years <= 2
        
        return CriteriaResult(
            name="Consistent Earnings History",
            passed=passed,
            actual_value=f"{negative_years} negative years out of {years_available} available",
            required_value="No more than 2 negative earnings years",
            explanation=(
                "Buffett looks for businesses with consistent, predictable earnings. "
                "Companies with erratic or frequently negative earnings are too unpredictable "
                "to value with confidence. Consistency allows for reliable DCF projections "
                "and indicates a stable, proven business model."
            )
        )
    
    def _check_buffett_revenue_growth(self) -> CriteriaResult:
        """
        Business Tenet 3: Favorable Long-Term Prospects
        Revenue CAGR > 5% over available history
        """
        revenue = self.data.revenue_history
        
        if len(revenue) < 3:
            return CriteriaResult(
                name="Revenue Growth (CAGR)",
                passed=False,
                actual_value="Insufficient data",
                required_value="Revenue CAGR > 5%",
                explanation=(
                    "Buffett seeks businesses with favorable long-term prospects. "
                    "Consistent revenue growth indicates expanding markets or market share gains."
                )
            )
        
        # Calculate CAGR: (Ending/Beginning)^(1/years) - 1
        starting = revenue[-1]  # Oldest
        ending = revenue[0]     # Most recent
        years = len(revenue) - 1
        
        if starting <= 0:
            cagr = 0
            passed = False
        else:
            cagr = ((ending / starting) ** (1 / years) - 1) * 100
            passed = cagr >= 5
        
        return CriteriaResult(
            name="Revenue Growth (CAGR)",
            passed=passed,
            actual_value=f"{cagr:.1f}% CAGR over {years} years",
            required_value="Revenue CAGR > 5%",
            explanation=(
                "Buffett prefers businesses with favorable long-term prospects. "
                "A 5%+ revenue CAGR suggests the company operates in a growing market "
                "or is gaining share. Stagnant or declining revenue signals potential problems."
            )
        )
    
    # --- Management Tenets ---
    
    def _check_buffett_roe_consistency(self) -> CriteriaResult:
        """
        Management Tenet 1: Rational Capital Allocation / High ROE
        Average ROE > 15% over available history (not debt-driven)
        """
        roe_history = self.data.roe_history
        current_roe = self.data.roe
        debt_to_equity = self.data.debt_to_equity
        
        if len(roe_history) < 2:
            avg_roe = current_roe
        else:
            avg_roe = sum(roe_history) / len(roe_history)
        
        # Check if ROE is debt-driven (high D/E)
        is_leveraged = debt_to_equity > 1.0
        
        # Pass if average ROE > 15% and not excessively leveraged
        passed = avg_roe >= 15 and not is_leveraged
        
        return CriteriaResult(
            name="High ROE (Not Debt-Driven)",
            passed=passed,
            actual_value=f"Avg ROE: {avg_roe:.1f}%, D/E: {debt_to_equity:.2f}",
            required_value="ROE > 15% average, Debt/Equity < 1.0",
            explanation=(
                "Buffett values management that generates high returns on equity without "
                "excessive leverage. ROE >15% shows efficient capital deployment. "
                "If ROE is high only due to heavy debt (D/E >1), it's a red flag "
                "as returns are borrowed, not earned through operational excellence."
            )
        )
    
    def _check_buffett_efficient_management(self) -> CriteriaResult:
        """
        Management Tenet 2: Efficient Operations
        SG&A < 30% of Gross Profit indicates lean, disciplined management
        """
        sga = self.data.sga_expense
        gross_profit = self.data.gross_profit
        
        if gross_profit <= 0:
            sga_ratio = 100
            passed = False
        else:
            sga_ratio = (sga / gross_profit) * 100
            passed = sga_ratio < 30
        
        return CriteriaResult(
            name="Efficient Management (Low SG&A)",
            passed=passed,
            actual_value=f"SG&A is {sga_ratio:.1f}% of Gross Profit",
            required_value="SG&A < 30% of Gross Profit",
            explanation=(
                "Buffett admires lean, efficient management that resists empire-building. "
                "Low SG&A relative to gross profit indicates disciplined cost control "
                "and management that doesn't bloat the organization. High SG&A often "
                "signals poor capital allocation or competitive pressure."
            )
        )
    
    # --- Financial Tenets ---
    
    def _check_buffett_high_margins(self) -> CriteriaResult:
        """
        Financial Tenet 1: High Profit Margins
        Net Margin > 20% indicates strong pricing power and efficiency
        """
        net_margin = self.data.net_margin
        passed = net_margin >= 20
        
        return CriteriaResult(
            name="High Net Profit Margin",
            passed=passed,
            actual_value=f"{net_margin:.1f}%",
            required_value="Net Margin > 20%",
            explanation=(
                "Buffett looks for businesses with wide profit margins, indicating "
                "pricing power from a moat. Net margins >20% suggest the company "
                "can charge premium prices or has exceptional cost structure. "
                "Low margins indicate commodity businesses vulnerable to competition."
            )
        )
    
    def _check_buffett_owner_earnings(self) -> CriteriaResult:
        """
        Financial Tenet 2: Positive Owner Earnings
        Owner Earnings = Net Income + D&A - Maintenance CapEx
        Should be positive and yield > 10-year Treasury (~4.5%)
        """
        owner_earnings = self.data.owner_earnings
        market_cap = self.data.market_cap
        
        # Owner earnings yield
        oe_yield = (owner_earnings / market_cap * 100) if market_cap > 0 else 0
        
        # Pass if positive and yield > ~4.5% (10-year Treasury proxy)
        passed = owner_earnings > 0 and oe_yield > 4.5
        
        return CriteriaResult(
            name="Positive Owner Earnings",
            passed=passed,
            actual_value=f"Owner Earnings: {format_currency(owner_earnings)}, Yield: {oe_yield:.1f}%",
            required_value="Positive and Yield > 4.5% (Treasury rate)",
            explanation=(
                "Buffett's 'owner earnings' (from his 1986 letter) represents what an owner "
                "could extract annually without harming the business. It's superior to GAAP "
                "net income or EBITDA because it accounts for necessary reinvestment. "
                "The yield should exceed Treasury rates to justify equity risk."
            )
        )
    
    def _check_buffett_low_debt(self) -> CriteriaResult:
        """
        Financial Tenet 3: Conservative Debt Levels
        Debt/Equity < 0.5 AND Debt payoff < 4 years from earnings
        """
        debt_to_equity = self.data.debt_to_equity
        total_debt = self.data.total_debt
        net_income = self.data.net_income
        
        # Years to pay off debt
        if net_income > 0:
            payoff_years = total_debt / net_income
        else:
            payoff_years = float('inf')
        
        passed = debt_to_equity < 0.5 and payoff_years < 4
        
        return CriteriaResult(
            name="Conservative Debt Levels",
            passed=passed,
            actual_value=f"D/E: {debt_to_equity:.2f}, Payoff: {payoff_years:.1f} years",
            required_value="Debt/Equity < 0.5 AND Payoff < 4 years",
            explanation=(
                "Buffett prefers companies that can self-fund growth without heavy borrowing. "
                "A D/E <0.5 and ability to pay off debt in <4 years provides financial "
                "flexibility and safety during downturns. High debt magnifies risk "
                "and limits management's options during stress periods."
            )
        )
    
    def _check_buffett_interest_coverage(self) -> CriteriaResult:
        """
        Financial Tenet 4: Strong Interest Coverage
        EBIT / Interest Expense > 5x
        Interest should be < 15% of EBIT
        """
        interest_coverage = self.data.interest_coverage
        operating_income = self.data.operating_income
        interest_expense = self.data.interest_expense
        
        # Interest as % of EBIT
        if operating_income > 0:
            interest_pct = (interest_expense / operating_income) * 100
        else:
            interest_pct = 100
        
        # Pass if coverage > 5x OR no interest expense
        passed = interest_coverage > 5 or interest_expense <= 0
        
        actual = f"Coverage: {interest_coverage:.1f}x" if interest_coverage < float('inf') else "No debt/interest"
        
        return CriteriaResult(
            name="Strong Interest Coverage",
            passed=passed,
            actual_value=f"{actual}, Interest is {interest_pct:.1f}% of EBIT",
            required_value="Interest Coverage > 5x OR Interest < 15% of EBIT",
            explanation=(
                "Buffett requires strong interest coverage to ensure debt service doesn't "
                "threaten operations. Coverage >5x means the company earns 5 times its "
                "interest obligations, providing ample buffer. Low coverage indicates "
                "vulnerability to earnings declines or rate increases."
            )
        )
    
    # --- Value Tenets ---
    
    def _check_buffett_reasonable_valuation(self) -> CriteriaResult:
        """
        Value Tenet: Reasonable Price (Margin of Safety)
        P/E < 15 (or < historical average)
        FCF Yield > Treasury rate
        """
        pe_ratio = self.data.pe_ratio
        fcf_yield = self.data.fcf_yield
        
        # Pass if P/E < 15 OR FCF yield > 4.5%
        pe_ok = 0 < pe_ratio < 15
        fcf_ok = fcf_yield > 4.5
        passed = pe_ok or fcf_ok
        
        return CriteriaResult(
            name="Reasonable Valuation (Margin of Safety)",
            passed=passed,
            actual_value=f"P/E: {pe_ratio:.1f}, FCF Yield: {fcf_yield:.1f}%",
            required_value="P/E < 15 OR FCF Yield > 4.5%",
            explanation=(
                "Buffett buys wonderful companies at fair prices (or fair companies at "
                "wonderful prices). A P/E <15 provides margin of safety, or alternatively "
                "an FCF yield above Treasury rates justifies the equity risk. "
                "Overpaying destroys returns regardless of business quality."
            )
        )

