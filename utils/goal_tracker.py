#!/usr/bin/env python3
"""
Goal Tracking System for Persistent Trading
===========================================

This module provides a comprehensive goal tracking system that stores
portfolio targets and monitors progress toward achieving them. It supports
various goal types and provides progress monitoring capabilities.
"""

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class GoalType(Enum):
    """Types of trading goals"""
    PORTFOLIO_GAIN = "portfolio_gain"
    PORTFOLIO_VALUE = "portfolio_value"
    DAILY_PROFIT = "daily_profit"
    MONTHLY_PROFIT = "monthly_profit"
    RISK_REDUCTION = "risk_reduction"
    SHARPE_RATIO = "sharpe_ratio"
    CUSTOM = "custom"

class GoalStatus(Enum):
    """Status of trading goals"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class TradingGoal:
    """Represents a trading goal with all necessary information"""
    id: str
    goal_type: GoalType
    target_value: float
    current_value: float
    description: str
    created_at: datetime
    deadline: Optional[datetime]
    status: GoalStatus
    progress_percentage: float
    daily_trading_enabled: bool
    priority: int = 1
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def update_progress(self, new_value: float):
        """Update current progress and calculate percentage"""
        self.current_value = new_value
        if self.target_value != 0:
            self.progress_percentage = (new_value / self.target_value) * 100
        else:
            self.progress_percentage = 0
    
    def is_completed(self) -> bool:
        """Check if goal is completed"""
        return self.current_value >= self.target_value
    
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until deadline"""
        if self.deadline:
            remaining = self.deadline - datetime.now()
            return max(0, remaining.days)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['goal_type'] = self.goal_type.value
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['deadline'] = self.deadline.isoformat() if self.deadline else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingGoal':
        """Create from dictionary"""
        data['goal_type'] = GoalType(data['goal_type'])
        data['status'] = GoalStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['deadline'] = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
        return cls(**data)

class GoalTracker:
    """Comprehensive goal tracking system"""
    
    def __init__(self, db_path: str = "trading_goals.db"):
        self.db_path = db_path
        self.goals: Dict[str, TradingGoal] = {}
        self.lock = threading.Lock()
        self._init_database()
        self._load_goals()
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_goals (
                    id TEXT PRIMARY KEY,
                    goal_type TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deadline TEXT,
                    status TEXT NOT NULL,
                    progress_percentage REAL NOT NULL,
                    daily_trading_enabled INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goal_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    progress_percentage REAL NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (goal_id) REFERENCES trading_goals (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_trading_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id TEXT NOT NULL,
                    session_date TEXT NOT NULL,
                    trades_executed INTEGER NOT NULL,
                    profit_loss REAL NOT NULL,
                    progress_made REAL NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (goal_id) REFERENCES trading_goals (id)
                )
            ''')
            
            conn.commit()
    
    def _load_goals(self):
        """Load goals from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM trading_goals WHERE status IN ("pending", "active", "paused")')
            
            for row in cursor.fetchall():
                goal_data = {
                    'id': row[0],
                    'goal_type': GoalType(row[1]),
                    'target_value': row[2],
                    'current_value': row[3],
                    'description': row[4],
                    'created_at': datetime.fromisoformat(row[5]),
                    'deadline': datetime.fromisoformat(row[6]) if row[6] else None,
                    'status': GoalStatus(row[7]),
                    'progress_percentage': row[8],
                    'daily_trading_enabled': bool(row[9]),
                    'priority': row[10],
                    'metadata': json.loads(row[11]) if row[11] else {}
                }
                self.goals[row[0]] = TradingGoal(**goal_data)
    
    def _save_goal(self, goal: TradingGoal):
        """Save goal to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO trading_goals 
                (id, goal_type, target_value, current_value, description, created_at, 
                 deadline, status, progress_percentage, daily_trading_enabled, priority, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                goal.id,
                goal.goal_type.value,
                goal.target_value,
                goal.current_value,
                goal.description,
                goal.created_at.isoformat(),
                goal.deadline.isoformat() if goal.deadline else None,
                goal.status.value,
                goal.progress_percentage,
                int(goal.daily_trading_enabled),
                goal.priority,
                json.dumps(goal.metadata)
            ))
            conn.commit()
    
    def create_goal(self, goal_type: GoalType, target_value: float, description: str,
                   deadline: Optional[datetime] = None, daily_trading: bool = True,
                   priority: int = 1, metadata: Dict[str, Any] = None) -> str:
        """Create a new trading goal"""
        with self.lock:
            goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            goal = TradingGoal(
                id=goal_id,
                goal_type=goal_type,
                target_value=target_value,
                current_value=0.0,
                description=description,
                created_at=datetime.now(),
                deadline=deadline,
                status=GoalStatus.PENDING,
                progress_percentage=0.0,
                daily_trading_enabled=daily_trading,
                priority=priority,
                metadata=metadata or {}
            )
            
            self.goals[goal_id] = goal
            self._save_goal(goal)
            
            return goal_id
    
    def update_goal_progress(self, goal_id: str, new_value: float, notes: str = ""):
        """Update progress for a specific goal"""
        with self.lock:
            if goal_id not in self.goals:
                raise ValueError(f"Goal {goal_id} not found")
            
            goal = self.goals[goal_id]
            old_value = goal.current_value
            goal.update_progress(new_value)
            
            # Check if goal is completed
            if goal.is_completed() and goal.status == GoalStatus.ACTIVE:
                goal.status = GoalStatus.COMPLETED
            
            # Save to database
            self._save_goal(goal)
            
            # Record progress in history
            self._record_progress(goal_id, new_value, goal.progress_percentage, notes)
            
            return goal.progress_percentage
    
    def _record_progress(self, goal_id: str, value: float, progress_percentage: float, notes: str):
        """Record progress in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goal_progress (goal_id, timestamp, value, progress_percentage, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (goal_id, datetime.now().isoformat(), value, progress_percentage, notes))
            conn.commit()
    
    def activate_goal(self, goal_id: str):
        """Activate a goal for daily trading"""
        with self.lock:
            if goal_id not in self.goals:
                raise ValueError(f"Goal {goal_id} not found")
            
            goal = self.goals[goal_id]
            goal.status = GoalStatus.ACTIVE
            self._save_goal(goal)
    
    def pause_goal(self, goal_id: str):
        """Pause a goal"""
        with self.lock:
            if goal_id not in self.goals:
                raise ValueError(f"Goal {goal_id} not found")
            
            goal = self.goals[goal_id]
            goal.status = GoalStatus.PAUSED
            self._save_goal(goal)
    
    def complete_goal(self, goal_id: str):
        """Mark a goal as completed"""
        with self.lock:
            if goal_id not in self.goals:
                raise ValueError(f"Goal {goal_id} not found")
            
            goal = self.goals[goal_id]
            goal.status = GoalStatus.COMPLETED
            self._save_goal(goal)
    
    def get_active_goals(self) -> List[TradingGoal]:
        """Get all active goals"""
        with self.lock:
            return [goal for goal in self.goals.values() if goal.status == GoalStatus.ACTIVE]
    
    def get_all_goals(self) -> List[TradingGoal]:
        """Get all goals"""
        with self.lock:
            return list(self.goals.values())
    
    def get_goal(self, goal_id: str) -> Optional[TradingGoal]:
        """Get a specific goal"""
        with self.lock:
            return self.goals.get(goal_id)
    
    def get_goals_requiring_daily_trading(self) -> List[TradingGoal]:
        """Get goals that require daily trading"""
        with self.lock:
            return [
                goal for goal in self.goals.values()
                if goal.status == GoalStatus.ACTIVE and goal.daily_trading_enabled
            ]
    
    def record_daily_session(self, goal_id: str, trades_executed: int, profit_loss: float, 
                            progress_made: float, notes: str = ""):
        """Record a daily trading session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_trading_sessions 
                (goal_id, session_date, trades_executed, profit_loss, progress_made, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                goal_id,
                datetime.now().date().isoformat(),
                trades_executed,
                profit_loss,
                progress_made,
                notes
            ))
            conn.commit()
    
    def get_progress_history(self, goal_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get progress history for a goal"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT timestamp, value, progress_percentage, notes
                FROM goal_progress
                WHERE goal_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (goal_id, since_date))
            
            return [
                {
                    'timestamp': row[0],
                    'value': row[1],
                    'progress_percentage': row[2],
                    'notes': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def get_daily_sessions(self, goal_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily trading sessions for a goal"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            since_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            cursor.execute('''
                SELECT session_date, trades_executed, profit_loss, progress_made, notes
                FROM daily_trading_sessions
                WHERE goal_id = ? AND session_date > ?
                ORDER BY session_date DESC
            ''', (goal_id, since_date))
            
            return [
                {
                    'session_date': row[0],
                    'trades_executed': row[1],
                    'profit_loss': row[2],
                    'progress_made': row[3],
                    'notes': row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def parse_goal_from_text(self, text: str) -> Optional[Tuple[GoalType, float, str, Optional[datetime]]]:
        """Parse goal from natural language text"""
        text = text.lower().strip()
        
        # Portfolio gain patterns
        if any(word in text for word in ['increase', 'gain', 'profit', 'grow']):
            if 'portfolio' in text:
                # Extract percentage
                import re
                percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
                if percentage_match:
                    target = float(percentage_match.group(1))
                    return (GoalType.PORTFOLIO_GAIN, target, 
                           f"Increase portfolio gains to {target}%", None)
        
        # Portfolio value patterns
        if any(word in text for word in ['reach', 'achieve', 'value']):
            if 'portfolio' in text:
                # Extract dollar amount
                import re
                dollar_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', text)
                if dollar_match:
                    target = float(dollar_match.group(1).replace(',', ''))
                    return (GoalType.PORTFOLIO_VALUE, target,
                           f"Reach portfolio value of ${target:,.2f}", None)
        
        # Daily profit patterns
        if 'daily' in text and any(word in text for word in ['profit', 'gain']):
            import re
            amount_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', text)
            if amount_match:
                target = float(amount_match.group(1).replace(',', ''))
                return (GoalType.DAILY_PROFIT, target,
                       f"Generate ${target:,.2f} daily profit", None)
        
        return None
    
    def get_goal_summary(self) -> Dict[str, Any]:
        """Get a summary of all goals"""
        with self.lock:
            active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
            completed_goals = [g for g in self.goals.values() if g.status == GoalStatus.COMPLETED]
            
            return {
                'total_goals': len(self.goals),
                'active_goals': len(active_goals),
                'completed_goals': len(completed_goals),
                'daily_trading_goals': len([g for g in active_goals if g.daily_trading_enabled]),
                'average_progress': sum(g.progress_percentage for g in active_goals) / len(active_goals) if active_goals else 0,
                'goals_near_completion': len([g for g in active_goals if g.progress_percentage >= 80])
            }

# Global instance
goal_tracker = GoalTracker()

def create_portfolio_gain_goal(target_percentage: float, description: str = None) -> str:
    """Helper function to create portfolio gain goal"""
    if description is None:
        description = f"Increase overall portfolio gains to {target_percentage}%"
    
    return goal_tracker.create_goal(
        goal_type=GoalType.PORTFOLIO_GAIN,
        target_value=target_percentage,
        description=description,
        daily_trading=True,
        priority=1
    )

def get_active_trading_goals() -> List[TradingGoal]:
    """Get all goals that require daily trading"""
    return goal_tracker.get_goals_requiring_daily_trading()

def update_goal_progress(goal_id: str, new_value: float, notes: str = "") -> float:
    """Update progress for a goal"""
    return goal_tracker.update_goal_progress(goal_id, new_value, notes)

def record_trading_session(goal_id: str, trades: int, profit_loss: float, progress: float, notes: str = ""):
    """Record a trading session"""
    goal_tracker.record_daily_session(goal_id, trades, profit_loss, progress, notes) 