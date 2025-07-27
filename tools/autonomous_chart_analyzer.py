#!/usr/bin/env python3
"""
Autonomous Chart Analyzer for CrewAI Trading Agents
==================================================

This module enables agents to autonomously read charts, analyze price patterns,
and make intelligent buy/sell decisions without human intervention.
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from crewai.tools import tool
import warnings
warnings.filterwarnings('ignore')

class AutonomousChartAnalyzer:
    """Autonomous chart analysis and trading decision maker
    if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
    """
    
    def __init__(self):
        self.min_data_points = 50
        self.confidence_threshold = 0.7
        self.risk_reward_ratio = 2.0
        
    def get_stock_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """Get comprehensive stock data"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval='1d')
            if data.empty or len(data) < self.min_data_points:
                raise ValueError(f"Insufficient data for {symbol}")
            return data
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        indicators = {}
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        indicators['macd'] = exp1 - exp2
        indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # Moving Averages
        indicators['sma_20'] = data['Close'].rolling(window=20).mean()
        indicators['sma_50'] = data['Close'].rolling(window=50).mean()
        indicators['sma_200'] = data['Close'].rolling(window=200).mean()
        indicators['ema_12'] = data['Close'].ewm(span=12).mean()
        indicators['ema_26'] = data['Close'].ewm(span=26).mean()
        
        # Bollinger Bands
        sma20 = indicators['sma_20']
        std20 = data['Close'].rolling(window=20).std()
        indicators['bb_upper'] = sma20 + (std20 * 2)
        indicators['bb_lower'] = sma20 - (std20 * 2)
        indicators['bb_middle'] = sma20
        
        # Stochastic
        low_min = data['Low'].rolling(window=14).min()
        high_max = data['High'].rolling(window=14).max()
        indicators['stoch_k'] = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        indicators['stoch_d'] = indicators['stoch_k'].rolling(window=3).mean()
        
        # Volume indicators
        indicators['volume_sma'] = data['Volume'].rolling(window=20).mean()
        indicators['volume_ratio'] = data['Volume'] / indicators['volume_sma']
        
        # ATR (Average True Range)
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        indicators['atr'] = true_range.rolling(window=14).mean()
        
        return indicators
    
    def detect_chart_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect chart patterns autonomously"""
        patterns = []
        
        # Double Bottom Pattern
        if self._detect_double_bottom(data):
            patterns.append({
                'pattern': 'Double Bottom',
                'signal': 'BUY',
                'confidence': 0.8,
                'description': 'Bullish reversal pattern indicating potential upward movement'
            })
        
        # Double Top Pattern
        if self._detect_double_top(data):
            patterns.append({
                'pattern': 'Double Top',
                'signal': 'SELL',
                'confidence': 0.8,
                'description': 'Bearish reversal pattern indicating potential downward movement'
            })
        
        # Head and Shoulders
        if self._detect_head_shoulders(data):
            patterns.append({
                'pattern': 'Head and Shoulders',
                'signal': 'SELL',
                'confidence': 0.85,
                'description': 'Strong bearish reversal pattern'
            })
        
        # Inverse Head and Shoulders
        if self._detect_inverse_head_shoulders(data):
            patterns.append({
                'pattern': 'Inverse Head and Shoulders',
                'signal': 'BUY',
                'confidence': 0.85,
                'description': 'Strong bullish reversal pattern'
            })
        
        # Cup and Handle
        if self._detect_cup_handle(data):
            patterns.append({
                'pattern': 'Cup and Handle',
                'signal': 'BUY',
                'confidence': 0.75,
                'description': 'Bullish continuation pattern'
            })
        
        # Triangle Patterns
        triangle = self._detect_triangle_pattern(data)
        if triangle:
            patterns.append(triangle)
        
        return patterns
    
    def _detect_double_bottom(self, data: pd.DataFrame) -> bool:
        """Detect double bottom pattern"""
        try:
            # Look for two significant lows with a peak in between
            lows = data[data['Low'] == data['Low'].rolling(window=10, center=True).min()]
            if len(lows) < 2:
                return False
            
            # Check if lows are similar in price and have a peak between them
            for i in range(len(lows) - 1):
                low1 = lows.iloc[i]
                low2 = lows.iloc[i + 1]
                
                # Check if lows are within 3% of each other
                price_diff = abs(low1['Low'] - low2['Low']) / low1['Low']
                if price_diff > 0.03:
                    continue
                
                # Check if there's a peak between the lows
                between_data = data[(data.index > low1.name) & (data.index < low2.name)]
                if len(between_data) > 0:
                    peak = between_data['High'].max()
                    if peak > low1['Low'] * 1.05:  # Peak should be at least 5% higher
                        return True
            
            return False
        except:
            return False
    
    def _detect_double_top(self, data: pd.DataFrame) -> bool:
        """Detect double top pattern"""
        try:
            # Look for two significant highs with a trough in between
            highs = data[data['High'] == data['High'].rolling(window=10, center=True).max()]
            if len(highs) < 2:
                return False
            
            # Check if highs are similar in price and have a trough between them
            for i in range(len(highs) - 1):
                high1 = highs.iloc[i]
                high2 = highs.iloc[i + 1]
                
                # Check if highs are within 3% of each other
                price_diff = abs(high1['High'] - high2['High']) / high1['High']
                if price_diff > 0.03:
                    continue
                
                # Check if there's a trough between the highs
                between_data = data[(data.index > high1.name) & (data.index < high2.name)]
                if len(between_data) > 0:
                    trough = between_data['Low'].min()
                    if trough < high1['High'] * 0.95:  # Trough should be at least 5% lower
                        return True
            
            return False
        except:
            return False
    
    def _detect_head_shoulders(self, data: pd.DataFrame) -> bool:
        """Detect head and shoulders pattern"""
        try:
            # Simplified detection - look for three peaks with middle peak higher
            highs = data[data['High'] == data['High'].rolling(window=15, center=True).max()]
            if len(highs) < 3:
                return False
            
            for i in range(len(highs) - 2):
                left = highs.iloc[i]['High']
                head = highs.iloc[i + 1]['High']
                right = highs.iloc[i + 2]['High']
                
                # Head should be higher than shoulders
                if head > left and head > right:
                    # Shoulders should be similar in height
                    shoulder_diff = abs(left - right) / left
                    if shoulder_diff < 0.05:  # Within 5%
                        return True
            
            return False
        except:
            return False
    
    def _detect_inverse_head_shoulders(self, data: pd.DataFrame) -> bool:
        """Detect inverse head and shoulders pattern"""
        try:
            # Look for three troughs with middle trough lower
            lows = data[data['Low'] == data['Low'].rolling(window=15, center=True).min()]
            if len(lows) < 3:
                return False
            
            for i in range(len(lows) - 2):
                left = lows.iloc[i]['Low']
                head = lows.iloc[i + 1]['Low']
                right = lows.iloc[i + 2]['Low']
                
                # Head should be lower than shoulders
                if head < left and head < right:
                    # Shoulders should be similar in height
                    shoulder_diff = abs(left - right) / left
                    if shoulder_diff < 0.05:  # Within 5%
                        return True
            
            return False
        except:
            return False
    
    def _detect_cup_handle(self, data: pd.DataFrame) -> bool:
        """Detect cup and handle pattern"""
        try:
            # Simplified cup and handle detection
            # Look for U-shaped price movement followed by small consolidation
            window = 30
            if len(data) < window:
                return False
            
            # Check for U-shaped movement in recent data
            recent_data = data.tail(window)
            start_price = recent_data.iloc[0]['Close']
            end_price = recent_data.iloc[-1]['Close']
            min_price = recent_data['Low'].min()
            
            # Cup should have similar start and end prices
            price_diff = abs(start_price - end_price) / start_price
            if price_diff < 0.03:  # Within 3%
                # Should have a dip in the middle
                if min_price < start_price * 0.95:  # At least 5% dip
                    return True
            
            return False
        except:
            return False
    
    def _detect_triangle_pattern(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        try:
            # Look for converging trendlines
            recent_data = data.tail(30)
            highs = recent_data['High'].values
            lows = recent_data['Low'].values
            
            # Calculate trendlines
            high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
            low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
            
            # Ascending triangle (flat top, rising bottom)
            if abs(high_slope) < 0.1 and low_slope > 0.1:
                return {
                    'pattern': 'Ascending Triangle',
                    'signal': 'BUY',
                    'confidence': 0.7,
                    'description': 'Bullish continuation pattern with flat resistance and rising support'
                }
            
            # Descending triangle (falling top, flat bottom)
            elif high_slope < -0.1 and abs(low_slope) < 0.1:
                return {
                    'pattern': 'Descending Triangle',
                    'signal': 'SELL',
                    'confidence': 0.7,
                    'description': 'Bearish continuation pattern with falling resistance and flat support'
                }
            
            # Symmetrical triangle (converging lines)
            elif abs(high_slope - low_slope) < 0.2:
                return {
                    'pattern': 'Symmetrical Triangle',
                    'signal': 'NEUTRAL',
                    'confidence': 0.6,
                    'description': 'Consolidation pattern - wait for breakout direction'
                }
            
            return None
        except:
            return None
    
    def analyze_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze support and resistance levels"""
        try:
            # Find recent highs and lows
            highs = data['High'].rolling(window=20, center=True).max()
            lows = data['Low'].rolling(window=20, center=True).min()
            
            # Current price
            current_price = data['Close'].iloc[-1]
            
            # Find nearest support and resistance
            resistance_levels = highs[highs > current_price].unique()
            support_levels = lows[lows < current_price].unique()
            
            nearest_resistance = min(resistance_levels) if len(resistance_levels) > 0 else None
            nearest_support = max(support_levels) if len(support_levels) > 0 else None
            
            return {
                'current_price': current_price,
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'resistance_distance': (nearest_resistance - current_price) / current_price if nearest_resistance else None,
                'support_distance': (current_price - nearest_support) / current_price if nearest_support else None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def make_autonomous_trading_decision(self, symbol: str, period: str = '1y') -> Dict[str, Any]:
        """Make autonomous trading decision based on chart analysis"""
        data = self.get_stock_data(symbol, period)
        if data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Calculate indicators
        indicators = self.calculate_technical_indicators(data)
        
        # Detect patterns
        patterns = self.detect_chart_patterns(data)
        
        # Analyze support/resistance
        levels = self.analyze_support_resistance(data)
        
        # Current values
        current_price = data['Close'].iloc[-1]
        current_rsi = indicators['rsi'].iloc[-1]
        current_macd = indicators['macd'].iloc[-1]
        current_macd_signal = indicators['macd_signal'].iloc[-1]
        
        # Decision logic
        decision = self._calculate_decision(
            current_price, current_rsi, current_macd, current_macd_signal,
            patterns, levels, indicators, data
        )
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'decision': decision['action'],
            'confidence': decision['confidence'],
            'reasoning': decision['reasoning'],
            'patterns_detected': patterns,
            'support_resistance': levels,
            'technical_indicators': {
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'sma_20': indicators['sma_20'].iloc[-1],
                'sma_50': indicators['sma_50'].iloc[-1],
                'sma_200': indicators['sma_200'].iloc[-1]
            },
            'risk_assessment': decision['risk_assessment'],
            'entry_price': decision['entry_price'],
            'stop_loss': decision['stop_loss'],
            'take_profit': decision['take_profit']
        }
    
    def _calculate_decision(self, price, rsi, macd, macd_signal, patterns, levels, indicators, data):
        """Calculate trading decision based on all factors"""
        score = 0
        reasons = []
        
        # RSI Analysis
        if rsi < 30:
            score += 2
            reasons.append("RSI oversold (< 30)")
        elif rsi > 70:
            score -= 2
            reasons.append("RSI overbought (> 70)")
        elif rsi < 50:
            score += 1
            reasons.append("RSI below midpoint")
        
        # MACD Analysis
        if macd > macd_signal:
            score += 1
            reasons.append("MACD above signal line")
        else:
            score -= 1
            reasons.append("MACD below signal line")
        
        # Moving Average Analysis
        sma_20 = indicators['sma_20'].iloc[-1]
        sma_50 = indicators['sma_50'].iloc[-1]
        sma_200 = indicators['sma_200'].iloc[-1]
        
        if price > sma_20 > sma_50:
            score += 2
            reasons.append("Price above 20MA and 50MA (bullish alignment)")
        elif price < sma_20 < sma_50:
            score -= 2
            reasons.append("Price below 20MA and 50MA (bearish alignment)")
        
        if price > sma_200:
            score += 1
            reasons.append("Price above 200MA (long-term bullish)")
        else:
            score -= 1
            reasons.append("Price below 200MA (long-term bearish)")
        
        # Pattern Analysis
        for pattern in patterns:
            if pattern['signal'] == 'BUY':
                score += pattern['confidence'] * 2
                reasons.append(f"Bullish pattern: {pattern['pattern']}")
            elif pattern['signal'] == 'SELL':
                score -= pattern['confidence'] * 2
                reasons.append(f"Bearish pattern: {pattern['pattern']}")
        
        # Support/Resistance Analysis
        if levels.get('nearest_support') and levels.get('nearest_resistance'):
            support_dist = levels['support_distance']
            resistance_dist = levels['resistance_distance']
            
            if support_dist and resistance_dist:
                if support_dist < resistance_dist:
                    score += 1
                    reasons.append("Closer to support than resistance")
                else:
                    score -= 1
                    reasons.append("Closer to resistance than support")
        
        # Volume Analysis
        volume_ratio = indicators['volume_ratio'].iloc[-1]
        if volume_ratio > 1.5:
            score += 1
            reasons.append("High volume (1.5x average)")
        elif volume_ratio < 0.5:
            score -= 1
            reasons.append("Low volume (0.5x average)")
        
        # Decision based on score
        if score >= 3:
            action = "BUY"
            confidence = min(0.95, 0.7 + (score - 3) * 0.1)
        elif score <= -3:
            action = "SELL"
            confidence = min(0.95, 0.7 + abs(score + 3) * 0.1)
        else:
            action = "HOLD"
            confidence = 0.5
        
        # Calculate entry, stop loss, and take profit
        atr = indicators['atr'].iloc[-1]
        
        if action == "BUY":
            entry_price = price
            stop_loss = price - (atr * 2)  # 2 ATR below entry
            take_profit = price + (atr * 4)  # 4 ATR above entry (2:1 risk/reward)
        elif action == "SELL":
            entry_price = price
            stop_loss = price + (atr * 2)  # 2 ATR above entry
            take_profit = price - (atr * 4)  # 4 ATR below entry (2:1 risk/reward)
        else:
            entry_price = price
            stop_loss = None
            take_profit = None
        
        # Risk assessment
        if action != "HOLD":
            risk_amount = abs(entry_price - stop_loss) if stop_loss else 0
            reward_amount = abs(take_profit - entry_price) if take_profit else 0
            risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
        else:
            risk_reward = 0
        
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasons,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_assessment': {
                'risk_reward_ratio': risk_reward,
                'atr': atr,
                'volatility': 'High' if atr > price * 0.03 else 'Medium' if atr > price * 0.02 else 'Low'
            }
        }

# Initialize analyzer
autonomous_analyzer = AutonomousChartAnalyzer()

# CrewAI Tools
@tool("Autonomous Chart Reader")
def read_chart_autonomously(symbol: str, period: str = "1y") -> str:
    """
    AUTONOMOUSLY read and analyze stock charts to make trading decisions.
    This tool analyzes price patterns, technical indicators, and makes BUY/SELL/HOLD decisions.
    
    Parameters:
        symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA')
        period (str): Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
    
    Returns:
        str: Autonomous trading decision with reasoning and risk assessment
    """
    try:
        decision = autonomous_analyzer.make_autonomous_trading_decision(symbol, period)
        
        if 'error' in decision:
            return f"❌ Error: {decision['error']}"
        
        # Format the decision output
        output = f"🎯 AUTONOMOUS CHART ANALYSIS: {symbol}\n"
        output += "=" * 60 + "\n\n"
        
        output += f"📊 CURRENT PRICE: ${decision['current_price']:.2f}\n"
        output += f"🎯 DECISION: {decision['decision']}\n"
        output += f"🎯 CONFIDENCE: {decision['confidence']:.1%}\n\n"
        
        output += "📈 TECHNICAL INDICATORS:\n"
        indicators = decision['technical_indicators']
        output += f"• RSI: {indicators['rsi']:.1f} {'(Oversold)' if indicators['rsi'] < 30 else '(Overbought)' if indicators['rsi'] > 70 else ''}\n"
        output += f"• MACD: {indicators['macd']:.2f} {'(Bullish)' if indicators['macd'] > indicators['macd_signal'] else '(Bearish)'}\n"
        output += f"• 20MA: ${indicators['sma_20']:.2f} {'(Above)' if decision['current_price'] > indicators['sma_20'] else '(Below)'}\n"
        output += f"• 50MA: ${indicators['sma_50']:.2f} {'(Above)' if decision['current_price'] > indicators['sma_50'] else '(Below)'}\n"
        output += f"• 200MA: ${indicators['sma_200']:.2f} {'(Above)' if decision['current_price'] > indicators['sma_200'] else '(Below)'}\n\n"
        
        if decision['patterns_detected']:
            output += "🔍 CHART PATTERNS DETECTED:\n"
            for pattern in decision['patterns_detected']:
                output += f"• {pattern['pattern']}: {pattern['signal']} ({pattern['confidence']:.1%} confidence)\n"
            output += "\n"
        
        if decision['support_resistance'].get('nearest_support') and decision['support_resistance'].get('nearest_resistance'):
            levels = decision['support_resistance']
            output += "📏 SUPPORT/RESISTANCE:\n"
            output += f"• Support: ${levels['nearest_support']:.2f} ({levels['support_distance']:.1%} below)\n"
            output += f"• Resistance: ${levels['nearest_resistance']:.2f} ({levels['resistance_distance']:.1%} above)\n\n"
        
        if decision['decision'] != "HOLD":
            output += "💰 TRADE PARAMETERS:\n"
            output += f"• Entry Price: ${decision['entry_price']:.2f}\n"
            output += f"• Stop Loss: ${decision['stop_loss']:.2f}\n"
            output += f"• Take Profit: ${decision['take_profit']:.2f}\n"
            output += f"• Risk/Reward: {decision['risk_assessment']['risk_reward_ratio']:.2f}:1\n"
            output += f"• Volatility: {decision['risk_assessment']['volatility']}\n\n"
        
        output += "🧠 REASONING:\n"
        for reason in decision['reasoning']:
            output += f"• {reason}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error in autonomous chart analysis: {str(e)}"

@tool("Multiple Chart Scanner")
def scan_multiple_charts_autonomously(symbols: str, period: str = "1y", signal_threshold: float = 0.7) -> str:
    """
    AUTONOMOUSLY scan multiple charts and identify the best trading opportunities.
    
    Parameters:
        symbols (str): Comma-separated stock symbols (e.g., 'AAPL,TSLA,NVDA')
        period (str): Time period for analysis
        signal_threshold (float): Minimum confidence threshold for signals
    
    Returns:
        str: Multi-chart analysis with ranked opportunities
    """
    try:
        # Handle None or empty symbols parameter
        if not symbols or not symbols.strip():
            symbols = "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI"  # Use default watchlist
        
        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            symbol_list = ["NIO", "SNDL", "IGC", "TLRY", "UGRO", "CGC", "EGO", "OGI"]

        results = []
        
        for symbol in symbol_list:
            decision = autonomous_analyzer.make_autonomous_trading_decision(symbol, period)
            if 'error' not in decision:
                results.append(decision)
        
        if not results:
            return "❌ No valid analysis results for any symbols"
        
        # Sort by confidence and decision strength
        buy_signals = [r for r in results if r['decision'] == 'BUY']
        sell_signals = [r for r in results if r['decision'] == 'SELL']
        hold_signals = [r for r in results if r['decision'] == 'HOLD']
        
        # Sort buy signals by confidence
        buy_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        output = f"🔍 AUTONOMOUS MULTI-STOCK SCAN RESULTS\n"
        output += "=" * 60 + "\n\n"
        
        if buy_signals:
            output += "🚀 TOP BUY OPPORTUNITIES:\n"
            for i, signal in enumerate(buy_signals[:5], 1):
                output += f"{i}. {signal['symbol']}: ${signal['current_price']:.2f} "
                output += f"({signal['confidence']:.1%} confidence)\n"
                output += f"   RSI: {signal['technical_indicators']['rsi']:.1f}, "
                output += f"Risk/Reward: {signal['risk_assessment']['risk_reward_ratio']:.2f}:1\n\n"
        
        if sell_signals:
            output += "📉 SELL SIGNALS:\n"
            for signal in sell_signals[:3]:
                output += f"• {signal['symbol']}: ${signal['current_price']:.2f} "
                output += f"({signal['confidence']:.1%} confidence)\n"
        
        if hold_signals:
            output += f"\n⏸️ HOLD POSITIONS: {len(hold_signals)} stocks\n"
        
        output += f"\n📊 SUMMARY:\n"
        output += f"• Buy Opportunities: {len(buy_signals)}\n"
        output += f"• Sell Signals: {len(sell_signals)}\n"
        output += f"• Hold Positions: {len(hold_signals)}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error in multi-stock scan: {str(e)}"

@tool("Pattern Recognition Scanner")
def scan_for_specific_patterns(symbols: str, patterns: str = "breakout,reversal,continuation", period: str = "1y") -> str:
    """
    Scan for specific chart patterns across multiple stocks.
    
    Parameters:
        symbols (str): Comma-separated stock symbols
        patterns (str): Comma-separated pattern types to look for
        period (str): Time period for analysis
    
    Returns:
        str: Pattern analysis results
    """
    try:
        # Handle None or empty symbols parameter
        if not symbols or not symbols.strip():
            symbols = "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI"  # Use default watchlist
        
        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            symbol_list = ["NIO", "SNDL", "IGC", "TLRY", "UGRO", "CGC", "EGO", "OGI"]

        pattern_results = []
        
        for symbol in symbol_list:
            data = autonomous_analyzer.get_stock_data(symbol, '6mo')
            if not data.empty:
                patterns = autonomous_analyzer.detect_chart_patterns(data)
                current_price = data['Close'].iloc[-1]
                
                for pattern in patterns:
                    if pattern_type == 'all' or pattern['pattern'].lower().replace(' ', '_') == pattern_type:
                        pattern_results.append({
                            'symbol': symbol,
                            'pattern': pattern,
                            'current_price': current_price
                        })
        
        if not pattern_results:
            return f"❌ No {pattern_type} patterns detected in the provided symbols"
        
        # Sort by pattern confidence
        pattern_results.sort(key=lambda x: x['pattern']['confidence'], reverse=True)
        
        output = f"🔍 PATTERN RECOGNITION SCAN RESULTS\n"
        output += "=" * 60 + "\n\n"
        
        for i, result in enumerate(pattern_results[:10], 1):
            output += f"{i}. {result['symbol']}: ${result['current_price']:.2f}\n"
            output += f"   Pattern: {result['pattern']['pattern']}\n"
            output += f"   Signal: {result['pattern']['signal']}\n"
            output += f"   Confidence: {result['pattern']['confidence']:.1%}\n"
            output += f"   Description: {result['pattern']['description']}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error in pattern recognition: {str(e)}" 