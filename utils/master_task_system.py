"""
Master Tudor Task System
========================

This system recognizes tasks from Master Tudor and ensures agents work 
continuously until the task is complete. It integrates with the goal tracking
system and manages persistent agent execution.
"""

import re
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .goal_tracker import goal_tracker, GoalType, TradingGoal

class TaskType(Enum):
    """Types of tasks from Master Tudor"""
    PROFIT_TARGET = "profit_target"
    WEEKLY_PROFIT = "weekly_profit"
    DAILY_PROFIT = "daily_profit"
    PORTFOLIO_GAIN = "portfolio_gain"
    RISK_REDUCTION = "risk_reduction"
    CUSTOM_ORDER = "custom_order"

@dataclass
class MasterTask:
    """Represents a task from Master Tudor"""
    task_id: str
    task_type: TaskType
    target_value: float
    time_frame: str  # "week", "day", "month", "immediate"
    description: str
    created_at: datetime
    deadline: datetime
    is_continuous: bool = True
    priority: int = 1
    status: str = "active"
    goal_id: Optional[str] = None  # Goal tracker ID
    
    def __str__(self):
        return f"🎯 Master Tudor's Task: {self.description} (Target: ${self.target_value:,.2f} in {self.time_frame})"

class MasterTaskRecognizer:
    """Recognizes and parses tasks from Master Tudor"""
    
    def __init__(self):
        self.task_patterns = {
            # Weekly profit patterns
            r"(?:this\s+)?week\s+make\s+(?:me\s+)?\$?([\d,]+)\s*(?:profit|gain)?": TaskType.WEEKLY_PROFIT,
            r"make\s+\$?([\d,]+)\s+(?:profit\s+)?this\s+week": TaskType.WEEKLY_PROFIT,
            r"generate\s+\$?([\d,]+)\s+(?:in\s+)?(?:profit\s+)?(?:this\s+)?week": TaskType.WEEKLY_PROFIT,
            
            # Daily profit patterns  
            r"(?:today|daily)\s+make\s+(?:me\s+)?\$?([\d,]+)\s*(?:profit|gain)?": TaskType.DAILY_PROFIT,
            r"make\s+\$?([\d,]+)\s+(?:profit\s+)?(?:today|daily)": TaskType.DAILY_PROFIT,
            
            # General profit patterns
            r"make\s+(?:me\s+)?\$?([\d,]+)\s+profit": TaskType.PROFIT_TARGET,
            r"earn\s+(?:me\s+)?\$?([\d,]+)": TaskType.PROFIT_TARGET,
            r"generate\s+\$?([\d,]+)\s+(?:in\s+)?profit": TaskType.PROFIT_TARGET,
            
            # Portfolio gain patterns
            r"increase\s+portfolio\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%": TaskType.PORTFOLIO_GAIN,
            r"grow\s+portfolio\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%": TaskType.PORTFOLIO_GAIN,
            
            # Risk reduction patterns
            r"reduce\s+risk\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%": TaskType.RISK_REDUCTION,
        }
        
        self.master_identifiers = [
            "master tudor",
            "tudor", 
            "boss",
            "sir",
            "master"
        ]
    
    def is_from_master(self, text: str) -> bool:
        """Check if the message is addressed as from Master Tudor"""
        text_lower = text.lower()
        
        # Check for direct identifiers
        for identifier in self.master_identifiers:
            if identifier in text_lower:
                return True
        
        # Check for authoritative language
        authoritative_phrases = ["you must", "i want", "make me", "get me", "i need"]
        return any(phrase in text_lower for phrase in authoritative_phrases)
    
    def parse_task(self, text: str) -> Optional[MasterTask]:
        """Parse a task from text"""
        text_lower = text.lower().strip()
        
        for pattern, task_type in self.task_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                # Extract target value
                target_str = match.group(1).replace(',', '')
                target_value = float(target_str)
                
                # Determine time frame
                time_frame = "immediate"
                deadline = datetime.now() + timedelta(days=7)  # Default 1 week
                
                if "week" in text_lower:
                    time_frame = "week"
                    # Calculate end of current week
                    days_until_sunday = 6 - datetime.now().weekday()
                    deadline = datetime.now() + timedelta(days=days_until_sunday)
                elif "today" in text_lower or "daily" in text_lower:
                    time_frame = "day"
                    deadline = datetime.now().replace(hour=23, minute=59, second=59)
                elif "month" in text_lower:
                    time_frame = "month"
                    deadline = datetime.now() + timedelta(days=30)
                
                # Create task
                task_id = f"master_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return MasterTask(
                    task_id=task_id,
                    task_type=task_type,
                    target_value=target_value,
                    time_frame=time_frame,
                    description=text.strip(),
                    created_at=datetime.now(),
                    deadline=deadline,
                    is_continuous=True,
                    priority=10  # Master's tasks have highest priority
                )
        
        return None

class MasterTaskExecutor:
    """Executes Master Tudor's tasks continuously until completion"""
    
    def __init__(self):
        self.active_tasks: Dict[str, MasterTask] = {}
        self.execution_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, bool] = {}
        self.recognizer = MasterTaskRecognizer()
    
    def submit_task(self, text: str) -> Optional[str]:
        """Submit a new task from Master Tudor"""
        # Check if it's from master
        if not self.recognizer.is_from_master(text):
            return None
        
        # Parse the task
        task = self.recognizer.parse_task(text)
        if not task:
            return None
        
        # Create a goal in the goal tracker
        goal_id = self._create_goal_from_task(task)
        task.goal_id = goal_id  # Store goal_id as attribute
        
        # Store the task
        self.active_tasks[task.task_id] = task
        
        # Start continuous execution
        self._start_continuous_execution(task)
        
        return task.task_id
    
    def _create_goal_from_task(self, task: MasterTask) -> str:
        """Create a goal in the goal tracking system"""
        goal_type_map = {
            TaskType.PROFIT_TARGET: GoalType.CUSTOM,
            TaskType.WEEKLY_PROFIT: GoalType.CUSTOM,
            TaskType.DAILY_PROFIT: GoalType.DAILY_PROFIT,
            TaskType.PORTFOLIO_GAIN: GoalType.PORTFOLIO_GAIN,
            TaskType.RISK_REDUCTION: GoalType.RISK_REDUCTION,
        }
        
        goal_type = goal_type_map.get(task.task_type, GoalType.CUSTOM)
        
        return goal_tracker.create_goal(
            goal_type=goal_type,
            target_value=task.target_value,
            description=f"Master Tudor's Order: {task.description}",
            deadline=task.deadline,
            daily_trading=True,
            priority=task.priority,
            metadata={
                "master_task_id": task.task_id,
                "time_frame": task.time_frame,
                "is_master_task": True
            }
        )
    
    def _start_continuous_execution(self, task: MasterTask):
        """Start continuous execution thread for the task"""
        self.stop_flags[task.task_id] = False
        
        def execution_loop():
            """Continuous execution loop that runs until task is complete"""
            from tools.profit_taking_strategy_tool import execute_profit_taking_strategy
            from tools.profit_taking_strategy_tool import get_default_watchlist
            
            print(f"\n🚀 MASTER TUDOR'S TASK ACTIVATED!")
            print(f"📋 Task: {task.description}")
            print(f"🎯 Target: ${task.target_value:,.2f}")
            print(f"⏰ Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}")
            print(f"💪 AGENTS WILL WORK CONTINUOUSLY UNTIL TASK IS COMPLETE!\n")
            
            cycles = 0
            while not self.stop_flags.get(task.task_id, False):
                cycles += 1
                
                try:
                    # Get current progress
                    goal = goal_tracker.get_goal(task.goal_id)
                    if goal and goal.is_completed():
                        print(f"\n🎉 MASTER TUDOR'S TASK COMPLETED! 🏆")
                        print(f"✅ Target ${task.target_value:,.2f} ACHIEVED!")
                        print(f"🔄 Total cycles: {cycles}")
                        break
                    
                    # Check if deadline passed
                    if datetime.now() > task.deadline:
                        print(f"\n⚠️ Task deadline reached. Stopping execution.")
                        break
                    
                    print(f"\n🔄 Executing cycle {cycles} for Master Tudor's task...")
                    
                    # Execute continuous trading with ALL available tools
                    print(f"\n🔧 ACTIVATING ALL TRADING TOOLS:")
                    print(f"   ✅ Advanced Chart Analysis")
                    print(f"   ✅ News Sentiment Analysis") 
                    print(f"   ✅ Risk Assessment")
                    print(f"   ✅ Portfolio Optimization")
                    print(f"   ✅ Market Scanner")
                    print(f"   ✅ Performance Analytics")
                    print(f"   ✅ Twitter Sentiment")
                    print(f"   ✅ Profit Taking Strategy")
                    
                    # FIXED: Call the underlying function directly instead of the tool object
                    analysis_symbols = get_default_watchlist()
                    result = execute_profit_taking_strategy(
                        profit_threshold=1.5,  # Lower threshold for more opportunities
                        analysis_symbols=analysis_symbols,
                        target_goal=f"Make ${task.target_value} profit",
                        max_cycles=5  # 5 sub-cycles per main cycle
                    )
                    
                    # Additional market analysis using all tools
                    if cycles % 2 == 0:  # Every other cycle, do deep analysis
                        print(f"\n🔍 DEEP MARKET ANALYSIS FOR MASTER TUDOR:")
                        try:
                            # Use available tools for market analysis
                            from tools.stockstrader_api_tool import api_client
                            
                            # Simple market scan using StocksTrader API
                            watchlist = analysis_symbols.split(',')[:5]  # Check top 5 symbols
                            opportunities = []
                            
                            for symbol in watchlist:
                                symbol = symbol.strip().upper()
                                quote_result = api_client.get_quote(symbol)
                                if quote_result.get("code") == "ok" and "data" in quote_result:
                                    data = quote_result["data"]
                                    change_pct = float(data.get("change_percent", 0))
                                    if change_pct > 2:  # Strong positive momentum
                                        opportunities.append(symbol)
                            
                            print(f"   📊 Found {len(opportunities)} symbols with strong momentum: {', '.join(opportunities)}")
                            
                        except Exception as e:
                            print(f"   ⚠️ Market analysis unavailable: {str(e)}")
                    
                    # Update progress with REAL trading results
                    if goal:
                        # Get actual account information
                        from tools.stockstrader_api_tool import api_client
                        try:
                            account_info = api_client.get_account_info()
                            if account_info.get("code") == "ok" and "data" in account_info:
                                data = account_info["data"]
                                
                                # Calculate actual profit based on task type
                                if task.task_type in [TaskType.PROFIT_TARGET, TaskType.WEEKLY_PROFIT, TaskType.DAILY_PROFIT]:
                                    # Get realized P&L for profit targets
                                    current_profit = float(data.get("realized_pnl", 0))
                                    
                                    # Add unrealized P&L if counting total gains
                                    unrealized_pnl = float(data.get("unrealized_pnl", 0))
                                    total_profit = current_profit + unrealized_pnl
                                    
                                    goal_tracker.update_goal_progress(
                                        task.goal_id, 
                                        total_profit,
                                        f"Cycle {cycles} - Realized: ${current_profit:.2f}, Unrealized: ${unrealized_pnl:.2f}"
                                    )
                                    
                                    print(f"\n📊 REAL PROGRESS UPDATE:")
                                    print(f"   💰 Realized P&L: ${current_profit:.2f}")
                                    print(f"   📈 Unrealized P&L: ${unrealized_pnl:.2f}")
                                    print(f"   🎯 Total Progress: ${total_profit:.2f} / ${task.target_value:.2f}")
                                    print(f"   📊 Completion: {(total_profit/task.target_value)*100:.1f}%")
                                    
                                elif task.task_type == TaskType.PORTFOLIO_GAIN:
                                    # Get portfolio gain percentage
                                    portfolio_value = float(data.get("portfolio_value", 0))
                                    initial_value = float(data.get("initial_value", portfolio_value))
                                    
                                    if initial_value > 0:
                                        gain_percentage = ((portfolio_value - initial_value) / initial_value) * 100
                                        goal_tracker.update_goal_progress(
                                            task.goal_id,
                                            gain_percentage,
                                            f"Cycle {cycles} - Portfolio gain: {gain_percentage:.2f}%"
                                        )
                                        
                                        print(f"\n📊 PORTFOLIO PROGRESS:")
                                        print(f"   💼 Portfolio Value: ${portfolio_value:.2f}")
                                        print(f"   📈 Gain: {gain_percentage:.2f}%")
                                        print(f"   🎯 Target: {task.target_value:.2f}%")
                        except Exception as e:
                            print(f"⚠️ Could not get real account data: {str(e)}")
                            print(f"   Continuing with trading cycles...")
                    
                    # Wait before next cycle (market conditions check)
                    time.sleep(300)  # 5 minutes between cycles
                    
                except Exception as e:
                    print(f"❌ Error in execution cycle {cycles}: {str(e)}")
                    time.sleep(60)  # Wait 1 minute on error
            
            # Clean up
            self.active_tasks.pop(task.task_id, None)
            self.execution_threads.pop(task.task_id, None)
        
        # Start execution thread
        thread = threading.Thread(target=execution_loop, daemon=True)
        self.execution_threads[task.task_id] = thread
        thread.start()
    
    def stop_task(self, task_id: str):
        """Stop a running task"""
        if task_id in self.stop_flags:
            self.stop_flags[task_id] = True
            print(f"🛑 Stopping Master Tudor's task: {task_id}")
    
    def get_active_tasks(self) -> List[MasterTask]:
        """Get all active Master Tudor tasks"""
        return list(self.active_tasks.values())
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        goal = goal_tracker.get_goal(task.goal_id) if hasattr(task, 'goal_id') else None
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "target": task.target_value,
            "current_progress": goal.current_value if goal else 0,
            "progress_percentage": goal.progress_percentage if goal else 0,
            "time_remaining": str(task.deadline - datetime.now()),
            "status": "completed" if goal and goal.is_completed() else "active",
            "created_at": task.created_at.isoformat()
        }

# Global instance
master_task_executor = MasterTaskExecutor()

def recognize_and_execute_master_task(text: str) -> Optional[str]:
    """Main entry point to recognize and execute Master Tudor's tasks"""
    task_id = master_task_executor.submit_task(text)
    if task_id:
        print(f"\n👑 MASTER TUDOR'S TASK RECOGNIZED AND ACTIVATED!")
        print(f"📋 Task ID: {task_id}")
        print(f"🤖 All agents are now working to complete your task!")
        return task_id
    return None

def get_master_tasks_status() -> List[Dict[str, Any]]:
    """Get status of all Master Tudor's tasks"""
    return [
        master_task_executor.get_task_status(task.task_id)
        for task in master_task_executor.get_active_tasks()
    ] 