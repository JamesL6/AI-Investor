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
from src.indices import INDEX_CONFIGS

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


def analyze_stock_no_ai(ticker: str, investor_type: InvestorType) -> dict:
    """
    Phase 1 of index mode: fetch data and score criteria only — no AI call.
    Retries up to 3 times with backoff to handle Yahoo Finance rate limiting.
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
        "ai_time": 0,
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait = attempt * 3  # 3s, 6s backoff
                print(f"[{ticker}] Retry {attempt}/{max_retries - 1} after {wait}s (rate limit)...")
                time.sleep(wait)

            start_fetch = time.time()
            data = get_financial_data(ticker)
            result["fetch_time"] = time.time() - start_fetch

            if not data or data.total_revenue <= 0 or data.current_price <= 0:
                result["error"] = f"Could not fetch valid data for {ticker}"
                continue  # retry

            result["data"] = data

            start_analysis = time.time()
            validator = GrahamValidator(data)
            analysis = validator.analyze(investor_type)
            result["analysis"] = analysis
            result["analysis_time"] = time.time() - start_analysis
            result["success"] = True

            print(f"[{ticker}] Score: {analysis.passed_count}/{analysis.total_count} ({analysis.score_percentage:.0f}%)")
            return result

        except Exception as e:
            result["error"] = f"Error analyzing {ticker}: {str(e)}"
            print(f"[{ticker}] Attempt {attempt + 1} error: {str(e)}")

    print(f"[{ticker}] Failed after {max_retries} attempts: {result['error']}")
    return result


def display_stock_result(result: dict, index: int, expand_verdict: bool = True):
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
    with st.expander(f"📜 {analyst_name}'s Verdict", expanded=expand_verdict):
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
    st.header("📝 Stock Selection")

    input_mode = st.radio(
        "Input method",
        ["✏️ Enter tickers manually", "📊 Select an index"],
        horizontal=True,
        label_visibility="collapsed"
    )

    stocks = []
    is_index_mode = False
    selected_index_name = None

    if input_mode == "✏️ Enter tickers manually":
        st.markdown("Enter stock tickers below, **one per line**.")
        stock_input = st.text_area(
            "Stock Tickers",
            placeholder="AAPL\nJNJ\nKO\nWMT\nBRK-B",
            height=200,
            help="Enter one ticker per line. Examples: AAPL, JNJ, MSFT, etc."
        )
        if stock_input.strip():
            lines = [line.strip().upper() for line in stock_input.strip().split('\n') if line.strip()]
            stocks = list(dict.fromkeys(lines))
            st.markdown("**Stocks to analyze:**")
            for i, stock in enumerate(stocks, 1):
                st.markdown(f"`{i}.` **{stock}**")

    else:  # Index mode
        is_index_mode = True
        selected_index_name = st.selectbox(
            "Choose Index",
            list(INDEX_CONFIGS.keys()),
            help="Tickers are fetched automatically from Wikipedia when you run the analysis."
        )
        config = INDEX_CONFIGS[selected_index_name]
        est_phase1 = max(1, config["est_minutes"] // 2)
        st.info(
            f"**{selected_index_name}** — {config['description']}  \n"
            f"- Phase 1 (data + scoring, ~{config['count']} stocks): ~{est_phase1} min  \n"
            f"- Phase 2 (AI verdicts for all stocks): ~{config['est_minutes']} min total  \n"
            f"Results are ranked **best → worst** by score. Contrarian analysis is disabled in index mode."
        )

    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Run Analysis",
            type="primary",
            disabled=(len(stocks) == 0 and not is_index_mode),
            use_container_width=True
        )

    # =========================================================================
    # RUN ANALYSIS
    # =========================================================================
    if analyze_button and (stocks or is_index_mode):
        st.markdown("---")
        st.header("📊 Analysis Results")
        start_time = time.time()
        results = []

        # ---- INDEX MODE: Two-phase ----
        if is_index_mode:
            # Load tickers
            with st.spinner(f"Loading {selected_index_name} tickers from Wikipedia..."):
                stocks = INDEX_CONFIGS[selected_index_name]["tickers_fn"]()

            if not stocks:
                st.error(
                    f"Failed to load {selected_index_name} tickers. "
                    "Check internet connection and try again."
                )
                st.stop()

            st.markdown(f"**{len(stocks)} tickers loaded.** Running two-phase analysis...")

            # -- Phase 1: Data fetch + criteria scoring (no AI) --
            phase1_bar = st.progress(0, text=f"Phase 1 of 2: Scoring {len(stocks)} stocks (no AI)...")
            phase1_status = st.empty()
            phase1_results = []
            phase1_start = time.time()

            # Cap Phase 1 workers at 3 — Yahoo Finance rate-limits aggressive parallel fetching
            phase1_workers = min(max_workers, 3)
            with concurrent.futures.ThreadPoolExecutor(max_workers=phase1_workers) as executor:
                futures = {
                    executor.submit(analyze_stock_no_ai, ticker, investor_type): ticker
                    for ticker in stocks
                }
                p1_done = 0
                for future in concurrent.futures.as_completed(futures):
                    ticker = futures[future]
                    p1_done += 1
                    phase1_bar.progress(
                        p1_done / len(stocks),
                        text=f"Phase 1 of 2: Scored {p1_done}/{len(stocks)} stocks..."
                    )
                    try:
                        phase1_results.append(future.result())
                    except Exception as e:
                        phase1_results.append({
                            "ticker": ticker, "success": False, "error": str(e),
                            "data": None, "analysis": None, "verdict": None,
                            "contrarian_devil": None, "contrarian_skeptic": None,
                            "fetch_time": 0, "analysis_time": 0, "ai_time": 0
                        })

            phase1_elapsed = time.time() - phase1_start
            successful_p1 = [r for r in phase1_results if r["success"]]
            failed_p1 = [r for r in phase1_results if not r["success"]]

            # Sort successful results by score descending before Phase 2
            successful_p1.sort(key=lambda r: r["analysis"].score_percentage, reverse=True)

            phase1_status.info(
                f"Phase 1 complete: {len(successful_p1)}/{len(stocks)} stocks scored "
                f"in {phase1_elapsed:.0f}s. Generating AI verdicts..."
            )

            # -- Phase 2: AI verdicts for ALL successful stocks --
            phase2_bar = st.progress(
                0, text=f"Phase 2 of 2: Generating AI verdicts for {len(successful_p1)} stocks..."
            )
            phase2_start = time.time()
            verdict_map = {}

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                verdict_futures = {
                    executor.submit(get_llm_verdict, r["analysis"], selected_model): r["ticker"]
                    for r in successful_p1
                }
                p2_done = 0
                for future in concurrent.futures.as_completed(verdict_futures):
                    ticker = verdict_futures[future]
                    p2_done += 1
                    phase2_bar.progress(
                        p2_done / len(successful_p1),
                        text=f"Phase 2 of 2: AI verdicts {p2_done}/{len(successful_p1)}..."
                    )
                    try:
                        verdict_map[ticker] = future.result()
                    except Exception as e:
                        verdict_map[ticker] = f"AI verdict unavailable: {str(e)}"

            # Merge verdicts into Phase 1 results
            for r in successful_p1:
                r["verdict"] = verdict_map.get(r["ticker"], "Verdict not generated")

            phase2_elapsed = time.time() - phase2_start
            total_elapsed = time.time() - start_time

            phase1_bar.progress(1.0, text="Phase 1 complete ✅")
            phase2_bar.progress(1.0, text=f"Phase 2 complete ✅")
            phase1_status.success(
                f"✅ {len(successful_p1)}/{len(stocks)} stocks fully analyzed in "
                f"{total_elapsed:.0f}s — ranked best → worst below."
            )

            # Combine: successful (sorted by score) + failed at the end
            results = successful_p1 + failed_p1
            is_ranked = True

        # ---- MANUAL MODE: Single-phase ----
        else:
            progress_bar = st.progress(0, text="Starting analysis...")
            status_text = st.empty()
            status_text.info(f"🔄 Analyzing {len(stocks)} stock(s): {', '.join(stocks)}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_ticker = {
                    executor.submit(analyze_stock, ticker, investor_type, selected_model, include_contrarian): ticker
                    for ticker in stocks
                }
                completed = 0
                for future in concurrent.futures.as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    completed += 1
                    progress_bar.progress(
                        completed / len(stocks),
                        text=f"Completed {ticker} ({completed}/{len(stocks)})"
                    )
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "ticker": ticker, "success": False, "error": str(e),
                            "data": None, "analysis": None, "verdict": None,
                            "contrarian_devil": None, "contrarian_skeptic": None
                        })

            elapsed = time.time() - start_time
            progress_bar.progress(1.0, text=f"✅ Analysis complete! ({elapsed:.1f}s)")
            successful = sum(1 for r in results if r["success"])
            status_text.success(
                f"✅ Completed: {successful}/{len(stocks)} stocks analyzed successfully in {elapsed:.1f}s"
            )

            # Preserve original entry order for manual mode
            ticker_order = {t: i for i, t in enumerate(stocks)}
            results.sort(key=lambda r: ticker_order.get(r["ticker"], 999))
            is_ranked = False

        # =========================================================================
        # DISPLAY RESULTS
        # =========================================================================
        st.markdown("---")

        successful_results = [r for r in results if r["success"]]
        label = (
            f"{len(successful_results)} of {len(results)} stocks analyzed — ranked best → worst"
            if is_ranked
            else f"{len(successful_results)} of {len(results)} stocks analyzed"
        )
        st.subheader(f"📈 Summary — {label}")

        # Build summary table (already in display order)
        summary_data = []
        for r in results:
            if r["success"]:
                analysis = r["analysis"]
                score_pct = analysis.score_percentage
                score_emoji = "🟢" if score_pct >= 70 else "🟡" if score_pct >= 50 else "🔴"
                summary_data.append({
                    "Rank": f"#{results.index(r) + 1}" if is_ranked else "",
                    "Ticker": r["ticker"],
                    "Company": r["data"].company_name[:30],
                    "Score": f"{score_emoji} {analysis.passed_count}/{analysis.total_count} ({score_pct:.0f}%)",
                    "Price": f"${r['data'].current_price:.2f}",
                    "P/E": f"{r['data'].pe_ratio:.1f}" if r["data"].pe_ratio else "N/A",
                    "Recommendation": analysis.overall_recommendation.split(" - ")[0],
                })
            else:
                summary_data.append({
                    "Rank": "",
                    "Ticker": r["ticker"],
                    "Company": "Error",
                    "Score": "❌",
                    "Price": "-",
                    "P/E": "-",
                    "Recommendation": (r.get("error") or "Unknown error")[:40],
                })

        col_config = {"Recommendation": st.column_config.TextColumn("Recommendation", width="medium")}
        if not is_ranked:
            col_config["Rank"] = st.column_config.TextColumn("Rank", width="small")

        st.dataframe(summary_data, use_container_width=True, hide_index=True, column_config=col_config)

        # Detailed results
        st.markdown("---")
        if is_ranked:
            st.subheader(f"📋 Detailed Analysis ({len(successful_results)} stocks, best → worst)")
            st.caption("AI verdicts are collapsed by default. Click any stock's verdict to expand.")
        else:
            st.subheader("📋 Detailed Analysis")

        for i, result in enumerate(results, 1):
            display_stock_result(result, i, expand_verdict=not is_ranked)

        # Ranking section (manual mode only — index mode is already ranked above)
        if not is_ranked and len(successful_results) > 1:
            st.markdown("---")
            st.subheader("🏆 Ranking")
            ranked = sorted(successful_results, key=lambda r: r["analysis"].score_percentage, reverse=True)
            for i, r in enumerate(ranked, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                analysis = r["analysis"]
                st.markdown(
                    f"**{medal} {r['ticker']}** ({r['data'].company_name}) — "
                    f"{analysis.score_percentage:.0f}% ({analysis.passed_count}/{analysis.total_count})"
                )


if __name__ == "__main__":
    main()

