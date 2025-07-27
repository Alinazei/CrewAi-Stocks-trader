"""
Portfolio Management Task for CrewAI Stock Trading Agents
Handles portfolio analysis, optimization, and rebalancing
"""

from crewai import Task
from typing import Dict, Any

def portfolio_management_task(agent, context: Dict[str, Any] = None) -> Task:
    """
    Create a portfolio management task for analyzing and optimizing portfolios.
    
    Args:
        agent: The portfolio management agent
        context: Optional context for the task
        
    Returns:
        Task for portfolio management
    """
    
    description = """
    Analyze and optimize the investment portfolio using advanced portfolio management techniques.
    
    PORTFOLIO MANAGEMENT RESPONSIBILITIES:
    1. 📊 Portfolio Analysis:
       - Analyze current portfolio composition and performance
       - Calculate risk metrics (volatility, Sharpe ratio, max drawdown)
       - Assess sector and asset allocation diversification
    
    2. 🎯 Portfolio Optimization:
       - Optimize portfolio weights for maximum Sharpe ratio
       - Implement mean-reversion and momentum strategies
       - Balance risk and return based on investor profile
    
    3. ⚖️ Rebalancing Strategy:
       - Identify overweight and underweight positions
       - Recommend rebalancing actions to maintain target allocation
       - Consider transaction costs and tax implications
    
    4. 🔍 Performance Analysis:
       - Track portfolio performance vs benchmarks
       - Analyze attribution to individual holdings
       - Generate performance reports with actionable insights
    
    AVAILABLE TOOLS:
    - analyze_portfolio: Comprehensive portfolio analysis
    - optimize_portfolio: Portfolio weight optimization
    - sector_analysis: Sector allocation analysis
    - get_current_positions: Real-time position data via StocksTrader API
    - comprehensive_stock_analysis: Individual stock analysis
    
    CRITICAL REQUIREMENTS:
    - ALWAYS use DEFAULT_WATCHLIST for analysis (never hardcode other symbols)
    - Focus on the user's actual portfolio and holdings
    - Provide specific, actionable recommendations with clear reasoning
    - Consider risk tolerance and investment objectives
    - Use real-time data from StocksTrader API when available
    
    OUTPUT FORMAT:
    Provide a comprehensive portfolio management report including:
    1. Current portfolio status and composition
    2. Risk analysis and performance metrics
    3. Optimization recommendations with specific actions
    4. Rebalancing strategy with target allocations
    5. Next steps and monitoring recommendations
    
    Remember: Focus on practical portfolio management that the user can implement immediately.
    """
    
    expected_output = """
    A comprehensive portfolio management report containing:
    
    1. PORTFOLIO STATUS SUMMARY:
       - Current holdings and their weights
       - Overall portfolio value and performance
       - Risk metrics and diversification analysis
    
    2. PERFORMANCE ANALYSIS:
       - Portfolio vs benchmark performance
       - Individual position contributions
       - Risk-adjusted returns (Sharpe ratio, alpha, beta)
    
    3. OPTIMIZATION RECOMMENDATIONS:
       - Recommended portfolio weights for optimal risk/return
       - Specific buy/sell recommendations with quantities
       - Expected improvement in risk-adjusted returns
    
    4. REBALANCING STRATEGY:
       - Current vs target allocation gaps
       - Priority rebalancing actions
       - Implementation timeline and considerations
    
    5. RISK MANAGEMENT:
       - Portfolio risk assessment
       - Concentration risks and mitigation strategies
       - Stress testing results
    
    6. ACTION PLAN:
       - Immediate actions to take
       - Monitoring schedule and key metrics to track
       - Market conditions to watch for adjustment triggers
    
    All recommendations should be specific, actionable, and based on real market data.
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context
    )

def portfolio_optimization_task(agent, target_return: float = 0.15, context: Dict[str, Any] = None) -> Task:
    """
    Create a focused portfolio optimization task.
    
    Args:
        agent: The portfolio management agent
        target_return: Target annual return (default: 15%)
        context: Optional context for the task
        
    Returns:
        Task for portfolio optimization
    """
    
    description = f"""
    Optimize the portfolio allocation to achieve a target return of {target_return:.1%} while minimizing risk.
    
    OPTIMIZATION OBJECTIVES:
    - Maximize risk-adjusted returns (Sharpe ratio)
    - Achieve target return of {target_return:.1%}
    - Minimize portfolio volatility and downside risk
    - Maintain adequate diversification across sectors
    
    OPTIMIZATION PROCESS:
    1. Analyze current portfolio composition and performance
    2. Calculate expected returns and covariance matrix for holdings
    3. Run mean-variance optimization with constraints
    4. Generate optimal portfolio weights
    5. Compare optimized vs current allocation
    6. Provide implementation recommendations
    
    CONSTRAINTS:
    - Use only symbols from DEFAULT_WATCHLIST
    - Maximum 40% allocation to any single position
    - Minimum 1% allocation for included positions
    - Maintain reasonable sector diversification
    
    TOOLS TO USE:
    - optimize_portfolio: Core optimization engine
    - analyze_portfolio: Current portfolio analysis  
    - sector_analysis: Diversification assessment
    - comprehensive_stock_analysis: Individual position analysis
    
    OUTPUT: Detailed optimization report with specific allocation recommendations.
    """
    
    expected_output = f"""
    Portfolio optimization report with target return of {target_return:.1%}:
    
    1. CURRENT PORTFOLIO ANALYSIS:
       - Existing allocation weights and performance
       - Risk metrics and Sharpe ratio
       - Sector concentration analysis
    
    2. OPTIMIZATION RESULTS:
       - Optimal portfolio weights for each holding
       - Expected return and volatility of optimized portfolio
       - Improvement in Sharpe ratio vs current allocation
    
    3. IMPLEMENTATION PLAN:
       - Specific buy/sell orders to achieve optimal weights
       - Dollar amounts and share quantities for each trade
       - Expected transaction costs and market impact
    
    4. RISK ASSESSMENT:
       - Portfolio beta and correlation to market
       - Maximum drawdown expectations
       - Stress test results under various market scenarios
    
    5. MONITORING FRAMEWORK:
       - Key metrics to track portfolio performance
       - Rebalancing triggers and frequency
       - Market conditions that would warrant strategy adjustment
    
    All recommendations should be immediately actionable with specific dollar amounts and trade orders.
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context
    )

def portfolio_rebalancing_task(agent, context: Dict[str, Any] = None) -> Task:
    """
    Create a portfolio rebalancing task.
    
    Args:
        agent: The portfolio management agent
        context: Optional context for the task
        
    Returns:
        Task for portfolio rebalancing
    """
    
    description = """
    Analyze current portfolio allocation and recommend rebalancing actions to maintain optimal risk/return profile.
    
    REBALANCING ANALYSIS:
    1. 📊 Current State Assessment:
       - Get real-time position data from StocksTrader API
       - Calculate current allocation weights vs target weights
       - Identify overweight and underweight positions
    
    2. 🎯 Target Allocation Determination:
       - Use portfolio optimization to determine ideal weights
       - Consider market conditions and volatility changes
       - Account for recent performance and momentum
    
    3. ⚖️ Rebalancing Recommendations:
       - Calculate required trades to reach target allocation
       - Prioritize trades by impact and cost efficiency
       - Consider minimum trade sizes and transaction costs
    
    4. 📈 Implementation Strategy:
       - Sequence trades to minimize market impact
       - Consider timing and market liquidity
       - Plan for partial implementation if needed
    
    REBALANCING CRITERIA:
    - Positions more than 5% away from target weight
    - New market opportunities or changed fundamentals
    - Risk management requirements (stop losses, position limits)
    - Seasonal or cyclical allocation adjustments
    
    TOOLS TO USE:
    - get_current_positions: Live portfolio data
    - optimize_portfolio: Target allocation calculation
    - analyze_portfolio: Performance impact analysis
    - place_order: Execute rebalancing trades (if approved)
    
    OUTPUT: Actionable rebalancing plan with specific trade recommendations.
    """
    
    expected_output = """
    Portfolio rebalancing report and action plan:
    
    1. CURRENT vs TARGET ALLOCATION:
       - Side-by-side comparison of current and optimal weights
       - Allocation gaps requiring rebalancing
       - Total portfolio value and position sizes
    
    2. REBALANCING RECOMMENDATIONS:
       - Specific buy/sell orders with quantities and amounts
       - Priority ranking of trades by importance
       - Expected impact on portfolio risk and return
    
    3. TRADE EXECUTION PLAN:
       - Optimal sequence for executing trades
       - Market timing considerations
       - Transaction cost estimates
    
    4. RISK IMPACT ANALYSIS:
       - How rebalancing will affect portfolio volatility
       - Changes in sector exposure and diversification
       - Expected improvement in risk-adjusted returns
    
    5. IMPLEMENTATION CHECKLIST:
       - Pre-trade verification steps
       - Order types and execution parameters
       - Post-trade monitoring requirements
    
    6. FOLLOW-UP SCHEDULE:
       - Next rebalancing review date
       - Triggers for interim adjustments
       - Performance monitoring metrics
    
    Include specific dollar amounts, share quantities, and order details ready for execution.
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context
    )

def portfolio_risk_assessment_task(agent, context: Dict[str, Any] = None) -> Task:
    """
    Create a comprehensive portfolio risk assessment task.
    
    Args:
        agent: The portfolio management agent
        context: Optional context for the task
        
    Returns:
        Task for portfolio risk assessment
    """
    
    description = """
    Conduct comprehensive risk analysis of the current portfolio to identify and quantify all major risk factors.
    
    RISK ASSESSMENT SCOPE:
    1. 📊 Quantitative Risk Metrics:
       - Portfolio volatility and beta
       - Value at Risk (VaR) and Expected Shortfall
       - Maximum drawdown and recovery time
       - Sharpe ratio and risk-adjusted performance
    
    2. 🎯 Concentration Risk Analysis:
       - Single position concentration limits
       - Sector and geographic concentration
       - Correlation analysis between holdings
       - Liquidity risk assessment
    
    3. ⚠️ Market Risk Factors:
       - Interest rate sensitivity
       - Market beta and systematic risk
       - Currency exposure (if applicable)
       - Volatility regime analysis
    
    4. 🔍 Stress Testing:
       - Historical scenario analysis (2008, 2020 crashes)
       - Monte Carlo simulation of portfolio outcomes
       - Tail risk and extreme event preparation
       - Recovery scenarios and timeframes
    
    RISK MONITORING FRAMEWORK:
    - Daily risk metrics tracking
    - Alert thresholds for risk limit breaches
    - Regular stress testing schedule
    - Risk reporting and dashboard creation
    
    TOOLS TO USE:
    - analyze_portfolio: Core risk metric calculation
    - get_current_positions: Real-time position data
    - comprehensive_stock_analysis: Individual security risks
    - sector_analysis: Concentration risk assessment
    
    OUTPUT: Comprehensive risk report with mitigation recommendations.
    """
    
    expected_output = """
    Comprehensive portfolio risk assessment report:
    
    1. RISK METRICS DASHBOARD:
       - Current portfolio volatility and beta
       - Value at Risk (1-day, 1-week, 1-month)
       - Maximum drawdown over various time periods
       - Risk-adjusted return metrics (Sharpe, Sortino, Calmar)
    
    2. CONCENTRATION RISK ANALYSIS:
       - Position size limits and current concentrations
       - Sector allocation vs benchmark/optimal
       - Correlation matrix of major holdings
       - Liquidity analysis and trading volume assessment
    
    3. STRESS TEST RESULTS:
       - Portfolio performance in historical market crashes
       - Monte Carlo simulation outcomes (5th, 50th, 95th percentiles)
       - Tail risk scenarios and potential losses
       - Recovery time estimates under different scenarios
    
    4. RISK FACTOR ATTRIBUTION:
       - Systematic vs idiosyncratic risk breakdown
       - Interest rate and inflation sensitivity
       - Market sector and style factor exposures
       - Geographic and currency risk (if applicable)
    
    5. RISK MITIGATION RECOMMENDATIONS:
       - Position size adjustments to reduce concentration
       - Hedging strategies using options or ETFs
       - Diversification improvements across sectors/assets
       - Stop-loss and position management rules
    
    6. RISK MONITORING FRAMEWORK:
       - Key risk indicators to track daily/weekly
       - Alert thresholds and escalation procedures
       - Regular stress testing and review schedule
       - Risk dashboard and reporting structure
    
    Include specific risk limits, monitoring procedures, and actionable risk reduction strategies.
    """
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context
    ) 