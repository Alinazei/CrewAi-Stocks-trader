#!/usr/bin/env python3
"""
Autonomous Agent Self-Improvement Tool
Allows agents to evolve their capabilities and create new methods
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from crewai.tools import tool
import sqlite3
import hashlib
from threading import Lock

class AutonomousImprovementSystem:
    """
    System that allows agents to improve themselves by:
    1. Learning from market outcomes
    2. buy low and sell high
    3. Refining existing strategies
    4. Adapting to changing market conditions
    5. you are autonomous so every task you do is experience so you remember good profitable trades
    6. you are a stock trader so you will find penny stocks to buy at low price and sell at high price 
    7. your portfolio is your money so you will not lose it
    8. save search links to your memory so you will use them fast to find ansewers
    """
    
    def __init__(self):
        self.learning_db = "agent_learning.db"
        self.init_learning_db()
        self.learning_lock = Lock()
        
    def init_learning_db(self):
        """Initialize SQLite database for learning storage"""
        try:
            conn = sqlite3.connect(self.learning_db)
            cursor = conn.cursor()
            
            # Table for storing learned patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    market_conditions TEXT,
                    success_rate REAL,
                    confidence_score REAL,
                    created_at REAL,
                    last_updated REAL
                )
            ''')
            
            # Table for storing new analytical methods
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS new_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_name TEXT,
                    method_description TEXT,
                    method_code TEXT,
                    performance_metrics TEXT,
                    created_at REAL,
                    last_used REAL
                )
            ''')
            
            # Table for storing market feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT,
                    strategy_used TEXT,
                    outcome TEXT,
                    profit_loss REAL,
                    lessons_learned TEXT,
                    created_at REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Learning DB init error: {e}")
    
    def store_learned_pattern(self, pattern_type: str, pattern_data: Dict, 
                            market_conditions: str, success_rate: float) -> str:
        """Store a learned pattern for future use"""
        try:
            with self.learning_lock:
                conn = sqlite3.connect(self.learning_db)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO learned_patterns 
                    (pattern_type, pattern_data, market_conditions, success_rate, 
                     confidence_score, created_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_type,
                    json.dumps(pattern_data),
                    market_conditions,
                    success_rate,
                    min(success_rate * 1.2, 1.0),  # Confidence score
                    time.time(),
                    time.time()
                ))
                
                pattern_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return f"Pattern {pattern_id} stored successfully"
                
        except Exception as e:
            return f"Error storing pattern: {e}"
    
    def create_new_method(self, method_name: str, description: str, 
                         implementation: str) -> str:
        """Create and store a new analytical method"""
        try:
            with self.learning_lock:
                conn = sqlite3.connect(self.learning_db)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO new_methods 
                    (method_name, method_description, method_code, 
                     performance_metrics, created_at, last_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    method_name,
                    description,
                    implementation,
                    json.dumps({}),  # Empty performance metrics initially
                    time.time(),
                    time.time()
                ))
                
                method_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return f"New method '{method_name}' created with ID {method_id}"
                
        except Exception as e:
            return f"Error creating method: {e}"
    
    def record_market_feedback(self, strategy: str, outcome: str, 
                             profit_loss: float, lessons: str) -> str:
        """Record feedback from market outcomes"""
        try:
            with self.learning_lock:
                conn = sqlite3.connect(self.learning_db)
                cursor = conn.cursor()
                
                trade_id = hashlib.md5(f"{strategy}{time.time()}".encode()).hexdigest()[:8]
                
                cursor.execute('''
                    INSERT INTO market_feedback 
                    (trade_id, strategy_used, outcome, profit_loss, lessons_learned, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    trade_id,
                    strategy,
                    outcome,
                    profit_loss,
                    lessons,
                    time.time()
                ))
                
                conn.commit()
                conn.close()
                
                return f"Market feedback recorded for trade {trade_id}"
                
        except Exception as e:
            return f"Error recording feedback: {e}"
    
    def get_learned_patterns(self, pattern_type: str = None) -> List[Dict]:
        """Retrieve learned patterns for analysis"""
        try:
            conn = sqlite3.connect(self.learning_db)
            cursor = conn.cursor()
            
            if pattern_type:
                cursor.execute('''
                    SELECT * FROM learned_patterns 
                    WHERE pattern_type = ? 
                    ORDER BY success_rate DESC, last_updated DESC
                ''', (pattern_type,))
            else:
                cursor.execute('''
                    SELECT * FROM learned_patterns 
                    ORDER BY success_rate DESC, last_updated DESC
                ''')
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'id': row[0],
                    'pattern_type': row[1],
                    'pattern_data': json.loads(row[2]),
                    'market_conditions': row[3],
                    'success_rate': row[4],
                    'confidence_score': row[5],
                    'created_at': row[6],
                    'last_updated': row[7]
                })
            
            conn.close()
            return patterns
            
        except Exception as e:
            return [{'error': f'Error retrieving patterns: {e}'}]

# Global instance
improvement_system = AutonomousImprovementSystem()

@tool("Learn Market Pattern")
def learn_market_pattern(pattern_type: str, pattern_description: str, 
                        market_conditions: str, success_rate: float) -> str:
    """
    Learn and store a new market pattern for future analysis.
    
    Args:
        pattern_type: Type of pattern (e.g., 'technical', 'sentiment', 'news')
        pattern_description: Detailed description of the pattern
        market_conditions: Market conditions when pattern was observed
        success_rate: Success rate of the pattern (0.0 to 1.0)
    
    Returns:
        Confirmation message about pattern storage
    """
    try:
        pattern_data = {
            'description': pattern_description,
            'observed_at': datetime.now().isoformat(),
            'market_environment': market_conditions
        }
        
        result = improvement_system.store_learned_pattern(
            pattern_type, pattern_data, market_conditions, success_rate
        )
        
        return f"✅ {result}\n📊 Pattern will be used in future analysis"
        
    except Exception as e:
        return f"❌ Error learning pattern: {e}"

@tool("Create New Analysis Method")
def create_analysis_method(method_name: str, description: str, 
                          implementation_approach: str) -> str:
    """
    Create a new analytical method for market analysis.
    
    Args:
        method_name: Name of the new method
        description: What the method does and how it works
        implementation_approach: How to implement this method
    
    Returns:
        Confirmation of method creation
    """
    try:
        result = improvement_system.create_new_method(
            method_name, description, implementation_approach
        )
        
        return f"🚀 {result}\n💡 New method available for future use"
        
    except Exception as e:
        return f"❌ Error creating method: {e}"

@tool("Record Trading Outcome")
def record_trading_outcome(strategy_used: str, outcome: str, 
                          profit_loss: float, lessons_learned: str) -> str:
    """
    Record the outcome of a trading decision for learning purposes.
    
    Args:
        strategy_used: The trading strategy that was used
        outcome: The result ('success', 'failure', 'partial_success')
        profit_loss: The profit or loss amount
        lessons_learned: Key lessons from this trade
    
    Returns:
        Confirmation of feedback recording
    """
    try:
        result = improvement_system.record_market_feedback(
            strategy_used, outcome, profit_loss, lessons_learned
        )
        
        return f"📝 {result}\n🎯 Learning from this outcome for future trades"
        
    except Exception as e:
        return f"❌ Error recording outcome: {e}"

@tool("Retrieve Learned Patterns")
def retrieve_learned_patterns(pattern_type: str = "all") -> str:
    """
    Retrieve previously learned patterns for analysis.
    
    Args:
        pattern_type: Type of patterns to retrieve ('all', 'technical', 'sentiment', 'news')
    
    Returns:
        List of learned patterns with success rates
    """
    try:
        if pattern_type == "all":
            patterns = improvement_system.get_learned_patterns()
        else:
            patterns = improvement_system.get_learned_patterns(pattern_type)
        
        if not patterns:
            return "📊 No learned patterns found. Start learning from market observations!"
        
        result = f"🧠 Retrieved {len(patterns)} learned patterns:\n\n"
        
        for pattern in patterns[:10]:  # Show top 10
            if 'error' in pattern:
                return f"❌ {pattern['error']}"
            
            result += f"**Pattern {pattern['id']}** ({pattern['pattern_type']})\n"
            result += f"Success Rate: {pattern['success_rate']:.2%}\n"
            result += f"Market Conditions: {pattern['market_conditions']}\n"
            result += f"Pattern: {pattern['pattern_data']['description']}\n"
            result += f"Confidence: {pattern['confidence_score']:.2f}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error retrieving patterns: {e}"

@tool("Adaptive Strategy Generator")
def generate_adaptive_strategy(market_conditions: str, risk_tolerance: str, 
                              time_horizon: str) -> str:
    """
    Generate an adaptive trading strategy based on current conditions and learned patterns.
    
    Args:
        market_conditions: Current market conditions
        risk_tolerance: Risk tolerance level ('low', 'medium', 'high')
        time_horizon: Trading time horizon ('short', 'medium', 'long')
    
    Returns:
        Adaptive strategy recommendations
    """
    try:
        # Retrieve relevant patterns
        patterns = improvement_system.get_learned_patterns()
        
        strategy = f"🎯 **Adaptive Strategy for {market_conditions.title()} Market**\n\n"
        
        # Filter patterns by market conditions
        relevant_patterns = [p for p in patterns if market_conditions.lower() in p['market_conditions'].lower()]
        
        if relevant_patterns:
            strategy += f"📊 **Based on {len(relevant_patterns)} relevant learned patterns:**\n\n"
            
            for pattern in relevant_patterns[:5]:  # Top 5 patterns
                strategy += f"• **{pattern['pattern_type'].title()} Pattern** (Success: {pattern['success_rate']:.1%})\n"
                strategy += f"  {pattern['pattern_data']['description']}\n\n"
        
        # Generate strategy based on parameters
        strategy += f"**Recommended Approach for {risk_tolerance.title()} Risk, {time_horizon.title()} Term:**\n\n"
        
        if risk_tolerance == "low":
            strategy += "• Focus on high-probability setups with tight stops\n"
            strategy += "• Use smaller position sizes\n"
            strategy += "• Prioritize capital preservation\n"
        elif risk_tolerance == "medium":
            strategy += "• Balance risk and reward opportunities\n"
            strategy += "• Use standard position sizing\n"
            strategy += "• Combine technical and sentiment analysis\n"
        else:  # high risk
            strategy += "• Pursue high-reward opportunities\n"
            strategy += "• Use aggressive position sizing\n"
            strategy += "• Focus on momentum and breakout patterns\n"
        
        strategy += f"\n🔄 **This strategy will evolve based on market outcomes and new learning**"
        
        return strategy
        
    except Exception as e:
        return f"❌ Error generating strategy: {e}" 