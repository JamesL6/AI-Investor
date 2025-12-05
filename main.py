#!/usr/bin/env python3
"""
Benjamin Graham Intelligent Investor Agent
==========================================

Analyze stocks using Benjamin Graham's classic value investing criteria
from 'The Intelligent Investor'.

Usage:
    python main.py                      # Interactive mode
    python main.py --ticker AAPL        # Analyze single stock
    python main.py --tickers AAPL,JNJ   # Compare multiple stocks
"""

import argparse
import sys
import os
from dotenv import load_dotenv

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from src.data import get_financial_data, format_currency, FinancialData
from src.analyzer import GrahamValidator, InvestorType, AnalysisResult
from src.agent import get_llm_verdict, generate_comparison_report

# Load environment variables
load_dotenv()

console = Console()


def display_welcome():
    """Display welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     BENJAMIN GRAHAM INTELLIGENT INVESTOR AGENT                   ║
║     ─────────────────────────────────────────                    ║
║                                                                  ║
║     "The intelligent investor is a realist who sells to          ║
║      optimists and buys from pessimists."                        ║
║                                                                  ║
║     Analyze stocks using Graham's time-tested value criteria     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def get_investor_type_choice() -> InvestorType:
    """Prompt user to choose investor type."""
    console.print("\n[bold]Choose your investor strategy:[/bold]\n")
    console.print("  [cyan][1][/cyan] Defensive Investor")
    console.print("      • Stricter criteria for maximum safety")
    console.print("      • Requires 10+ years of earnings history")
    console.print("      • 20 years of dividend payments")
    console.print("      • Current ratio > 2.0")
    console.print()
    console.print("  [cyan][2][/cyan] Enterprising Investor")
    console.print("      • More aggressive, seeks bargains")
    console.print("      • 5 years of positive earnings")
    console.print("      • Current dividend payment")
    console.print("      • Price < 120% of net tangible assets")
    console.print()
    
    while True:
        choice = console.input("[bold]Enter choice (1 or 2): [/bold]").strip()
        if choice == "1":
            return InvestorType.DEFENSIVE
        elif choice == "2":
            return InvestorType.ENTERPRISING
        else:
            console.print("[red]Invalid choice. Please enter 1 or 2.[/red]")


def display_financial_summary(data: FinancialData):
    """Display a summary table of key financial data."""
    table = Table(title=f"📊 Financial Summary: {data.ticker}", show_header=True, header_style="bold cyan")
    
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")
    
    table.add_row("Company", data.company_name)
    table.add_row("Current Price", f"${data.current_price:.2f}")
    table.add_row("Market Cap", format_currency(data.market_cap))
    table.add_row("Revenue (TTM)", format_currency(data.total_revenue))
    table.add_row("Net Income (TTM)", format_currency(data.net_income))
    table.add_row("", "")
    table.add_row("Current Ratio", f"{data.current_ratio:.2f}")
    table.add_row("P/E Ratio", f"{data.pe_ratio:.2f}" if data.pe_ratio else "N/A")
    table.add_row("P/B Ratio", f"{data.pb_ratio:.2f}" if data.pb_ratio else "N/A")
    # yfinance returns dividend yield as decimal (e.g., 0.0257 for 2.57%)
    # Cap at 20% as sanity check - higher values are likely data errors
    div_yield_pct = data.dividend_yield * 100 if data.dividend_yield < 1 else data.dividend_yield
    if div_yield_pct > 20:
        table.add_row("Dividend Yield", f"{div_yield_pct:.2f}% [dim](verify)[/dim]")
    else:
        table.add_row("Dividend Yield", f"{div_yield_pct:.2f}%")
    table.add_row("", "")
    table.add_row("Years of Earnings Data", str(data.years_of_earnings_data))
    table.add_row("Years of Dividend Data", str(data.years_of_dividend_data))
    
    console.print()
    console.print(table)


def display_criteria_results(analysis: AnalysisResult):
    """Display detailed criteria results in a formatted table."""
    strategy = "Defensive" if analysis.investor_type == InvestorType.DEFENSIVE else "Enterprising"
    
    console.print(f"\n[bold magenta]📋 {strategy} Investor Criteria Results[/bold magenta]\n")
    
    for result in analysis.criteria_results:
        status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
        console.print(f"  {status}  [bold]{result.name}[/bold]")
        console.print(f"        Actual: [cyan]{result.actual_value}[/cyan]")
        console.print(f"        Required: [dim]{result.required_value}[/dim]")
        console.print()
    
    # Score summary
    score_color = "green" if analysis.score_percentage >= 70 else "yellow" if analysis.score_percentage >= 50 else "red"
    console.print(
        Panel(
            f"[bold]Score: {analysis.passed_count}/{analysis.total_count} "
            f"([{score_color}]{analysis.score_percentage:.0f}%[/{score_color}])[/bold]\n\n"
            f"[italic]{analysis.overall_recommendation}[/italic]",
            title="📈 Analysis Summary",
            border_style=score_color
        )
    )


def analyze_single_stock(ticker: str, investor_type: InvestorType, show_llm: bool = True) -> AnalysisResult | None:
    """Analyze a single stock and display results."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Fetch data
        task = progress.add_task(f"Fetching financial data for {ticker}...", total=None)
        data = get_financial_data(ticker)
        progress.remove_task(task)
    
    if not data:
        console.print(f"[red]Error: Could not fetch data for {ticker}[/red]")
        return None
    
    # Display financial summary
    display_financial_summary(data)
    
    # Run analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running Graham analysis...", total=None)
        validator = GrahamValidator(data)
        analysis = validator.analyze(investor_type)
        progress.remove_task(task)
    
    # Display criteria results
    display_criteria_results(analysis)
    
    # Generate LLM verdict
    if show_llm:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating Benjamin Graham's verdict...", total=None)
            verdict = get_llm_verdict(analysis)
            progress.remove_task(task)
        
        console.print()
        console.print(Panel(verdict, title="📜 Benjamin Graham's Verdict", border_style="blue"))
    
    return analysis


def analyze_multiple_stocks(tickers: list[str], investor_type: InvestorType):
    """Analyze and compare multiple stocks."""
    analyses = []
    
    for ticker in tickers:
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold]Analyzing: {ticker}[/bold]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]")
        
        analysis = analyze_single_stock(ticker, investor_type, show_llm=False)
        if analysis:
            analyses.append(analysis)
    
    # Generate comparison report
    if len(analyses) > 1:
        comparison = generate_comparison_report(analyses)
        console.print()
        console.print(Panel(comparison, title="🏆 Stock Comparison", border_style="gold1"))


def interactive_mode():
    """Run in interactive mode with prompts."""
    display_welcome()
    
    # Get ticker(s)
    console.print("\n[bold]Enter stock ticker(s) to analyze:[/bold]")
    console.print("[dim]For multiple stocks, separate with commas (e.g., AAPL,JNJ,KO)[/dim]")
    
    ticker_input = console.input("\n[bold]Ticker(s): [/bold]").strip().upper()
    
    if not ticker_input:
        console.print("[red]No ticker provided. Exiting.[/red]")
        return
    
    tickers = [t.strip() for t in ticker_input.split(",")]
    
    # Get investor type
    investor_type = get_investor_type_choice()
    
    console.print(f"\n[bold green]Starting analysis with {investor_type.value.title()} Investor criteria...[/bold green]")
    
    if len(tickers) == 1:
        analyze_single_stock(tickers[0], investor_type)
    else:
        analyze_multiple_stocks(tickers, investor_type)
    
    console.print("\n[dim]Analysis complete. Remember: Past performance does not guarantee future results.[/dim]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze stocks using Benjamin Graham's value investing criteria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Interactive mode
  python main.py --ticker AAPL            # Analyze Apple
  python main.py --tickers AAPL,JNJ,KO    # Compare multiple stocks
  python main.py --ticker AAPL --strategy defensive
  python main.py --ticker AAPL --strategy enterprising
        """
    )
    
    parser.add_argument(
        "--ticker", "-t",
        type=str,
        help="Single stock ticker to analyze"
    )
    
    parser.add_argument(
        "--tickers", "-T",
        type=str,
        help="Comma-separated list of tickers to compare"
    )
    
    parser.add_argument(
        "--strategy", "-s",
        type=str,
        choices=["defensive", "enterprising"],
        default="defensive",
        help="Investment strategy to use (default: defensive)"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM-generated verdict"
    )
    
    args = parser.parse_args()
    
    # Determine investor type
    investor_type = (
        InvestorType.ENTERPRISING 
        if args.strategy == "enterprising" 
        else InvestorType.DEFENSIVE
    )
    
    # Run appropriate mode
    if args.ticker:
        display_welcome()
        analyze_single_stock(args.ticker.upper(), investor_type, show_llm=not args.no_llm)
    elif args.tickers:
        display_welcome()
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
        analyze_multiple_stocks(tickers, investor_type)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

