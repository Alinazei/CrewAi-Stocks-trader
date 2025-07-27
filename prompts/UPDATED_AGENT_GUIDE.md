# 🤖 CrewAI Trading Agents Guide - Updated System

## 📊 **AGENT SYSTEM OVERVIEW**

Our **optimized trading system** consists of **8 specialized agents**, each with clearly defined roles, tools, and responsibilities. This guide provides comprehensive information for understanding and interacting with each agent.

---

## 🎯 **CORE TRADING AGENTS**

### **📊 1. ANALYST AGENT**
**Command**: `@analyst`

#### **Role & Purpose**
- **Primary Function**: Comprehensive stock analysis and research
- **Expertise**: Technical analysis, fundamental analysis, market research
- **Decision Making**: Buy/sell recommendations based on data analysis

#### **Key Tools**
- `monitor_real_time_sentiment()` - Real-time sentiment monitoring
- `get_stock_price()` - Current stock prices and data
- `get_extended_hours_analysis()` - After-hours trading analysis
- `get_stock_news_analysis()` - News impact analysis
- `get_technical_analysis()` - Technical indicators and charts
- `get_quick_chart_signals()` - Rapid technical signals
- `analyze_sector_news()` - Sector-wide news analysis
- `get_twitter_sentiment()` - Social media sentiment
- `autonomous_stock_research()` - Deep stock research

#### **Typical Outputs**
- Detailed stock analysis reports
- Buy/sell/hold recommendations
- Technical indicator summaries
- Risk assessment for individual stocks
- Market timing recommendations

#### **Best Use Cases**
- "Analyze AAPL for potential investment"
- "What are the technical indicators showing for TSLA?"
- "Research emerging growth stocks in tech sector"

---

### **📰 2. NEWS SENTIMENT AGENT**
**Command**: `@news`

#### **Role & Purpose**
- **Primary Function**: News analysis and market sentiment tracking
- **Expertise**: Sentiment analysis, news impact assessment, social media monitoring
- **Decision Making**: Sentiment-driven trading signals and market mood analysis

#### **Key Tools**
- `get_stock_news_analysis()` - News impact analysis
- `scan_breaking_news()` - Real-time breaking news
- `analyze_sector_news()` - Sector news analysis
- `monitor_real_time_sentiment()` - Sentiment tracking
- `analyze_sentiment_impact()` - Sentiment impact on prices
- `track_sentiment_momentum()` - Sentiment trend analysis
- `generate_sentiment_alerts()` - Sentiment-based alerts
- `serper_stock_news_tool()` - Web news search
- `twitter_sentiment_analysis()` - Twitter sentiment
- `autonomous_stock_research()` - News-based research

#### **Typical Outputs**
- Sentiment scores and analysis
- News impact assessments
- Breaking news alerts
- Social media sentiment trends
- Market mood reports

#### **Best Use Cases**
- "What's the current sentiment around NVDA?"
- "Any breaking news affecting the tech sector?"
- "Track sentiment momentum for energy stocks"

---

### **⚠️ 3. RISK MANAGEMENT AGENT**
**Command**: `@risk`

#### **Role & Purpose**
- **Primary Function**: Risk assessment and portfolio protection
- **Expertise**: Portfolio risk analysis, position sizing, risk metrics
- **Decision Making**: Risk-adjusted position recommendations and portfolio protection

#### **Key Tools**
- `calculate_portfolio_risk()` - Portfolio risk metrics
- `analyze_correlation_risk()` - Asset correlation analysis
- `calculate_position_size()` - Optimal position sizing
- `assess_market_risk()` - Market-wide risk assessment
- `calculate_var_metrics()` - Value-at-Risk calculations
- `analyze_drawdown_risk()` - Drawdown analysis
- `get_risk_adjusted_returns()` - Risk-adjusted performance
- `monitor_concentration_risk()` - Portfolio concentration analysis

#### **Typical Outputs**
- Risk assessment reports
- Position size recommendations
- Portfolio risk metrics (VaR, Sharpe ratio)
- Correlation analysis
- Risk warnings and alerts

#### **Best Use Cases**
- "Assess the risk of my current portfolio"
- "What's the optimal position size for AMZN?"
- "Check correlation risk between tech stocks"

---

### **💼 4. PORTFOLIO MANAGEMENT AGENT**
**Command**: `@portfolio`

#### **Role & Purpose**
- **Primary Function**: Portfolio optimization and asset allocation
- **Expertise**: Asset allocation, portfolio rebalancing, diversification
- **Decision Making**: Portfolio structure and allocation recommendations

#### **Key Tools**
- `optimize_portfolio_allocation()` - Portfolio optimization
- `calculate_efficient_frontier()` - Efficient frontier analysis
- `rebalance_portfolio()` - Portfolio rebalancing
- `analyze_asset_allocation()` - Asset allocation analysis
- `calculate_sharpe_optimization()` - Sharpe ratio optimization
- `assess_diversification()` - Diversification analysis
- `generate_allocation_strategy()` - Allocation strategies
- `monitor_portfolio_drift()` - Portfolio drift monitoring

#### **Typical Outputs**
- Optimal asset allocation percentages
- Rebalancing recommendations
- Diversification analysis
- Portfolio optimization strategies
- Risk-return optimization results

#### **Best Use Cases**
- "Optimize my portfolio allocation"
- "How should I rebalance my portfolio?"
- "Analyze diversification of my holdings"

---

### **💰 5. TRADER AGENT**
**Command**: `@trader`

#### **Role & Purpose**
- **Primary Function**: Trading execution and market timing decisions
- **Expertise**: Order execution, market timing, trading strategies
- **Decision Making**: Specific buy/sell orders with precise execution instructions

#### **Key Tools**
- `place_market_order()` - Market order execution
- `get_real_time_quote()` - Real-time pricing
- `get_current_positions()` - Current position status
- `get_active_orders()` - Active order monitoring
- `cancel_order()` - Order cancellation
- `close_position()` - Position closing
- `modify_deal()` - Deal modification
- `get_account_information()` - Account status
- `get_technical_analysis()` - Technical timing signals
- `check_market_status()` - Market hours verification

#### **Typical Outputs**
- Specific buy/sell orders
- Order execution instructions
- Market timing recommendations
- Position management decisions
- Trading strategy implementations

#### **Best Use Cases**
- "Execute a buy order for 100 shares of MSFT"
- "What's the best timing to enter GOOGL?"
- "Close my position in META"

---

### **📈 6. PERFORMANCE TRACKING AGENT**
**Command**: `@performance`

#### **Role & Purpose**
- **Primary Function**: Performance analysis and portfolio monitoring
- **Expertise**: Returns analysis, benchmarking, performance attribution
- **Decision Making**: Performance-based optimization recommendations

#### **Key Tools**
- `analyze_portfolio_performance()` - Portfolio performance analysis
- `analyze_trade_performance()` - Individual trade analysis
- `analyze_performance_attribution()` - Performance attribution
- `calculate_risk_adjusted_metrics()` - Risk-adjusted performance
- `compare_benchmark_performance()` - Benchmark comparison
- `generate_performance_report()` - Performance reporting
- `track_drawdown_analysis()` - Drawdown tracking
- `calculate_returns_metrics()` - Return calculations

#### **Typical Outputs**
- Performance reports and metrics
- Benchmark comparisons
- Trade performance analysis
- Risk-adjusted return calculations
- Performance attribution analysis

#### **Best Use Cases**
- "Analyze my portfolio performance this quarter"
- "Compare my returns to S&P 500"
- "Show me my best and worst performing trades"

---

### **🎯 7. ORDER MANAGEMENT LEADER AGENT**
**Command**: `@order_leader`

#### **Role & Purpose**
- **Primary Function**: Overall trading coordination and profit optimization
- **Expertise**: Order management, profit optimization, position coordination
- **Decision Making**: Strategic trading decisions and profit maximization

#### **Key Tools**
- `get_account_information()` - Account management
- `get_current_positions()` - Position oversight
- `get_active_orders()` - Order management
- `close_position()` - Position closing
- `modify_deal()` - Deal adjustments
- `place_market_order()` - Order execution
- `monitor_real_time_sentiment()` - Market sentiment
- `analyze_sentiment_impact()` - Sentiment impact
- `analyze_portfolio_performance()` - Performance oversight
- `get_technical_analysis()` - Technical analysis

#### **Typical Outputs**
- Coordinated trading strategies
- Profit optimization decisions
- Position management recommendations
- Overall trading coordination
- Strategic market decisions

#### **Best Use Cases**
- "Coordinate a complex multi-stock strategy"
- "Optimize profits across my entire portfolio"
- "Manage all my current positions"

---

### **🔍 8. SCAN AGENT**
**Command**: `@scan`

#### **Role & Purpose**
- **Primary Function**: Stock discovery and opportunity identification
- **Expertise**: Stock screening, opportunity scanning, growth catalyst detection
- **Decision Making**: Investment opportunity recommendations and stock discovery

#### **Key Tools**
- `scan_undervalued_stocks()` - Undervalued stock discovery
- `scan_growth_catalysts()` - Growth opportunity detection
- `discover_stocks_from_news()` - News-based stock discovery
- `generate_team_report()` - Opportunity reporting
- `execute_buy_orders()` - Opportunity execution
- `scan_and_execute()` - Combined scan and execution
- `get_stock_news_analysis()` - News analysis for screening
- `analyze_sentiment_impact()` - Sentiment-based screening
- `autonomous_stock_research()` - Deep opportunity research

#### **Typical Outputs**
- Lists of undervalued stocks
- Growth opportunity reports
- Investment candidates with scoring
- Market scanning results
- Discovery-based recommendations

#### **Best Use Cases**
- "Find undervalued stocks with growth potential"
- "Scan for earnings catalyst opportunities"
- "Discover stocks trending in financial news"

---

## 🤝 **TEAM COLLABORATION MODE**

### **@team Command**
When you use `@team`, **ALL 8 AGENTS** collaborate on your request:

#### **Collaborative Process**
1. **📊 Analyst** - Provides detailed market analysis
2. **📰 News** - Adds sentiment and news perspective
3. **⚠️ Risk** - Assesses and quantifies risks
4. **💼 Portfolio** - Considers portfolio impact
5. **💰 Trader** - Adds execution perspective
6. **📈 Performance** - Provides performance context
7. **🎯 Order Leader** - Coordinates overall strategy
8. **🔍 Scan** - Identifies related opportunities

#### **Best Use Cases for Team Mode**
- Complex investment decisions
- Major portfolio changes
- Market crisis response
- Comprehensive stock analysis
- Strategic planning sessions

#### **Example Team Requests**
- "@team Should I invest $10,000 in TSLA right now?"
- "@team Help me restructure my portfolio for 2024"
- "@team Analyze the impact of Fed rate changes on my holdings"

---

## 🎮 **QUICK COMMAND REFERENCE**

### **Individual Agents**
```
@analyst     → Stock analysis and research
@news        → News and sentiment analysis
@risk        → Risk assessment and management
@portfolio   → Portfolio optimization
@trader      → Trading execution
@performance → Performance analysis
@order_leader → Overall coordination
@scan        → Stock discovery
```

### **System Commands**
```
@team        → ALL AGENTS COLLABORATE
!scan        → Quick market scan
!status      → System status
!clear       → Clear conversation
```

### **Trading Commands**
```
!scan-opportunities  → Find undervalued stocks
!discover-stocks     → News-based discovery
!team-report        → Generate trading report
!execute-trades     → Execute recommendations
```

---

## 💡 **BEST PRACTICES**

### **Choosing the Right Agent**
- **Single stock analysis** → `@analyst`
- **Market sentiment check** → `@news`
- **Risk assessment** → `@risk`
- **Portfolio decisions** → `@portfolio`
- **Execute trades** → `@trader`
- **Performance review** → `@performance`
- **Overall strategy** → `@order_leader`
- **Find opportunities** → `@scan`
- **Complex decisions** → `@team`

### **Effective Communication**
- Be specific about your goals
- Provide context (portfolio size, risk tolerance)
- Ask follow-up questions for clarification
- Use team mode for important decisions

**Your optimized 8-agent trading team is ready to help you make profitable, risk-managed trading decisions!** 🚀 