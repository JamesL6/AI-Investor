"""
Graham & Buffett Intelligent Investor Agent - Web UI
Built with Streamlit for a clean, interactive experience.
Supports Benjamin Graham (Defensive/Enterprising) and Warren Buffett investment analysis.
"""

import streamlit as st
import concurrent.futures
from typing import Optional
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.data import get_financial_data, FinancialData, format_currency
from src.analyzer import GrahamValidator, InvestorType, AnalysisResult
from src.agent import get_llm_verdict, get_contrarian_analysis
from src.models import AVAILABLE_MODELS, get_model_choices

# Page configuration
st.set_page_config(
    page_title="Graham & Buffett Investor Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a365d;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4a5568;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .stock-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
    .pass-badge {
        background-color: #48bb78;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
    .fail-badge {
        background-color: #f56565;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
    .score-high { color: #48bb78; font-weight: bold; }
    .score-medium { color: #ecc94b; font-weight: bold; }
    .score-low { color: #f56565; font-weight: bold; }
    .stTextArea textarea {
        font-family: 'Monaco', 'Menlo', monospace;
    }
</style>
""", unsafe_allow_html=True)


def analyze_stock(ticker: str, investor_type: InvestorType, model_id: str, include_contrarian: bool = False) -> dict:
    """
    Analyze a single stock and return results.
    Designed to run in parallel.
    
    Args:
        ticker: Stock ticker symbol
        investor_type: Defensive or Enterprising
        model_id: AI model to use
        include_contrarian: Whether to generate contrarian perspectives
    """
    import time
    
    result = {
        "ticker": ticker,
        "success": False,
        "data": None,
        "analysis": None,
        "verdict": None,
        "contrarian_devil": None,
        "contrarian_skeptic": None,
        "error": None,
        "fetch_time": 0,
        "analysis_time": 0,
        "ai_time": 0
    }
    
    try:
        # Fetch financial data from Yahoo Finance
        print(f"[{ticker}] Starting analysis...")
        start_fetch = time.time()
        
        data = get_financial_data(ticker)
        result["fetch_time"] = time.time() - start_fetch
        
        if not data:
            result["error"] = f"Could not fetch financial data for {ticker}. Check ticker symbol or try again."
            print(f"[{ticker}] ERROR: {result['error']}")
            return result
        
        # Validate we got real data
        if data.total_revenue <= 0:
            result["error"] = f"Invalid data received for {ticker}: Revenue is zero or missing"
            print(f"[{ticker}] ERROR: {result['error']}")
            return result
        
        if data.current_price <= 0:
            result["error"] = f"Invalid data received for {ticker}: Price is zero or missing"
            print(f"[{ticker}] ERROR: {result['error']}")
            return result
        
        result["data"] = data
        print(f"[{ticker}] Data fetched in {result['fetch_time']:.1f}s: ${data.current_price:.2f}, Revenue: ${data.total_revenue:,.0f}")
        
        # Run Graham analysis
        start_analysis = time.time()
        validator = GrahamValidator(data)
        analysis = validator.analyze(investor_type)
        result["analysis"] = analysis
        result["analysis_time"] = time.time() - start_analysis
        print(f"[{ticker}] Analysis complete: {analysis.passed_count}/{analysis.total_count} criteria passed")
        
        # Generate AI verdict
        start_ai = time.time()
        print(f"[{ticker}] Generating AI verdict with {model_id}...")
        
        try:
            verdict = get_llm_verdict(analysis, model_id=model_id)
            result["verdict"] = verdict
            result["ai_time"] = time.time() - start_ai
            print(f"[{ticker}] AI verdict generated in {result['ai_time']:.1f}s")
        except Exception as e:
            result["verdict"] = f"AI verdict unavailable: {str(e)}"
            result["ai_time"] = time.time() - start_ai
            print(f"[{ticker}] AI Error: {str(e)}")
        
        if include_contrarian:
            print(f"[{ticker}] Generating contrarian analysis...")
            try:
                contrarian = get_contrarian_analysis(analysis, model_id=model_id)
                result["contrarian_devil"] = contrarian["devil"]
                result["contrarian_skeptic"] = contrarian["skeptic"]
                print(f"[{ticker}] Contrarian analysis complete")
            except Exception as e:
                result["contrarian_devil"] = f"Devil's Advocate unavailable: {str(e)}"
                result["contrarian_skeptic"] = f"Skeptic unavailable: {str(e)}"
                print(f"[{ticker}] Contrarian Error: {str(e)}")
        
        result["success"] = True
        total_time = result["fetch_time"] + result["analysis_time"] + result["ai_time"]
        print(f"[{ticker}] ✅ Complete in {total_time:.1f}s")
        
    except Exception as e:
        import traceback
        result["error"] = f"Error analyzing {ticker}: {str(e)}"
        print(f"[{ticker}] ❌ EXCEPTION: {str(e)}")
        traceback.print_exc()
    
    return result


def display_stock_result(result: dict, index: int):
    """Display results for a single stock."""
    ticker = result["ticker"]
    
    if not result["success"]:
        st.error(f"**{index}. {ticker}**: {result['error']}")
        return
    
    data: FinancialData = result["data"]
    analysis: AnalysisResult = result["analysis"]
    
    # Determine score color
    if analysis.score_percentage >= 70:
        score_class = "score-high"
    elif analysis.score_percentage >= 50:
        score_class = "score-medium"
    else:
        score_class = "score-low"
    
    # Stock header
    st.markdown(f"### {index}. {ticker} - {data.company_name}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price", f"${data.current_price:.2f}")
    with col2:
        st.metric("Market Cap", format_currency(data.market_cap))
    with col3:
        st.metric("P/E Ratio", f"{data.pe_ratio:.1f}" if data.pe_ratio else "N/A")
    with col4:
        score_emoji = "🟢" if analysis.score_percentage >= 70 else "🟡" if analysis.score_percentage >= 50 else "🔴"
        st.metric("Graham Score", f"{score_emoji} {analysis.passed_count}/{analysis.total_count}")
    
    # Debug: Show raw data (expandable)
    with st.expander("🔍 Data Verification (Click to verify Yahoo Finance data)", expanded=False):
        from src.debug import show_analysis_breakdown
        breakdown = show_analysis_breakdown(analysis, data)
        st.code(breakdown, language=None)
    
    # Show AI Prompt
    with st.expander("🤖 AI Prompt Debug (See exact prompt sent to Grok)", expanded=False):
        from src.debug import show_ai_prompt
        prompt_text = show_ai_prompt(analysis)
        st.code(prompt_text, language=None)
        st.caption("💡 This is the exact prompt sent to the xAI Grok API. The AI responds with a narrative explanation.")
    
    # Expandable criteria details
    with st.expander(f"📋 Detailed Criteria Analysis ({analysis.score_percentage:.0f}%)", expanded=False):
        for cr in analysis.criteria_results:
            status = "✅" if cr.passed else "❌"
            st.markdown(f"**{status} {cr.name}**")
            st.markdown(f"- Actual: `{cr.actual_value}`")
            st.markdown(f"- Required: `{cr.required_value}`")
            st.markdown(f"_{cr.explanation}_")
            st.divider()
    
    # AI Verdict - dynamic title based on investor type
    analyst_name = "Warren Buffett" if analysis.investor_type == InvestorType.BUFFETT else "Benjamin Graham"
    with st.expander(f"📜 {analyst_name}'s Verdict", expanded=True):
        st.markdown(result["verdict"])
    
    # Contrarian expanders (only shown if contrarian analysis was generated)
    if result.get("contrarian_devil"):
        with st.expander("😈 Contrarian: Devil's Advocate", expanded=False):
            st.markdown(result["contrarian_devil"])
    
    if result.get("contrarian_skeptic"):
        with st.expander("🧐 Contrarian: The Skeptic", expanded=False):
            st.markdown(result["contrarian_skeptic"])
    
    # Recommendation badge
    if analysis.score_percentage >= 70:
        st.success(f"**Recommendation:** {analysis.overall_recommendation}")
    elif analysis.score_percentage >= 50:
        st.warning(f"**Recommendation:** {analysis.overall_recommendation}")
    else:
        st.error(f"**Recommendation:** {analysis.overall_recommendation}")
    
    st.markdown("---")


def main():
    # Header
    st.markdown('<p class="main-header">📈 Graham & Buffett Intelligent Investor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Value investing analysis using the principles of Benjamin Graham and Warren Buffett</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        st.subheader("AI Model")
        model_choices = get_model_choices()
        model_options = {display: model_id for model_id, display in model_choices}
        selected_model_display = st.selectbox(
            "Choose AI Model",
            options=list(model_options.keys()),
            index=0,
            help="Select which AI model generates the analysis verdict"
        )
        selected_model = model_options[selected_model_display]
        
        # Show which API key is needed
        model_config = AVAILABLE_MODELS[selected_model]
        st.caption(f"Requires: `{model_config.api_key_env}` environment variable")
        
        # Note about Gemini 3
        if len(model_choices) == 1:
            st.info("💡 **Gemini 3** coming soon!")
        
        st.divider()
        
        # Investment strategy
        st.subheader("Investment Strategy")
        strategy = st.radio(
            "Analysis Framework",
            options=["Graham: Defensive Investor", "Graham: Enterprising Investor", "Buffett: Quality Investor"],
            index=0,
            help="""
            **Graham Defensive**: Strictest criteria for maximum safety (7 criteria).
            **Graham Enterprising**: More aggressive bargain hunting (6 criteria).
            **Buffett Quality**: Wonderful businesses at fair prices - focuses on moats, ROE, margins (10 criteria).
            """
        )
        
        if strategy == "Graham: Defensive Investor":
            investor_type = InvestorType.DEFENSIVE
        elif strategy == "Graham: Enterprising Investor":
            investor_type = InvestorType.ENTERPRISING
        else:
            investor_type = InvestorType.BUFFETT
        
        # Strategy explanation
        if investor_type == InvestorType.DEFENSIVE:
            st.info("""
            **Defensive Investor** (7 criteria):
            - Revenue > $500M
            - Current Ratio > 2.0
            - Long-term Debt < Working Capital
            - 10 years positive earnings
            - 20 years of dividends
            - 33% earnings growth (10yr)
            - P/E < 15 AND P/B < 1.5
            """)
        elif investor_type == InvestorType.ENTERPRISING:
            st.info("""
            **Enterprising Investor** (6 criteria):
            - Current Ratio > 1.5
            - Debt < 110% of Working Capital
            - 5 years no deficit
            - Currently pays dividend
            - Earnings growth (5yr)
            - Price < 120% of Net Tangible Assets
            """)
        else:  # BUFFETT
            st.info("""
            **Buffett Quality Investor** (10 criteria):
            - **Business:** Gross Margin > 40%, ROIC > 15%, Revenue CAGR > 5%
            - **Management:** ROE > 15% (not leveraged), Low SG&A
            - **Financial:** Net Margin > 20%, Positive Owner Earnings, Low Debt, Interest Coverage > 5x
            - **Valuation:** P/E < 15 OR FCF Yield > 4.5%
            """)
        
        st.divider()
        
        # Contrarian analysis option
        st.subheader("Contrarian Analysis")
        include_contrarian = st.checkbox(
            "Include Contrarian Analysis",
            value=False,
            help="Adds 😈 Devil's Advocate and 🧐 Skeptic perspectives per stock. "
                 "Generates 2 extra AI calls per stock — slower but deeper."
        )
        
        st.divider()
        
        # Parallel processing setting
        st.subheader("Performance")
        max_workers = st.slider(
            "Parallel Workers",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of stocks to analyze simultaneously"
        )
    
    # Main content area
    st.header("📝 Enter Stocks to Analyze")
    
    st.markdown("""
    Enter stock tickers below, **one per line**. Each stock will be numbered and analyzed.
    """)
    
    # Stock input
    stock_input = st.text_area(
        "Stock Tickers",
        placeholder="AAPL\nJNJ\nKO\nWMT\nBRK-B",
        height=200,
        help="Enter one ticker per line. Examples: AAPL, JNJ, MSFT, etc."
    )
    
    # Parse stocks
    if stock_input.strip():
        lines = [line.strip().upper() for line in stock_input.strip().split('\n') if line.strip()]
        stocks = list(dict.fromkeys(lines))  # Remove duplicates while preserving order
        
        # Display parsed stocks
        st.markdown("**Stocks to analyze:**")
        for i, stock in enumerate(stocks, 1):
            st.markdown(f"`{i}.` **{stock}**")
    else:
        stocks = []
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Run Analysis",
            type="primary",
            disabled=len(stocks) == 0,
            use_container_width=True
        )
    
    # Run analysis
    if analyze_button and stocks:
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Progress tracking
        progress_bar = st.progress(0, text="Starting analysis...")
        status_text = st.empty()
        
        results = []
        start_time = time.time()
        
        # Show which stocks are being analyzed
        status_text.info(f"🔄 Analyzing {len(stocks)} stock(s): {', '.join(stocks)}")
        
        # Parallel analysis
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(analyze_stock, ticker, investor_type, selected_model, include_contrarian): ticker 
                for ticker in stocks
            }
            
            # Collect results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                completed += 1
                progress = completed / len(stocks)
                progress_bar.progress(progress, text=f"Completed {ticker} ({completed}/{len(stocks)})")
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log result
                    if result["success"]:
                        total_time = result.get("fetch_time", 0) + result.get("analysis_time", 0) + result.get("ai_time", 0)
                        print(f"UI: {ticker} completed successfully in {total_time:.1f}s")
                    else:
                        print(f"UI: {ticker} failed - {result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"UI: {ticker} exception - {str(e)}")
                    results.append({
                        "ticker": ticker,
                        "success": False,
                        "error": str(e)
                    })
        
        elapsed = time.time() - start_time
        progress_bar.progress(1.0, text=f"✅ Analysis complete! ({elapsed:.1f}s)")
        
        # Show final summary
        successful = sum(1 for r in results if r["success"])
        status_text.success(f"✅ Completed: {successful}/{len(stocks)} stocks analyzed successfully in {elapsed:.1f}s")
        
        # Sort results by original order
        ticker_order = {t: i for i, t in enumerate(stocks)}
        results.sort(key=lambda r: ticker_order.get(r["ticker"], 999))
        
        # Display results
        st.markdown("---")
        
        # Summary table
        st.subheader("📈 Summary")
        summary_data = []
        for r in results:
            if r["success"]:
                analysis = r["analysis"]
                score_emoji = "🟢" if analysis.score_percentage >= 70 else "🟡" if analysis.score_percentage >= 50 else "🔴"
                summary_data.append({
                    "Ticker": r["ticker"],
                    "Company": r["data"].company_name[:30],
                    "Score": f"{score_emoji} {analysis.passed_count}/{analysis.total_count} ({analysis.score_percentage:.0f}%)",
                    "Price": f"${r['data'].current_price:.2f}",
                    "P/E": f"{r['data'].pe_ratio:.1f}" if r['data'].pe_ratio else "N/A",
                    "Recommendation": analysis.overall_recommendation.split(" - ")[0],
                    "Analysis": "👇 Scroll Down"
                })
            else:
                summary_data.append({
                    "Ticker": r["ticker"],
                    "Company": "Error",
                    "Score": "❌",
                    "Price": "-",
                    "P/E": "-",
                    "Recommendation": r.get("error", "Unknown error")[:30]
                })
        
        st.dataframe(
            summary_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Analysis": st.column_config.TextColumn("View", width="small"),
            }
        )
        
        # Detailed results
        st.markdown("---")
        st.subheader("📋 Detailed Analysis")
        
        for i, result in enumerate(results, 1):
            display_stock_result(result, i)
        
        # Ranking
        successful_results = [r for r in results if r["success"]]
        if len(successful_results) > 1:
            st.markdown("---")
            st.subheader("🏆 Graham Ranking")
            
            ranked = sorted(successful_results, key=lambda r: r["analysis"].score_percentage, reverse=True)
            
            for i, r in enumerate(ranked, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                analysis = r["analysis"]
                st.markdown(
                    f"**{medal} {r['ticker']}** ({r['data'].company_name}) - "
                    f"{analysis.score_percentage:.0f}% ({analysis.passed_count}/{analysis.total_count})"
                )


if __name__ == "__main__":
    main()

