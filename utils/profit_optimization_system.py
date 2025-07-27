#!/usr/bin/env python3
"""
Profit Optimization System for Daily Trading Profitability
==========================================================

This system coordinates the Order Management Leader Agent with other agents
to ensure daily profitability through intelligent profit-taking and order management.
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from crewai import Crew, Task
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfitOptimizationSystem:
    """System for coordinating profit optimization across all trading agents
    if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
    """
    
    def __init__(self):
        self.running = False
        self.optimization_thread = None
        self.check_interval = 300  # 5 minutes
        self.profit_targets = {
            'daily_target': 2.0,      # 2% daily profit target
            'position_close': 5.0,     # Close position at 5% profit
            'trailing_stop': 3.0,      # Start trailing stop at 3% profit
            'scale_out': 8.0,          # Scale out 50% at 8% profit
            'emergency_close': -2.0    # Emergency close at -2% loss
        }
        self.last_optimization = None
        self.total_daily_profit = 0.0
        
    def start_optimization_loop(self):
        """Start the continuous profit optimization loop"""
        if self.running:
            logger.warning("Optimization loop already running")
            return
        
        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop)
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
        logger.info("🚀 Profit Optimization System STARTED")
    
    def stop_optimization_loop(self):
        """Stop the profit optimization loop"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join()
        logger.info("🛑 Profit Optimization System STOPPED")
    
    def _optimization_loop(self):
        """Main optimization loop - runs every 5 minutes during market hours"""
        while self.running:
            try:
                if self._is_market_hours():
                    logger.info("🔄 Running profit optimization cycle...")
                    self._run_optimization_cycle()
                    self.last_optimization = datetime.now()
                else:
                    logger.info("💤 Market closed - optimization paused")
                
                # Wait for next cycle
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in optimization loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def _is_market_hours(self) -> bool:
        """Check if market is currently open"""
        from utils.market_hours import is_market_open
        return is_market_open()
    
    def _run_optimization_cycle(self):
        """Run a single optimization cycle"""
        try:
            # Import here to avoid circular imports
            from agents.order_management_leader_agent import create_order_management_leader_agent
            from tasks.order_management_task import order_management_task
            
            # Create optimization crew
            optimization_crew = Crew(
                agents=[create_order_management_leader_agent()],
                tasks=[order_management_task],
                verbose=False,
                process="sequential",
                memory=False,
                max_rpm=60
            )
            
            # Execute optimization
            result = optimization_crew.kickoff()
            
            # Log results
            self._log_optimization_results(result)
            
        except Exception as e:
            logger.error(f"❌ Optimization cycle failed: {e}")
    
    def _log_optimization_results(self, result: str):
        """Log optimization results"""
        logger.info(f"✅ Optimization cycle completed")
        logger.info(f"📊 Results: {result[:200]}...")
        
        # Extract profit information if available
        if "profits secured" in result.lower():
            logger.info("💰 PROFITS SECURED this cycle!")
        
        if "positions closed" in result.lower():
            logger.info("🎯 POSITIONS CLOSED for profit optimization")
    
    def get_daily_performance(self) -> Dict[str, Any]:
        """Get daily performance metrics"""
        return {
            'total_daily_profit': self.total_daily_profit,
            'daily_target': self.profit_targets['daily_target'],
            'target_achieved': self.total_daily_profit >= self.profit_targets['daily_target'],
            'last_optimization': self.last_optimization,
            'optimization_running': self.running,
            'profit_targets': self.profit_targets
        }
    
    def update_profit_targets(self, new_targets: Dict[str, float]):
        """Update profit targets"""
        self.profit_targets.update(new_targets)
        logger.info(f"📈 Profit targets updated: {new_targets}")
    
    def manual_optimization(self) -> str:
        """Run manual optimization cycle"""
        logger.info("🔧 Manual optimization triggered")
        try:
            self._run_optimization_cycle()
            return "✅ Manual optimization completed successfully"
        except Exception as e:
            error_msg = f"❌ Manual optimization failed: {e}"
            logger.error(error_msg)
            return error_msg

# Global optimization system instance
profit_optimizer = ProfitOptimizationSystem()

def initialize_profit_optimization():
    """Initialize the profit optimization system"""
    profit_optimizer.start_optimization_loop()
    return "🚀 Profit Optimization System initialized and running"

def stop_profit_optimization():
    """Stop the profit optimization system"""
    profit_optimizer.stop_optimization_loop()
    return "🛑 Profit Optimization System stopped"

def get_optimization_status() -> Dict[str, Any]:
    """Get current optimization status"""
    return profit_optimizer.get_daily_performance()

def run_manual_optimization() -> str:
    """Run manual optimization cycle"""
    return profit_optimizer.manual_optimization()

# Enhanced Team Collaboration with Profit Optimization
def create_profit_optimized_team_collaboration(user_input: str) -> str:
    """Create team collaboration with integrated profit optimization"""
    from crewai import Crew, Task
    from agents.analyst_agent import create_analyst_agent
    from agents.news_sentiment_agent import create_news_sentiment_agent
    from agents.risk_management_agent import create_risk_management_agent
    from agents.portfolio_management_agent import create_portfolio_management_agent
    from agents.trader_agent import create_trader_agent
    from agents.performance_tracking_agent import create_performance_tracking_agent
    from agents.order_management_leader_agent import create_order_management_leader_agent
    
    # Create enhanced tasks with profit optimization focus
    tasks = []
    
    # Task 1: Market Analysis with Profit Opportunities
    market_analysis_task = Task(
        description=f"""
        Analyze market conditions for profit opportunities: {user_input}
        
        Focus on:
        - Current market trends and momentum
        - Stocks showing strong profit potential
        - Technical levels for entry and exit
        - Risk factors that could impact profitability
        """,
        expected_output="Market analysis with profit-focused recommendations",
        agent=create_analyst_agent()
    )
    tasks.append(market_analysis_task)
    
    # Task 2: News Impact on Profitability
    news_task = Task(
        description="""
        Analyze news impact on current and potential positions for profit optimization:
        - Breaking news affecting open positions
        - Upcoming events that could impact profitability
        - Sentiment shifts that create profit opportunities
        """,
        expected_output="News analysis with profit impact assessment",
        agent=create_news_sentiment_agent()
    )
    tasks.append(news_task)
    
    # Task 3: Risk Management for Profit Protection
    risk_task = Task(
        description="""
        Assess risks to current profitable positions and portfolio:
        - Position sizing for optimal profit potential
        - Risk factors that could reduce profitability
        - Portfolio protection strategies
        """,
        expected_output="Risk assessment with profit protection recommendations",
        agent=create_risk_management_agent()
    )
    tasks.append(risk_task)
    
    # Task 4: Portfolio Optimization for Daily Profits
    portfolio_task = Task(
        description="""
        Optimize portfolio for daily profitability:
        - Rebalancing for profit maximization
        - Sector allocation for best profit potential
        - Diversification while maintaining profit focus
        """,
        expected_output="Portfolio optimization for daily profits",
        agent=create_portfolio_management_agent()
    )
    tasks.append(portfolio_task)
    
    # Task 5: Trading Execution with Profit Focus
    trading_task = Task(
        description="""
        Execute trades with profit optimization in mind:
        - Entry points for maximum profit potential
        - Position sizing for optimal returns
        - Order types for profit maximization
        """,
        expected_output="Trading execution plan with profit optimization",
        agent=create_trader_agent()
    )
    tasks.append(trading_task)
    
    # Task 6: Performance Tracking
    performance_task = Task(
        description="""
        Track performance with focus on daily profitability:
        - Current profit/loss status
        - Progress toward daily profit targets
        - Performance metrics and optimization opportunities
        """,
        expected_output="Performance analysis with daily profit tracking",
        agent=create_performance_tracking_agent()
    )
    tasks.append(performance_task)
    
    # Task 7: ORDER MANAGEMENT LEADER (Final Decision Maker)
    order_management_task = Task(
        description="""
        As the ORDER MANAGEMENT LEADER, make final decisions on profit optimization:
        
        Based on ALL previous agent analysis:
        - CLOSE profitable positions at optimal levels
        - ADJUST stop losses to protect profits
        - SCALE OUT of large winning positions
        - COORDINATE all profit-taking decisions
        
        Focus on DAILY PROFITABILITY - make decisions that secure profits TODAY.
        """,
        expected_output="Order management decisions with executed profit optimization actions",
        agent=create_order_management_leader_agent()
    )
    tasks.append(order_management_task)
    
    # Create profit-optimized team crew
    profit_crew = Crew(
        agents=[
            create_analyst_agent(),
            create_news_sentiment_agent(),
            create_risk_management_agent(),
            create_portfolio_management_agent(),
            create_trader_agent(),
            create_performance_tracking_agent(),
            create_order_management_leader_agent()  # Leader makes final decisions
        ],
        tasks=tasks,
        verbose=True,
        process="sequential",  # Sequential so leader gets all info
        memory=False,
        max_rpm=30,
        share_crew=True
    )
    
    # Execute profit-optimized collaboration
    result = profit_crew.kickoff()
    
    return str(result)

if __name__ == "__main__":
    # Test the profit optimization system
    print("🚀 Testing Profit Optimization System...")
    
    # Initialize system
    status = initialize_profit_optimization()
    print(status)
    
    # Wait a bit
    time.sleep(2)
    
    # Check status
    performance = get_optimization_status()
    print(f"📊 Performance: {performance}")
    
    # Stop system
    stop_status = stop_profit_optimization()
    print(stop_status) 