from crewai import Task
from agents.news_sentiment_agent import create_news_sentiment_agent

news_sentiment_analysis_task = Task(
    description=(
        "Perform comprehensive news sentiment analysis for stock: {stock} and related market context. "
        "Provide detailed sentiment insights using available tools:\n"
        "1. **Individual Stock News**: Analyze news sentiment for the specific stock\n"
        "2. **Breaking News Monitoring**: Track and analyze breaking news impact\n"
        "3. **Market Sentiment**: Assess broader market sentiment trends\n"
        "4. **Sector News Analysis**: Evaluate sector-specific news and sentiment\n"
        "5. **Sentiment Trend Analysis**: Identify sentiment momentum and changes\n"
        "6. **News Impact Assessment**: Evaluate potential price impact of news\n"
        "7. **Research**: Use available research tools for additional insights\n"
        "8. **Risk Assessment**: Evaluate sentiment-based trading risks\n"
        "\n"
        "**NEWS ANALYSIS FRAMEWORK:**\n"
        "- Sentiment scoring: -1.0 (very negative) to +1.0 (very positive)\n"
        "- Impact assessment: Low, Medium, High market impact\n"
        "- Timing analysis: Immediate, Short-term, Long-term effects\n"
        "- Source credibility: Weight sources by reliability and market impact\n"
        "- Volume analysis: Consider news volume and frequency\n"
        "- Momentum tracking: Monitor sentiment momentum shifts\n"
        "- Alert system: Flag significant sentiment changes"
    ),
    expected_output=(
        "A comprehensive news sentiment analysis report including:\n"
        "**STOCK-SPECIFIC SENTIMENT ANALYSIS:**\n"
        "- Current sentiment score and trend\n"
        "- Key news headlines and their impact\n"
        "- Sentiment breakdown (positive/negative/neutral)\n"
        "- Recent sentiment changes and momentum\n"
        "- News volume and frequency analysis\n"
        "\n"
        "**MARKET CONTEXT ANALYSIS:**\n"
        "- Broader market sentiment trends\n"
        "- Sector sentiment comparison\n"
        "- Related stocks sentiment correlation\n"
        "- Market sentiment drivers\n"
        "- Sentiment divergence analysis\n"
        "\n"
        "**BREAKING NEWS IMPACT:**\n"
        "- Breaking news alerts and significance\n"
        "- Immediate market reaction assessment\n"
        "- Expected price impact magnitude\n"
        "- Trading implications and timing\n"
        "- Risk assessment from news events\n"
        "\n"
        "**SENTIMENT-BASED TRADING RECOMMENDATIONS:**\n"
        "- Optimal trading timing based on sentiment\n"
        "- Sentiment-driven entry/exit points\n"
        "- Risk management for sentiment volatility\n"
        "- Catalyst timing and preparation\n"
        "- Sentiment monitoring and alert setup"
    ),
    agent=create_news_sentiment_agent(),
    max_execution_time=180  # Reduced from 300s for faster execution
) 