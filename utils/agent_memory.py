#!/usr/bin/env python3
"""
Advanced Agent Memory and Learning System
Enables organic growth and experience-based learning for trading agents
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

@dataclass
class Experience:
    """Represents a single learning experience"""
    id: str
    agent_type: str
    action: str
    context: str
    outcome: str
    success_score: float  # -1.0 to +1.0
    timestamp: str
    market_conditions: Dict[str, Any]
    confidence: float
    feedback: Optional[str] = None

@dataclass
class Pattern:
    """Represents a learned pattern"""
    id: str
    pattern_type: str
    conditions: Dict[str, Any]
    expected_outcome: str
    success_rate: float
    confidence: float
    usage_count: int
    last_used: str
    created: str

@dataclass
class AgentPersonality:
    """Agent's evolving personality and preferences"""
    agent_type: str
    risk_tolerance: float
    decision_speed: float
    confidence_threshold: float
    learning_rate: float
    specializations: List[str]
    strengths: List[str]
    weaknesses: List[str]
    preferred_strategies: List[str]
    adaptation_history: List[Dict[str, Any]]

class AgentMemorySystem:
    """Advanced memory and learning system for trading agents"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.init_database()
        self.learning_threshold = 0.6  # Confidence threshold for pattern recognition
        self.decay_factor = 0.95  # How quickly old experiences fade
        
    def init_database(self):
        """Initialize the memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Experiences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                id TEXT PRIMARY KEY,
                agent_type TEXT,
                action TEXT,
                context TEXT,
                outcome TEXT,
                success_score REAL,
                timestamp TEXT,
                market_conditions TEXT,
                confidence REAL,
                feedback TEXT
            )
        ''')
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_type TEXT,
                conditions TEXT,
                expected_outcome TEXT,
                success_rate REAL,
                confidence REAL,
                usage_count INTEGER,
                last_used TEXT,
                created TEXT
            )
        ''')
        
        # Agent personalities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personalities (
                agent_type TEXT PRIMARY KEY,
                risk_tolerance REAL,
                decision_speed REAL,
                confidence_threshold REAL,
                learning_rate REAL,
                specializations TEXT,
                strengths TEXT,
                weaknesses TEXT,
                preferred_strategies TEXT,
                adaptation_history TEXT
            )
        ''')
        
        # Performance tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id TEXT PRIMARY KEY,
                agent_type TEXT,
                metric_type TEXT,
                value REAL,
                timestamp TEXT,
                context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_experience(self, experience: Experience):
        """Add a new experience to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO experiences 
            (id, agent_type, action, context, outcome, success_score, 
             timestamp, market_conditions, confidence, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            experience.id, experience.agent_type, experience.action,
            experience.context, experience.outcome, experience.success_score,
            experience.timestamp, json.dumps(experience.market_conditions),
            experience.confidence, experience.feedback
        ))
        
        conn.commit()
        conn.close()
        
        # Check if this experience creates a new pattern
        self._analyze_for_patterns(experience)
    
    def get_relevant_experiences(self, agent_type: str, context: str, limit: int = 10) -> List[Experience]:
        """Get relevant past experiences for current context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple similarity based on context keywords
        cursor.execute('''
            SELECT * FROM experiences 
            WHERE agent_type = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (agent_type, limit * 2))  # Get more to filter
        
        rows = cursor.fetchall()
        conn.close()
        
        experiences = []
        for row in rows:
            try:
                # Safely parse market_conditions JSON
                market_conditions = {}
                if row[7] and isinstance(row[7], str):
                    try:
                        market_conditions = json.loads(row[7])
                    except (json.JSONDecodeError, TypeError):
                        # If JSON parsing fails, use empty dict
                        market_conditions = {}
                
                exp = Experience(
                    id=row[0], agent_type=row[1], action=row[2],
                    context=row[3], outcome=row[4], success_score=row[5],
                    timestamp=row[6], market_conditions=market_conditions,
                    confidence=row[8], feedback=row[9]
                )
            except Exception as e:
                # Skip corrupted rows
                print(f"⚠️ Skipping corrupted experience row: {e}")
                continue
            
            # Calculate relevance score
            relevance = self._calculate_relevance(context, exp.context)
            if relevance > 0.3:  # Minimum relevance threshold
                experiences.append(exp)
        
        return sorted(experiences, key=lambda x: x.success_score, reverse=True)[:limit]
    
    def _calculate_relevance(self, current_context: str, past_context: str) -> float:
        """Calculate relevance between current and past contexts"""
        current_words = set(current_context.lower().split())
        past_words = set(past_context.lower().split())
        
        if not current_words or not past_words:
            return 0.0
        
        intersection = current_words.intersection(past_words)
        union = current_words.union(past_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _analyze_for_patterns(self, experience: Experience):
        """Analyze new experience for pattern formation"""
        similar_experiences = self.get_relevant_experiences(
            experience.agent_type, experience.context, limit=20
        )
        
        if len(similar_experiences) < 3:  # Need minimum experiences
            return
        
        # Group by similar outcomes
        outcome_groups = {}
        for exp in similar_experiences:
            if exp.outcome not in outcome_groups:
                outcome_groups[exp.outcome] = []
            outcome_groups[exp.outcome].append(exp)
        
        # Find patterns with high success rates
        for outcome, exps in outcome_groups.items():
            if len(exps) >= 3:  # Minimum for pattern
                success_rate = np.mean([exp.success_score for exp in exps])
                if success_rate > self.learning_threshold:
                    self._create_pattern(experience.agent_type, exps, outcome, success_rate)
    
    def _create_pattern(self, agent_type: str, experiences: List[Experience], 
                       outcome: str, success_rate: float):
        """Create a new learned pattern"""
        pattern_id = hashlib.md5(f"{agent_type}_{outcome}_{len(experiences)}".encode()).hexdigest()
        
        # Extract common conditions
        conditions = self._extract_common_conditions(experiences)
        
        pattern = Pattern(
            id=pattern_id,
            pattern_type="behavioral",
            conditions=conditions,
            expected_outcome=outcome,
            success_rate=success_rate,
            confidence=min(success_rate * len(experiences) / 10, 1.0),
            usage_count=0,
            last_used="",
            created=datetime.now().isoformat()
        )
        
        self._save_pattern(pattern)
    
    def _extract_common_conditions(self, experiences: List[Experience]) -> Dict[str, Any]:
        """Extract common conditions from a group of experiences"""
        conditions = {}
        
        # Analyze market conditions
        market_conditions = [exp.market_conditions for exp in experiences]
        
        # Find common patterns in market conditions
        if market_conditions:
            common_conditions = {}
            for key in market_conditions[0].keys():
                values = [mc.get(key) for mc in market_conditions if mc.get(key) is not None]
                if len(values) >= len(experiences) * 0.6:  # 70% commonality
                    if isinstance(values[0], (int, float)):
                        common_conditions[key] = {
                            'min': min(values),
                            'max': max(values),
                            'avg': sum(values) / len(values)
                        }
                    else:
                        # For non-numeric values, find most common
                        from collections import Counter
                        most_common = Counter(values).most_common(1)
                        if most_common:
                            common_conditions[key] = most_common[0][0]
            
            conditions['market_conditions'] = common_conditions
        
        return conditions
    
    def _save_pattern(self, pattern: Pattern):
        """Save a pattern to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO patterns 
            (id, pattern_type, conditions, expected_outcome, success_rate,
             confidence, usage_count, last_used, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.id, pattern.pattern_type, json.dumps(pattern.conditions),
            pattern.expected_outcome, pattern.success_rate, pattern.confidence,
            pattern.usage_count, pattern.last_used, pattern.created
        ))
        
        conn.commit()
        conn.close()
    
    def get_applicable_patterns(self, agent_type: str, current_context: Dict[str, Any]) -> List[Pattern]:
        """Get patterns applicable to current context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM patterns 
            WHERE confidence > ? 
            ORDER BY success_rate DESC, confidence DESC
        ''', (self.learning_threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        applicable_patterns = []
        for row in rows:
            try:
                # Safely parse conditions JSON
                conditions = {}
                if row[2] and isinstance(row[2], str):
                    try:
                        conditions = json.loads(row[2])
                    except (json.JSONDecodeError, TypeError):
                        # If JSON parsing fails, use empty dict
                        conditions = {}
                
                pattern = Pattern(
                    id=row[0], pattern_type=row[1], conditions=conditions,
                    expected_outcome=row[3], success_rate=row[4], confidence=row[5],
                    usage_count=row[6], last_used=row[7], created=row[8]
                )
                
                if self._pattern_matches_context(pattern, current_context):
                    applicable_patterns.append(pattern)
            except Exception as e:
                # Skip corrupted rows
                print(f"⚠️ Skipping corrupted pattern row: {e}")
                continue
        
        return applicable_patterns
    
    def _pattern_matches_context(self, pattern: Pattern, context: Dict[str, Any]) -> bool:
        """Check if a pattern matches current context"""
        pattern_conditions = pattern.conditions.get('market_conditions', {})
        
        for key, condition in pattern_conditions.items():
            if key not in context:
                continue
            
            current_value = context[key]
            
            if isinstance(condition, dict) and 'min' in condition:
                # Numeric range condition
                if not (condition['min'] <= current_value <= condition['max']):
                    return False
            elif condition != current_value:
                # Exact match condition
                return False
        
        return True
    
    def update_agent_personality(self, agent_type: str, performance_feedback: Dict[str, Any]):
        """Update agent personality based on performance feedback"""
        personality = self.get_agent_personality(agent_type)
        
        # Adapt based on performance
        if performance_feedback.get('success_rate', 0) > 0.6:
            # High success - increase confidence
            personality.confidence_threshold = min(personality.confidence_threshold + 0.05, 0.95)
        elif performance_feedback.get('success_rate', 0) < 0.4:
            # Low success - decrease confidence, increase caution
            personality.confidence_threshold = max(personality.confidence_threshold - 0.05, 0.3)
            personality.risk_tolerance = max(personality.risk_tolerance - 0.1, 0.1)
        
        # Track adaptation
        personality.adaptation_history.append({
            'timestamp': datetime.now().isoformat(),
            'reason': 'performance_feedback',
            'changes': performance_feedback,
            'new_confidence': personality.confidence_threshold,
            'new_risk_tolerance': personality.risk_tolerance
        })
        
        self._save_personality(personality)
    
    def get_agent_personality(self, agent_type: str) -> AgentPersonality:
        """Get or create agent personality"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM personalities WHERE agent_type = ?', (agent_type,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                # Safely parse JSON fields
                def safe_json_loads(data, default=[]):
                    if data and isinstance(data, str):
                        try:
                            return json.loads(data)
                        except (json.JSONDecodeError, TypeError):
                            return default
                    return default
                
                return AgentPersonality(
                    agent_type=row[0], risk_tolerance=row[1], decision_speed=row[2],
                    confidence_threshold=row[3], learning_rate=row[4],
                    specializations=safe_json_loads(row[5], []),
                    strengths=safe_json_loads(row[6], []),
                    weaknesses=safe_json_loads(row[7], []),
                    preferred_strategies=safe_json_loads(row[8], []),
                    adaptation_history=safe_json_loads(row[9], [])
                )
            except Exception as e:
                print(f"⚠️ Error parsing personality data: {e}")
                # Return default personality if parsing fails
                return self._create_default_personality(agent_type)
        else:
            # Create default personality
            personality = self._create_default_personality(agent_type)
            self._save_personality(personality)
            return personality
    
    def _create_default_personality(self, agent_type: str) -> AgentPersonality:
        """Create default personality for agent type"""
        defaults = {
            'analyst': {
                'risk_tolerance': 0.6,
                'decision_speed': 0.7,
                'confidence_threshold': 0.6,
                'specializations': ['technical_analysis', 'market_research'],
                'strengths': ['data_analysis', 'pattern_recognition'],
                'preferred_strategies': ['trend_following', 'fundamental_analysis']
            },
            'trader': {
                'risk_tolerance': 0.8,
                'decision_speed': 0.9,
                'confidence_threshold': 0.6,
                'specializations': ['execution', 'timing'],
                'strengths': ['quick_decisions', 'market_timing'],
                'preferred_strategies': ['momentum', 'swing_trading']
            },
            'risk': {
                'risk_tolerance': 0.3,
                'decision_speed': 0.5,
                'confidence_threshold': 0.6,
                'specializations': ['risk_assessment', 'portfolio_protection'],
                'strengths': ['conservative_analysis', 'downside_protection'],
                'preferred_strategies': ['diversification', 'hedging']
            }
        }
        
        agent_defaults = defaults.get(agent_type, defaults['analyst'])
        
        return AgentPersonality(
            agent_type=agent_type,
            risk_tolerance=agent_defaults['risk_tolerance'],
            decision_speed=agent_defaults['decision_speed'],
            confidence_threshold=agent_defaults['confidence_threshold'],
            learning_rate=0.1,
            specializations=agent_defaults['specializations'],
            strengths=agent_defaults['strengths'],
            weaknesses=[],
            preferred_strategies=agent_defaults['preferred_strategies'],
            adaptation_history=[]
        )
    
    def _save_personality(self, personality: AgentPersonality):
        """Save personality to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO personalities
            (agent_type, risk_tolerance, decision_speed, confidence_threshold,
             learning_rate, specializations, strengths, weaknesses,
             preferred_strategies, adaptation_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            personality.agent_type, personality.risk_tolerance, personality.decision_speed,
            personality.confidence_threshold, personality.learning_rate,
            json.dumps(personality.specializations), json.dumps(personality.strengths),
            json.dumps(personality.weaknesses), json.dumps(personality.preferred_strategies),
            json.dumps(personality.adaptation_history)
        ))
        
        conn.commit()
        conn.close()
    
    def generate_learning_insights(self, agent_type: str) -> Dict[str, Any]:
        """Generate insights about what the agent has learned"""
        experiences = self.get_relevant_experiences(agent_type, "", limit=100)
        patterns = self.get_applicable_patterns(agent_type, {})
        personality = self.get_agent_personality(agent_type)
        
        insights = {
            'total_experiences': len(experiences),
            'learned_patterns': len(patterns),
            'average_success_rate': np.mean([exp.success_score for exp in experiences]) if experiences else 0,
            'confidence_evolution': self._analyze_confidence_evolution(experiences),
            'strongest_patterns': sorted(patterns, key=lambda p: p.success_rate, reverse=True)[:3],
            'personality_changes': len(personality.adaptation_history),
            'current_specializations': personality.specializations,
            'learning_trajectory': self._analyze_learning_trajectory(experiences)
        }
        
        return insights
    
    def _analyze_confidence_evolution(self, experiences: List[Experience]) -> Dict[str, float]:
        """Analyze how confidence has evolved over time"""
        if not experiences:
            return {'initial': 0, 'current': 0, 'trend': 'stable'}
        
        sorted_exp = sorted(experiences, key=lambda x: x.timestamp)
        initial = sorted_exp[0].confidence
        current = sorted_exp[-1].confidence
        
        # Calculate trend
        recent_confidence = np.mean([exp.confidence for exp in sorted_exp[-10:]])
        early_confidence = np.mean([exp.confidence for exp in sorted_exp[:10]])
        
        if recent_confidence > early_confidence + 0.1:
            trend = 'improving'
        elif recent_confidence < early_confidence - 0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'initial': initial,
            'current': current,
            'trend': trend,
            'change': current - initial
        }
    
    def _analyze_learning_trajectory(self, experiences: List[Experience]) -> str:
        """Analyze the learning trajectory of the agent"""
        if len(experiences) < 10:
            return "insufficient_data"
        
        sorted_exp = sorted(experiences, key=lambda x: x.timestamp)
        
        # Split into periods
        period_size = len(sorted_exp) // 3
        early = sorted_exp[:period_size]
        middle = sorted_exp[period_size:period_size*2]
        recent = sorted_exp[period_size*2:]
        
        early_success = np.mean([exp.success_score for exp in early])
        middle_success = np.mean([exp.success_score for exp in middle])
        recent_success = np.mean([exp.success_score for exp in recent])
        
        if recent_success > middle_success > early_success:
            return "consistent_improvement"
        elif recent_success > early_success + 0.2:
            return "significant_improvement"
        elif recent_success < early_success - 0.2:
            return "performance_decline"
        else:
            return "stable_performance"

# Global memory system instance
memory_system = AgentMemorySystem()

def record_experience(agent_type: str, action: str, context: str, 
                     outcome: str, success_score: float, 
                     market_conditions: Dict[str, Any],
                     confidence: float = 0.5) -> str:
    """Record a new experience for learning"""
    experience_id = hashlib.md5(f"{agent_type}_{action}_{datetime.now()}".encode()).hexdigest()
    
    experience = Experience(
        id=experience_id,
        agent_type=agent_type,
        action=action,
        context=context,
        outcome=outcome,
        success_score=success_score,
        timestamp=datetime.now().isoformat(),
        market_conditions=market_conditions,
        confidence=confidence
    )
    
    memory_system.add_experience(experience)
    return experience_id

def get_agent_wisdom(agent_type: str, current_context: str) -> Dict[str, Any]:
    """Get accumulated wisdom for decision making"""
    relevant_experiences = memory_system.get_relevant_experiences(agent_type, current_context)
    applicable_patterns = memory_system.get_applicable_patterns(agent_type, {})
    personality = memory_system.get_agent_personality(agent_type)
    
    return {
        'relevant_experiences': relevant_experiences[:5],  # Top 5 most relevant
        'applicable_patterns': applicable_patterns[:3],   # Top 3 patterns
        'personality': personality,
        'recommendations': generate_recommendations(relevant_experiences, applicable_patterns, personality)
    }

def generate_recommendations(experiences: List[Experience], patterns: List[Pattern], 
                           personality: AgentPersonality) -> List[str]:
    """Generate recommendations based on accumulated wisdom"""
    recommendations = []
    
    if experiences:
        avg_success = np.mean([exp.success_score for exp in experiences])
        if avg_success > 0.7:
            recommendations.append(f"High success rate ({avg_success:.1%}) in similar situations")
        else:
            recommendations.append(f"Caution: Lower success rate ({avg_success:.1%}) in similar contexts")
    
    if patterns:
        best_pattern = max(patterns, key=lambda p: p.success_rate)
        recommendations.append(f"Apply pattern: {best_pattern.expected_outcome} (success rate: {best_pattern.success_rate:.1%})")
    
    # Personality-based recommendations
    if personality.risk_tolerance < 0.5:
        recommendations.append("Conservative approach recommended based on risk profile")
    elif personality.risk_tolerance > 0.6:
        recommendations.append("Aggressive approach acceptable based on risk profile")
    
    return recommendations 