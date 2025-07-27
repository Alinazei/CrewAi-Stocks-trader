#!/usr/bin/env python3
"""
Goal Progress Monitor
====================

This module provides comprehensive monitoring and reporting for trading goals.
It tracks progress, generates reports, and provides insights into goal achievement.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

# Import from our systems
from utils.goal_tracker import goal_tracker, TradingGoal, GoalStatus, GoalType

@dataclass
class ProgressReport:
    """Comprehensive progress report for a goal"""
    goal_id: str
    goal_description: str
    target_value: float
    current_value: float
    progress_percentage: float
    status: str
    days_active: int
    daily_average_progress: float
    estimated_completion_days: Optional[int]
    recent_sessions: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]

class GoalProgressMonitor:
    """Monitors and reports on goal progress
    if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
    """
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.progress_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.notification_callbacks: List[callable] = []
        self.check_interval = 300  # Check every 5 minutes
        
    def start_monitoring(self):
        """Start the progress monitoring system"""
        if self.monitoring_active:
            return "⚠️  Progress monitoring already active"
        
        self.monitoring_active = True
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        return "✅ Goal progress monitoring started"
    
    def stop_monitoring(self):
        """Stop the progress monitoring system"""
        if not self.monitoring_active:
            return "⚠️  Progress monitoring not active"
        
        self.monitoring_active = False
        self.stop_event.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return "🛑 Goal progress monitoring stopped"
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                self._update_progress_history()
                self._check_goal_milestones()
                self._analyze_trends()
                
                # Wait for next check
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _update_progress_history(self):
        """Update progress history for all active goals"""
        active_goals = goal_tracker.get_active_goals()
        
        for goal in active_goals:
            current_progress = {
                'timestamp': datetime.now().isoformat(),
                'value': goal.current_value,
                'progress_percentage': goal.progress_percentage,
                'status': goal.status.value
            }
            
            # Add to history
            self.progress_history[goal.id].append(current_progress)
            
            # Keep only last 1000 entries per goal
            if len(self.progress_history[goal.id]) > 1000:
                self.progress_history[goal.id] = self.progress_history[goal.id][-1000:]
    
    def _check_goal_milestones(self):
        """Check for goal milestones and trigger notifications"""
        active_goals = goal_tracker.get_active_goals()
        
        for goal in active_goals:
            # Check for milestone achievements
            milestones = [25, 50, 75, 90, 95, 100]
            
            for milestone in milestones:
                if goal.progress_percentage >= milestone:
                    # Check if we've already notified about this milestone
                    if not self._milestone_already_notified(goal.id, milestone):
                        self._trigger_milestone_notification(goal, milestone)
    
    def _milestone_already_notified(self, goal_id: str, milestone: int) -> bool:
        """Check if we've already notified about a milestone"""
        # This is a simplified check - in practice, you'd want to store notification history
        history = self.progress_history.get(goal_id, [])
        if not history:
            return False
        
        # Check if any recent entry was below the milestone
        recent_entries = history[-10:]  # Last 10 entries
        for entry in recent_entries:
            if entry['progress_percentage'] < milestone:
                return False
        
        return True
    
    def _trigger_milestone_notification(self, goal: TradingGoal, milestone: int):
        """Trigger milestone notification"""
        notification = {
            'type': 'milestone',
            'goal_id': goal.id,
            'milestone': milestone,
            'goal_description': goal.description,
            'message': f"🎯 Milestone achieved! {goal.description} is {milestone}% complete",
            'timestamp': datetime.now().isoformat()
        }
        
        # Call notification callbacks
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                print(f"Error calling notification callback: {e}")
    
    def _analyze_trends(self):
        """Analyze progress trends for all goals"""
        active_goals = goal_tracker.get_active_goals()
        
        for goal in active_goals:
            history = self.progress_history.get(goal.id, [])
            if len(history) >= 2:
                trend = self._calculate_trend(history)
                
                # Store trend analysis
                if not hasattr(goal, 'trend_analysis'):
                    goal.trend_analysis = {}
                goal.trend_analysis = trend
    
    def _calculate_trend(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend analysis from progress history"""
        if len(history) < 2:
            return {'trend': 'insufficient_data', 'confidence': 0.0}
        
        # Get recent progress changes
        recent_entries = history[-10:]  # Last 10 entries
        
        # Calculate rate of change
        if len(recent_entries) >= 2:
            first_entry = recent_entries[0]
            last_entry = recent_entries[-1]
            
            time_diff = datetime.fromisoformat(last_entry['timestamp']) - datetime.fromisoformat(first_entry['timestamp'])
            value_diff = last_entry['value'] - first_entry['value']
            
            if time_diff.total_seconds() > 0:
                rate_per_hour = value_diff / (time_diff.total_seconds() / 3600)
                
                # Determine trend
                if rate_per_hour > 0.1:
                    trend = 'accelerating'
                elif rate_per_hour > 0.01:
                    trend = 'steady'
                elif rate_per_hour > -0.01:
                    trend = 'stable'
                else:
                    trend = 'declining'
                
                return {
                    'trend': trend,
                    'rate_per_hour': rate_per_hour,
                    'confidence': min(1.0, len(recent_entries) / 10),
                    'last_updated': datetime.now().isoformat()
                }
        
        return {'trend': 'stable', 'confidence': 0.5}
    
    def generate_progress_report(self, goal_id: str) -> Optional[ProgressReport]:
        """Generate a comprehensive progress report for a goal"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return None
        
        # Get progress history
        history = self.progress_history.get(goal_id, [])
        
        # Calculate days active
        days_active = (datetime.now() - goal.created_at).days
        if days_active == 0:
            days_active = 1
        
        # Calculate daily average progress
        if history:
            total_progress = goal.current_value
            daily_average = total_progress / days_active
        else:
            daily_average = 0
        
        # Estimate completion days
        estimated_completion = self._estimate_completion_days(goal, daily_average)
        
        # Get recent sessions
        recent_sessions = goal_tracker.get_daily_sessions(goal_id, days=7)
        
        # Generate trend analysis
        trend_analysis = self._calculate_trend(history)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(goal, recent_sessions)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(goal, performance_metrics, trend_analysis)
        
        return ProgressReport(
            goal_id=goal_id,
            goal_description=goal.description,
            target_value=goal.target_value,
            current_value=goal.current_value,
            progress_percentage=goal.progress_percentage,
            status=goal.status.value,
            days_active=days_active,
            daily_average_progress=daily_average,
            estimated_completion_days=estimated_completion,
            recent_sessions=recent_sessions,
            trend_analysis=trend_analysis,
            performance_metrics=performance_metrics,
            recommendations=recommendations
        )
    
    def _estimate_completion_days(self, goal: TradingGoal, daily_average: float) -> Optional[int]:
        """Estimate days to completion based on current progress"""
        if daily_average <= 0:
            return None
        
        remaining_progress = goal.target_value - goal.current_value
        estimated_days = remaining_progress / daily_average
        
        return max(1, int(estimated_days))
    
    def _calculate_performance_metrics(self, goal: TradingGoal, recent_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for a goal"""
        if not recent_sessions:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'average_profit': 0.0,
                'total_profit': 0.0,
                'trading_days': 0
            }
        
        total_trades = sum(session['trades_executed'] for session in recent_sessions)
        total_profit = sum(session['profit_loss'] for session in recent_sessions)
        profitable_sessions = len([s for s in recent_sessions if s['profit_loss'] > 0])
        
        return {
            'total_trades': total_trades,
            'win_rate': profitable_sessions / len(recent_sessions) if recent_sessions else 0,
            'average_profit': total_profit / len(recent_sessions) if recent_sessions else 0,
            'total_profit': total_profit,
            'trading_days': len(recent_sessions)
        }
    
    def _generate_recommendations(self, goal: TradingGoal, performance_metrics: Dict[str, Any], 
                                 trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on goal progress"""
        recommendations = []
        
        # Progress-based recommendations
        if goal.progress_percentage < 20:
            recommendations.append("🚀 Focus on establishing consistent daily trading routine")
        elif goal.progress_percentage < 50:
            recommendations.append("📈 Maintain current trading pace and strategy")
        elif goal.progress_percentage < 80:
            recommendations.append("🎯 You're making good progress! Stay focused on the goal")
        else:
            recommendations.append("🏆 Almost there! Maintain momentum for final push")
        
        # Performance-based recommendations
        if performance_metrics['win_rate'] < 0.4:
            recommendations.append("⚠️  Consider reviewing trading strategy - win rate below 40%")
        elif performance_metrics['win_rate'] > 0.7:
            recommendations.append("✅ Excellent win rate! Consider increasing position sizes")
        
        # Trend-based recommendations
        trend = trend_analysis.get('trend', 'stable')
        if trend == 'declining':
            recommendations.append("📉 Progress declining - consider strategy adjustment")
        elif trend == 'accelerating':
            recommendations.append("🚀 Accelerating progress - excellent momentum!")
        elif trend == 'stable':
            recommendations.append("📊 Stable progress - consistent performance")
        
        # Time-based recommendations
        if goal.days_remaining() and goal.days_remaining() < 7:
            recommendations.append("⏰ Less than 7 days remaining - increase trading frequency")
        
        return recommendations
    
    def get_all_goals_summary(self) -> Dict[str, Any]:
        """Get a summary of all goals"""
        all_goals = goal_tracker.get_all_goals()
        active_goals = [g for g in all_goals if g.status == GoalStatus.ACTIVE]
        completed_goals = [g for g in all_goals if g.status == GoalStatus.COMPLETED]
        
        # Calculate aggregated metrics
        total_progress = sum(g.progress_percentage for g in active_goals)
        avg_progress = total_progress / len(active_goals) if active_goals else 0
        
        # Get goals near completion
        near_completion = [g for g in active_goals if g.progress_percentage >= 80]
        
        return {
            'total_goals': len(all_goals),
            'active_goals': len(active_goals),
            'completed_goals': len(completed_goals),
            'average_progress': avg_progress,
            'goals_near_completion': len(near_completion),
            'monitoring_active': self.monitoring_active,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_goal_leaderboard(self) -> List[Dict[str, Any]]:
        """Get a leaderboard of goals by progress"""
        active_goals = goal_tracker.get_active_goals()
        
        leaderboard = []
        for goal in active_goals:
            recent_sessions = goal_tracker.get_daily_sessions(goal.id, days=7)
            performance_metrics = self._calculate_performance_metrics(goal, recent_sessions)
            
            leaderboard.append({
                'goal_id': goal.id,
                'description': goal.description,
                'progress_percentage': goal.progress_percentage,
                'current_value': goal.current_value,
                'target_value': goal.target_value,
                'days_active': (datetime.now() - goal.created_at).days,
                'win_rate': performance_metrics['win_rate'],
                'total_profit': performance_metrics['total_profit']
            })
        
        # Sort by progress percentage
        leaderboard.sort(key=lambda x: x['progress_percentage'], reverse=True)
        
        return leaderboard
    
    def add_notification_callback(self, callback: callable):
        """Add a notification callback function"""
        self.notification_callbacks.append(callback)
    
    def get_daily_progress_chart(self, goal_id: str, days: int = 30) -> Dict[str, Any]:
        """Get data for a daily progress chart"""
        goal = goal_tracker.get_goal(goal_id)
        if not goal:
            return {'error': 'Goal not found'}
        
        # Get progress history
        progress_history = goal_tracker.get_progress_history(goal_id, days)
        
        # Group by day
        daily_progress = defaultdict(list)
        for entry in progress_history:
            date = datetime.fromisoformat(entry['timestamp']).date()
            daily_progress[date].append(entry['progress_percentage'])
        
        # Calculate daily averages
        chart_data = []
        for date, percentages in daily_progress.items():
            avg_percentage = sum(percentages) / len(percentages)
            chart_data.append({
                'date': date.isoformat(),
                'progress_percentage': avg_percentage,
                'value': goal.target_value * (avg_percentage / 100)
            })
        
        # Sort by date
        chart_data.sort(key=lambda x: x['date'])
        
        return {
            'goal_id': goal_id,
            'goal_description': goal.description,
            'target_value': goal.target_value,
            'chart_data': chart_data,
            'generated_at': datetime.now().isoformat()
        }

# Global instance
progress_monitor = GoalProgressMonitor()

def start_progress_monitoring():
    """Start the progress monitoring system"""
    return progress_monitor.start_monitoring()

def stop_progress_monitoring():
    """Stop the progress monitoring system"""
    return progress_monitor.stop_monitoring()

def get_progress_report(goal_id: str) -> Optional[ProgressReport]:
    """Get a progress report for a goal"""
    return progress_monitor.generate_progress_report(goal_id)

def get_goals_summary() -> Dict[str, Any]:
    """Get a summary of all goals"""
    return progress_monitor.get_all_goals_summary()

def get_goals_leaderboard() -> List[Dict[str, Any]]:
    """Get a leaderboard of goals by progress"""
    return progress_monitor.get_goal_leaderboard()

def add_progress_notification_callback(callback: callable):
    """Add a notification callback"""
    progress_monitor.add_notification_callback(callback) 