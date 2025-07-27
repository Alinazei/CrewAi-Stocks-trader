"""
Order Management Task - Coordinates team execution for flexible trading targets
"""

from crewai import Task
from textwrap import dedent

def create_order_management_task():
    """Create and return the Order Management Task"""
    return Task(
        description=dedent("""
            🎯 TEAM COORDINATION & FLEXIBLE TARGET ACHIEVEMENT 🎯
            
            As the Order Management Leader, coordinate your specialist team to achieve the specified trading target.
            
            AGENT DELEGATION & INFORMATION GATHERING:
            • Delegate to Market Analyst for technical analysis, price trends, and market conditions
            • Delegate to News Sentiment Agent for news impact analysis and market sentiment
            • Delegate to Portfolio Manager for allocation recommendations and rebalancing strategies  
            • Delegate to Risk Manager for position sizing and risk assessment
            • Delegate to Performance Tracker for goal progress monitoring and strategy effectiveness
            • Delegate to Professional Trader for execution timing and market entry/exit points
            
            GATHER comprehensive information from your team BEFORE making trading decisions.
            
            TARGET FLEXIBILITY:
            Support various trading objectives including:
            • Profit targets: "Make $500 profit", "Achieve 15% portfolio gain"
            • Risk management: "Reduce portfolio risk by 20%", "Limit drawdown to 5%"
            • Rebalancing: "Rebalance to equal weights", "Optimize allocation"
            • Opportunity capture: "Capitalize on market volatility", "Buy the dip"
            • Time-based goals: "Day trading session", "Weekly targets"
            
            EXECUTION RULES:
            • FOCUS ON DEFAULT_WATCHLIST symbols unless specifically directed otherwise
            • CONTINUE TRADING CYCLES until the specified target is achieved
            • DELEGATE information gathering to appropriate specialists before major decisions
            • SYNTHESIZE team insights into actionable trading recommendations
            • MONITOR progress continuously and adjust strategy as needed
            • PROVIDE clear reasoning for all trading decisions
            
            CONTINUOUS EXECUTION:
            • Execute multiple trading cycles if needed to reach the target
            • Each cycle: assess current positions → gather team insights → execute trades
            • Keep trading until success criteria are met or market conditions require stopping
            • Provide progress updates throughout the process
        """).strip(),
        
        expected_output=dedent("""
            Comprehensive trading execution report including:
            
            📊 TEAM COORDINATION SUMMARY:
            • Information gathered from each specialist agent
            • How team insights influenced final decisions
            • Delegation effectiveness and response quality
            
            🎯 TARGET PROGRESS:
            • Current progress toward specified trading goal
            • Key performance metrics and milestones achieved
            • Remaining actions needed to complete target
            
            ⚡ TRADING ACTIONS EXECUTED:
            • Specific buy/sell orders placed with reasoning
            • Position sizes and execution prices
            • Risk management measures implemented
            
            📈 MARKET ANALYSIS INTEGRATION:
            • Technical analysis insights used in decisions
            • News sentiment impact on strategy
            • Risk assessment results and position sizing logic
            
            🔄 CONTINUOUS STRATEGY:
            • Assessment of whether target has been achieved
            • Next steps if additional trading cycles are needed
            • Strategy adjustments based on performance feedback
            
            💡 DECISION RATIONALE:
            • Clear explanation of why each trade was executed
            • How team coordination improved decision quality
            • Risk/reward assessment for each position
        """).strip(),
        
        max_execution_time=600  # 10 minutes for complex coordination
    )

# Create the task instance
order_management_task = create_order_management_task() 