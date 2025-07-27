"""
Market Analyst Agent - Specialist in market data analysis and technical insights
Supports team coordination and responds to delegation from Order Management Leader
"""

from crewai import Agent
from textwrap import dedent
from utils.model_config import get_llm_config

# Import actual tool functions
from tools.stock_research_tool import get_stock_price, get_extended_hours_analysis
from tools.advanced_chart_analysis_tool import get_advanced_technical_analysis, get_tradingview_signals
from tools.news_analysis_tool import analyze_stock_news, scan_market_sentiment, analyze_watchlist_news, scan_breaking_news, analyze_sector_news
from tools.portfolio_optimization_tools import analyze_portfolio_allocation, optimize_portfolio_allocation, analyze_sector_diversification
from tools.performance_tracking_tools import calculate_performance_metrics, track_portfolio_performance
from tools.stockstrader_api_tool import get_account_information, get_current_positions, get_active_orders, get_real_time_quote

# Get LLM configuration
llm = get_llm_config()

def create_analyst_agent():
    """Create and return the Market Analyst Agent"""
    return Agent(
        role="📊 Market Data Analyst",
        goal=dedent("""
            TEAM COORDINATION: Provide expert market analysis and technical insights to support team decisions.
            RESPONDS to delegation from Order Management Leader for market data, technical analysis, and price trends.
            SUPPORT flexible trading targets by analyzing market conditions for various strategies.
            FOCUS ON DEFAULT_WATCHLIST symbols for all analysis unless specifically requested otherwise.
            PROVIDE expert input for team decision-making on market opportunities and risks.
        """).strip(),
        
        backstory=dedent("""
            You are a seasoned market analyst with 15+ years of experience in technical analysis,
            market research, and financial data interpretation. You specialize in:
            
            🎯 EXPERTISE AREAS:
            • Technical indicator analysis (RSI, MACD, Bollinger Bands, Moving Averages)
            • Chart pattern recognition and trend analysis  
            • Volume analysis and price action interpretation
            • Support/resistance level identification
            • Market sentiment and momentum analysis
            
            🤝 TEAM COORDINATION:
            • RESPONDS quickly to delegation requests from Order Management Leader
            • PROVIDES concise, actionable market insights for team decisions
            • SUPPORTS various trading targets (profit goals, risk management, rebalancing)
            • FOCUSES analysis on DEFAULT_WATCHLIST unless directed otherwise
            • COLLABORATES with other specialists for comprehensive market view
            
            🔍 ANALYSIS APPROACH:
            • Combines multiple timeframes for complete market picture
            • Uses both technical and fundamental data points
            • Provides clear buy/sell/hold recommendations with reasoning
            • Identifies optimal entry/exit points and risk levels
            • Monitors market volatility and trading volume patterns
            
            You work as part of an intelligent trading team, providing market expertise
            to help achieve the team's trading objectives efficiently and profitably.
        """).strip(),
        
        llm=get_llm_config(),
        tools=[
            # Stock data and analysis tools
            get_stock_price,
            get_extended_hours_analysis, 
            get_real_time_quote,
            get_advanced_technical_analysis,
            get_tradingview_signals,
            
            # News and sentiment tools
            analyze_stock_news,
            scan_market_sentiment,
            analyze_watchlist_news,
            scan_breaking_news,
            analyze_sector_news,
            
            # Portfolio and performance tools
            analyze_portfolio_allocation,
            optimize_portfolio_allocation,
            analyze_sector_diversification,
            calculate_performance_metrics,
            track_portfolio_performance,
            
            # Account and position tools
            get_account_information,
            get_current_positions,
            get_active_orders
        ],
        verbose=True,
        allow_delegation=True,
        max_iter=3,
        max_execution_time=300,
        memory=False
    ) 