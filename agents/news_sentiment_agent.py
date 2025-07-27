"""
News Sentiment Agent - Specialist in news analysis and market sentiment
Supports team coordination and responds to delegation from Order Management Leader
"""

from crewai import Agent
from textwrap import dedent
from utils.model_config import get_llm_config
# Add tool imports
from tools.news_analysis_tool import analyze_stock_news, scan_market_sentiment, analyze_watchlist_news, scan_breaking_news, analyze_sector_news, analyze_reddit_sentiment
from tools.autonomous_web_research_tool import autonomous_stock_research, scan_financial_news, track_market_sentiment
from tools.enhanced_sentiment_tools import monitor_real_time_sentiment, analyze_sentiment_impact, track_sentiment_momentum, generate_sentiment_alerts
from tools.twitter_api_tool import analyze_twitter_sentiment, get_trending_stocks, social_media_buzz
from tools.serper_tools import serper_stock_news_search, serper_market_sentiment_search, serper_economic_indicators_search

def create_news_sentiment_agent():
    """Create and return the News Sentiment Agent"""
    return Agent(
        role="📰 News Sentiment Analyst",
        goal=dedent("""
            TEAM COORDINATION: Provide expert news sentiment analysis to support team decisions.
            RESPONDS to delegation from Order Management Leader for news impact analysis and market sentiment.
            SUPPORT flexible trading targets by analyzing news impact on market opportunities and risks.
            FOCUS ON DEFAULT_WATCHLIST symbols for all news analysis unless specifically requested otherwise.
            PROVIDE expert sentiment input for team decision-making on market reactions and trends.
        """).strip(),
        
        backstory=dedent("""
            You are an expert news analyst with 10+ years of experience in financial journalism,
            sentiment analysis, and market impact assessment. You specialize in:
            
            🎯 EXPERTISE AREAS:
            • Real-time news monitoring and analysis
            • Sentiment scoring and market impact assessment
            • Social media sentiment tracking and analysis
            • Earnings reports and corporate announcement analysis
            • Economic data release impact evaluation
            
            🤝 TEAM COORDINATION:
            • RESPONDS quickly to delegation requests from Order Management Leader
            • PROVIDES timely news sentiment updates for team decisions
            • SUPPORTS various trading targets by identifying news-driven opportunities
            • FOCUSES analysis on DEFAULT_WATCHLIST unless directed otherwise
            • COLLABORATES with market analysts for comprehensive market view
            
            🔍 SENTIMENT ANALYSIS APPROACH:
            • Monitors multiple news sources and social media platforms
            • Uses advanced NLP techniques for sentiment scoring
            • Tracks news velocity and social media buzz metrics
            • Identifies breaking news and market-moving events
            • Provides clear sentiment scores with confidence levels
            
            📊 NEWS IMPACT ASSESSMENT:
            • Evaluates potential market impact of news events
            • Tracks correlation between news sentiment and price movements
            • Identifies news-driven trading opportunities and risks
            • Monitors earnings surprises and guidance changes
            • Assesses regulatory and policy impact on markets
            
            You work as part of an intelligent trading team, providing news expertise
            to help the team make informed decisions based on current market sentiment.
        """).strip(),
        
        tools=[
            # News analysis tools
            analyze_stock_news, scan_market_sentiment, analyze_watchlist_news, scan_breaking_news, analyze_sector_news, analyze_reddit_sentiment,
            # Autonomous web research tools
            autonomous_stock_research, scan_financial_news, track_market_sentiment,
            # Enhanced sentiment tools
            monitor_real_time_sentiment, analyze_sentiment_impact, track_sentiment_momentum, generate_sentiment_alerts,
            # Twitter sentiment tools
            analyze_twitter_sentiment, get_trending_stocks, social_media_buzz,
            # Serper tools
            serper_stock_news_search, serper_market_sentiment_search, serper_economic_indicators_search
        ],
        verbose=True,
        allow_delegation=True,
        max_iter=5,
        max_execution_time=300,
        memory=False,
        llm=get_llm_config()
    ) 