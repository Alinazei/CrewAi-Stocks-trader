#!/usr/bin/env python3
"""
Persistent Trading Loop System
=============================

This module provides a persistent trading loop that continues trading daily
until specified goals are achieved. It manages goal-oriented trading sessions
and integrates with the goal tracking system.
"""

import asyncio
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

# Import from our systems
from utils.goal_tracker import goal_tracker, TradingGoal, GoalStatus
from utils.market_hours import is_market_open, get_market_status
from utils.trade_executor import execute_team_recommendations

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingSession:
    """Represents a single trading session"""
    session_id: str
    goal_id: str
    start_time: datetime
    end_time: Optional[datetime]
    trades_executed: int
    profit_loss: float
    progress_made: float
    status: str
    notes: str
    market_conditions: Dict[str, Any]

class PersistentTradingLoop:
    """Manages persistent trading loops for goal achievement
    if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
    """
    
    def __init__(self, team_collaboration_func: Callable[[str], str]):
        self.team_collaboration_func = team_collaboration_func
        self.active_loops: Dict[str, threading.Thread] = {}
        self.loop_status: Dict[str, str] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        self.session_history: List[TradingSession] = []
        self.daily_check_interval = 300  # Check every 5 minutes
        self.is_running = False
        
    def start_goal_oriented_trading(self, goal_id: str, user_message: str = "") -> str:
        """Start persistent trading for a specific goal"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return f"❌ Goal {goal_id} not found"
        
        if goal.status != GoalStatus.ACTIVE:
            goal_tracker.activate_goal(goal_id)
            goal = goal_tracker.get_goal(goal_id)
        
        if goal_id in self.active_loops and self.active_loops[goal_id].is_alive():
            return f"⚠️  Goal {goal_id} already has an active trading loop"
        
        # Create stop flag for this goal
        stop_flag = threading.Event()
        self.stop_flags[goal_id] = stop_flag
        
        # Start the persistent loop in a separate thread
        loop_thread = threading.Thread(
            target=self._persistent_trading_loop,
            args=(goal_id, user_message, stop_flag),
            daemon=True
        )
        
        self.active_loops[goal_id] = loop_thread
        self.loop_status[goal_id] = "starting"
        
        loop_thread.start()
        
        return f"""🎯 **PERSISTENT TRADING ACTIVATED**

**Goal**: {goal.description}
**Target**: {goal.target_value}% portfolio gain
**Current Progress**: {goal.progress_percentage:.1f}%
**Remaining**: {goal.target_value - goal.current_value:.1f}%

🔄 **Trading Loop Status**: ACTIVE
📅 **Daily Trading**: Enabled
⏰ **Next Check**: Every 5 minutes during market hours

The team will continue trading daily until this goal is achieved!
Use '!goals' to monitor progress or '!stop-goal {goal_id}' to pause."""
    
    def _persistent_trading_loop(self, goal_id: str, initial_message: str, stop_flag: threading.Event):
        """Main persistent trading loop"""
        logger.info(f"Starting persistent trading loop for goal {goal_id}")
        self.loop_status[goal_id] = "active"
        
        last_trading_day = None
        consecutive_no_trade_days = 0
        
        try:
            while not stop_flag.is_set():
                goal = goal_tracker.get_goal(goal_id)
                if not goal or goal.status != GoalStatus.ACTIVE:
                    logger.info(f"Goal {goal_id} is no longer active, stopping loop")
                    break
                
                # Check if goal is completed
                if goal.is_completed():
                    self._handle_goal_completion(goal_id)
                    break
                
                current_date = datetime.now().date()
                
                # Check if we should trade today
                if self._should_trade_today(current_date, last_trading_day):
                    market_status = get_market_status()
                    
                    if market_status.is_open or self._should_trade_extended_hours():
                        session_result = self._execute_trading_session(goal_id, initial_message)
                        
                        if session_result['success']:
                            last_trading_day = current_date
                            consecutive_no_trade_days = 0
                            
                            # Update goal progress
                            self._update_goal_progress_from_session(goal_id, session_result)
                            
                            # Check if goal completed after this session
                            updated_goal = goal_tracker.get_goal(goal_id)
                            if updated_goal and updated_goal.is_completed():
                                self._handle_goal_completion(goal_id)
                                break
                        else:
                            consecutive_no_trade_days += 1
                            
                            # If we can't trade for 5 consecutive days, pause
                            if consecutive_no_trade_days >= 5:
                                logger.warning(f"Goal {goal_id}: No trading for 5 consecutive days, pausing")
                                goal_tracker.pause_goal(goal_id)
                                break
                    else:
                        logger.info(f"Market closed, waiting for next trading session")
                
                # Wait before next check
                time.sleep(self.daily_check_interval)
                
        except Exception as e:
            logger.error(f"Error in persistent trading loop for goal {goal_id}: {e}")
            self.loop_status[goal_id] = f"error: {str(e)}"
        finally:
            self.loop_status[goal_id] = "stopped"
            if goal_id in self.active_loops:
                del self.active_loops[goal_id]
            if goal_id in self.stop_flags:
                del self.stop_flags[goal_id]
    
    def _should_trade_today(self, current_date, last_trading_day) -> bool:
        """Determine if we should trade today"""
        if last_trading_day is None:
            return True  # First day
        
        # Check if it's a new trading day
        if current_date > last_trading_day:
            # Skip weekends (market closed)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                return True
        
        return False
    
    def _should_trade_extended_hours(self) -> bool:
        """Check if we should trade during extended hours"""
        # For now, only trade during regular market hours
        # This can be enhanced based on trading strategy
        return False
    
    def _execute_trading_session(self, goal_id: str, initial_message: str) -> Dict[str, Any]:
        """Execute a single trading session"""
        session_id = f"session_{goal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Executing trading session {session_id} for goal {goal_id}")
        
        try:
            goal = goal_tracker.get_goal(goal_id)
            if not goal:
                return {'success': False, 'error': 'Goal not found'}
            
            # Create context-aware trading prompt
            trading_prompt = self._create_trading_prompt(goal, initial_message)
            
            # Execute team collaboration
            result = self.team_collaboration_func(trading_prompt)
            
            # AUTOMATICALLY EXECUTE TRADES
            logger.info(f"Executing trades for session {session_id}")
            execution_result = execute_team_recommendations(result, goal_id)
            
            # Parse results for trading metrics
            session_metrics = self._parse_session_results(goal_id, result, execution_result)
            
            # Record the session
            session = TradingSession(
                session_id=session_id,
                goal_id=goal_id,
                start_time=start_time,
                end_time=datetime.now(),
                trades_executed=session_metrics['trades_executed'],
                profit_loss=session_metrics['profit_loss'],
                progress_made=session_metrics['progress_made'],
                status='completed',
                notes=session_metrics['notes'],
                market_conditions=session_metrics['market_conditions']
            )
            
            self.session_history.append(session)
            
            # Record in goal tracker
            goal_tracker.record_daily_session(
                goal_id=goal_id,
                trades_executed=session_metrics['trades_executed'],
                profit_loss=session_metrics['profit_loss'],
                progress_made=session_metrics['progress_made'],
                notes=session_metrics['notes']
            )
            
            return {
                'success': True,
                'session': session,
                'metrics': session_metrics,
                'result': result,
                'execution_result': execution_result
            }
            
        except Exception as e:
            logger.error(f"Error executing trading session: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
    
    def _create_trading_prompt(self, goal: TradingGoal, initial_message: str) -> str:
        """Create a context-aware trading prompt"""
        progress_context = f"""
🎯 **ACTIVE TRADING GOAL**
Goal: {goal.description}
Target: {goal.target_value}%
Current Progress: {goal.current_value:.2f}% ({goal.progress_percentage:.1f}% complete)
Remaining: {goal.target_value - goal.current_value:.2f}%

"""
        
        # Get recent session history
        recent_sessions = [s for s in self.session_history if s.goal_id == goal.id][-5:]
        if recent_sessions:
            progress_context += "📈 **Recent Trading Sessions:**\n"
            for session in recent_sessions:
                progress_context += f"• {session.start_time.strftime('%Y-%m-%d')}: {session.trades_executed} trades, P&L: ${session.profit_loss:.2f}\n"
            progress_context += "\n"
        
        trading_prompt = f"""{progress_context}

**PERSISTENT TRADING MISSION**

You are in PERSISTENT TRADING MODE. Your mission is to continue making profitable trades daily until the above goal is achieved.

Original user request: "{initial_message}"

**Today's Trading Objective:**
1. Make strategic trades to move closer to the {goal.target_value}% portfolio gain target
2. Focus on profitable opportunities that align with the goal
3. Manage risk while pursuing consistent daily gains
4. Track progress and adjust strategy based on market conditions

**Key Requirements:**
- Execute actual trades (not just analysis)
- Focus on profit generation to achieve the goal
- Provide specific trade recommendations with entry/exit points
- Calculate the impact on overall portfolio gains
- Continue trading until the {goal.target_value}% target is reached

**Current Market Context:**
- Market Status: {get_market_status().status}
- Trading Focus: Goal-oriented daily profit generation
- Risk Management: Moderate risk to achieve consistent gains

Proceed with today's trading session to progress toward the goal!
"""
        
        return trading_prompt
    
    def _parse_session_results(self, goal_id: str, result: str, execution_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse trading session results to extract metrics"""
        # Extract metrics from execution result if available
        profit_loss = 0.0
        if execution_result and execution_result.get('success'):
            # Example: sum up realized P&L from all executed trades
            trades = execution_result.get('trades', [])
            for trade in trades:
                # You must ensure your trade dict has a 'realized_pnl' or similar field
                profit_loss += trade.get('realized_pnl', 0.0)
            
            # Calculate progress made based on actual profit/loss and your goal
            progress_made = 0.0
            goal = goal_tracker.get_goal(goal_id)
            if goal and goal.target_value:
                # Example: progress as a percentage of the goal
                progress_made = (profit_loss / goal.target_value) * 100
            
            execution_notes = f"Executed {len(trades)} trades, total value: ${execution_result.get('total_value_traded', 0.0):,.2f}, P&L: ${profit_loss:,.2f}"
            
        else:
            trades_executed = 0
            profit_loss = 0.0
            progress_made = 0.0
            execution_notes = "No trades executed"
        
        # Combine analysis and execution notes
        combined_notes = f"{execution_notes}. Analysis: {result[:150]}..." if len(result) > 150 else f"{execution_notes}. Analysis: {result}"
        
        metrics = {
            'trades_executed': len(trades),
            'profit_loss': profit_loss,
            'progress_made': progress_made,
            'notes': combined_notes,
            'execution_result': execution_result,
            'market_conditions': {
                'market_open': is_market_open(),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Try to extract numbers from the result
        import re
        
        # Look for trade counts
        trade_matches = re.findall(r'(\d+)\s*trades?', result.lower())
        if trade_matches:
            metrics['trades_executed'] = int(trade_matches[0])
        
        # Look for profit/loss amounts
        profit_matches = re.findall(r'\$(\d+(?:\.\d+)?)', result)
        if profit_matches:
            metrics['profit_loss'] = float(profit_matches[0])
        
        # Look for percentage gains
        percent_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', result)
        if percent_matches:
            metrics['progress_made'] = float(percent_matches[0])
        
        return metrics
    
    def _update_goal_progress_from_session(self, goal_id: str, session_result: Dict[str, Any]):
        """Update goal progress based on session results"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return
        
        # Calculate new progress value
        progress_made = session_result['metrics']['progress_made']
        if progress_made > 0:
            new_value = goal.current_value + progress_made
            goal_tracker.update_goal_progress(
                goal_id=goal_id,
                new_value=new_value,
                notes=f"Daily trading session: {session_result['metrics']['trades_executed']} trades, ${session_result['metrics']['profit_loss']:.2f} P&L"
            )
    
    def _handle_goal_completion(self, goal_id: str):
        """Handle goal completion"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return
        
        goal_tracker.complete_goal(goal_id)
        
        completion_message = f"""
🎉 **GOAL ACHIEVED!** 🎉

**Goal**: {goal.description}
**Target**: {goal.target_value}%
**Final Progress**: {goal.current_value:.2f}%
**Completion**: {goal.progress_percentage:.1f}%

✅ **Mission Accomplished!**
The persistent trading loop has successfully achieved your goal!
"""
        
        logger.info(f"Goal {goal_id} completed: {goal.description}")
        
        # Store completion message (can be retrieved later)
        self.loop_status[goal_id] = "completed"
    
    def stop_goal_trading(self, goal_id: str) -> str:
        """Stop trading for a specific goal"""
        if goal_id in self.stop_flags:
            self.stop_flags[goal_id].set()
            goal_tracker.pause_goal(goal_id)
            return f"🛑 Trading stopped for goal {goal_id}"
        else:
            return f"⚠️  No active trading loop found for goal {goal_id}"
    
    def get_active_loops(self) -> Dict[str, str]:
        """Get status of all active trading loops"""
        return self.loop_status.copy()
    
    def get_session_history(self, goal_id: str = None, days: int = 30) -> List[TradingSession]:
        """Get trading session history"""
        sessions = self.session_history
        
        if goal_id:
            sessions = [s for s in sessions if s.goal_id == goal_id]
        
        # Filter by days
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions = [s for s in sessions if s.start_time >= cutoff_date]
        
        return sessions
    
    def get_goal_progress_summary(self, goal_id: str) -> Dict[str, Any]:
        """Get a comprehensive progress summary for a goal"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return {'error': 'Goal not found'}
        
        recent_sessions = self.get_session_history(goal_id, days=7)
        
        total_trades = sum(s.trades_executed for s in recent_sessions)
        total_profit = sum(s.profit_loss for s in recent_sessions)
        
        return {
            'goal': goal.to_dict(),
            'recent_sessions': len(recent_sessions),
            'total_trades_7days': total_trades,
            'total_profit_7days': total_profit,
            'average_daily_progress': sum(s.progress_made for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0,
            'trading_status': self.loop_status.get(goal_id, 'inactive'),
            'days_to_completion': self._estimate_days_to_completion(goal_id)
        }
    
    def _estimate_days_to_completion(self, goal_id: str) -> Optional[int]:
        """Estimate days to goal completion based on recent progress"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return None
        
        recent_sessions = self.get_session_history(goal_id, days=7)
        if not recent_sessions:
            return None
        
        # Calculate average daily progress
        avg_daily_progress = sum(s.progress_made for s in recent_sessions) / len(recent_sessions)
        
        if avg_daily_progress <= 0:
            return None
        
        remaining_progress = goal.target_value - goal.current_value
        estimated_days = remaining_progress / avg_daily_progress
        
        return max(1, int(estimated_days))

# Global instance
persistent_trading_loop = None

def initialize_persistent_trading(team_collaboration_func: Callable[[str], str]):
    """Initialize the persistent trading loop system"""
    global persistent_trading_loop
    persistent_trading_loop = PersistentTradingLoop(team_collaboration_func)
    return persistent_trading_loop

def start_persistent_trading(goal_id: str, user_message: str = "") -> str:
    """Start persistent trading for a goal"""
    if persistent_trading_loop is None:
        return "❌ Persistent trading system not initialized"
    
    return persistent_trading_loop.start_goal_oriented_trading(goal_id, user_message)

def stop_goal_trading(goal_id: str) -> str:
    """Stop trading for a specific goal"""
    if persistent_trading_loop is None:
        return "❌ Persistent trading system not initialized"
    
    return persistent_trading_loop.stop_goal_trading(goal_id)

def get_trading_status() -> Dict[str, Any]:
    """Get status of all active trading loops"""
    if persistent_trading_loop is None:
        return {'error': 'Persistent trading system not initialized'}
    
    return {
        'active_loops': persistent_trading_loop.get_active_loops(),
        'goals_summary': goal_tracker.get_goal_summary()
    } 