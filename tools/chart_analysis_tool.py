import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from crewai.tools import tool
import warnings
import logging

# Import our safe Yahoo Finance utilities
from utils.yfinance_utils import safe_yfinance_call, safe_yfinance_history, get_fallback_message, validate_ticker_symbol

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class ChartAnalyzer:
    """Advanced chart analysis with technical indicators and pattern recognition
    Enhanced with robust error handling and rate limiting for Yahoo Finance API
    """
    
    def __init__(self):
        self.timeframes = {
            '1d': '1d',
            '5d': '5d',
            '1mo': '1mo',
            '3mo': '3mo',
            '6mo': '6mo',
            '1y': '1y',
            '2y': '2y',
            '5y': '5y'
        }
    
    def get_stock_data(self, symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """Get stock data with enhanced error handling and fallback periods"""
        try:
            # Validate symbol first
            if not validate_ticker_symbol(symbol):
                logger.warning(f"Invalid ticker symbol: {symbol}")
                return None
            
            # Try different periods if the requested one fails
            periods_to_try = [period, '1y', '6mo', '3mo', '1mo']
            for p in periods_to_try:
                try:
                    logger.debug(f"Trying to fetch {p} data for {symbol}")
                    data = safe_yfinance_history(symbol, period=p, interval='1d')
                    
                    if data is not None and not data.empty and len(data) >= 20:  # Minimum data points
                        logger.info(f"Successfully fetched {len(data)} data points for {symbol} ({p})")
                        return data
                except Exception as e:
                    logger.warning(f"Failed to fetch {p} data for {symbol}: {str(e)}")
                    continue
            
            # Last resort - try with smaller periods
            for fallback_period in ['2w', '1w', '5d']:
                try:
                    data = safe_yfinance_history(symbol, period=fallback_period, interval='1d')
                    if data is not None and not data.empty:
                        logger.info(f"Fallback successful with {fallback_period} for {symbol}")
                        return data
                except:
                    continue
            
            logger.error(f"All attempts failed for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error getting stock data for {symbol}: {str(e)}")
            return None
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float, handling NaN and None"""
        if pd.isna(value) or value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index) with adaptive period"""
        data_len = len(data)
        
        # Use adaptive period based on available data
        if data_len >= period * 2:
            actual_period = period
        elif data_len >= 14:
            actual_period = 7
        elif data_len >= 10:
            actual_period = 5
        else:
            actual_period = max(2, data_len // 3)
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=actual_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=actual_period).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence) with adaptive periods"""
        data_len = len(data)
        
        # Use adaptive periods based on available data
        if data_len >= slow * 2:
            actual_fast = fast
            actual_slow = slow
            actual_signal = signal
        elif data_len >= 20:
            actual_fast = 6
            actual_slow = 13
            actual_signal = 5
        elif data_len >= 10:
            actual_fast = 3
            actual_slow = 7
            actual_signal = 3
        else:
            actual_fast = max(1, data_len // 4)
            actual_slow = max(2, data_len // 2)
            actual_signal = max(1, data_len // 6)
        
        exp1 = data['Close'].ewm(span=actual_fast).mean()
        exp2 = data['Close'].ewm(span=actual_slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=actual_signal).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands with adaptive period"""
        data_len = len(data)
        
        # Use adaptive period based on available data
        if data_len >= period:
            actual_period = period
        elif data_len >= 10:
            actual_period = 10
        elif data_len >= 5:
            actual_period = 5
        else:
            actual_period = max(2, data_len // 2)
        
        sma = data['Close'].rolling(window=actual_period).mean()
        std = data['Close'].rolling(window=actual_period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate multiple moving averages with adaptive periods"""
        averages = {}
        data_len = len(data)
        
        # Calculate moving averages with fallback to shorter periods if needed
        if data_len >= 20:
            averages['sma_20'] = data['Close'].rolling(window=20).mean()
        elif data_len >= 10:
            averages['sma_20'] = data['Close'].rolling(window=10).mean()
        else:
            averages['sma_20'] = data['Close'].rolling(window=max(1, data_len//2)).mean()
        
        if data_len >= 50:
            averages['sma_50'] = data['Close'].rolling(window=50).mean()
        elif data_len >= 25:
            averages['sma_50'] = data['Close'].rolling(window=25).mean()
        elif data_len >= 10:
            averages['sma_50'] = data['Close'].rolling(window=10).mean()
        else:
            averages['sma_50'] = data['Close'].rolling(window=max(1, data_len//2)).mean()
        
        if data_len >= 200:
            averages['sma_200'] = data['Close'].rolling(window=200).mean()
        elif data_len >= 100:
            averages['sma_200'] = data['Close'].rolling(window=100).mean()
        elif data_len >= 50:
            averages['sma_200'] = data['Close'].rolling(window=50).mean()
        elif data_len >= 20:
            averages['sma_200'] = data['Close'].rolling(window=20).mean()
        else:
            averages['sma_200'] = data['Close'].rolling(window=max(1, data_len//2)).mean()
        
        if data_len >= 12:
            averages['ema_12'] = data['Close'].ewm(span=12).mean()
        elif data_len >= 6:
            averages['ema_12'] = data['Close'].ewm(span=6).mean()
        else:
            averages['ema_12'] = data['Close'].ewm(span=max(1, data_len//2)).mean()
        
        if data_len >= 26:
            averages['ema_26'] = data['Close'].ewm(span=26).mean()
        elif data_len >= 13:
            averages['ema_26'] = data['Close'].ewm(span=13).mean()
        else:
            averages['ema_26'] = data['Close'].ewm(span=max(1, data_len//2)).mean()
        
        return averages
    
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator with adaptive period"""
        data_len = len(data)
        
        # Use adaptive period based on available data
        if data_len >= k_period:
            actual_k_period = k_period
        elif data_len >= 7:
            actual_k_period = 7
        elif data_len >= 5:
            actual_k_period = 5
        else:
            actual_k_period = max(2, data_len // 2)
        
        actual_d_period = min(d_period, max(1, actual_k_period // 2))
        
        low_min = data['Low'].rolling(window=actual_k_period).min()
        high_max = data['High'].rolling(window=actual_k_period).max()
        
        # Avoid division by zero
        denominator = high_max - low_min
        k_percent = 100 * ((data['Close'] - low_min) / denominator.replace(0, np.nan))
        d_percent = k_percent.rolling(window=actual_d_period).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    def find_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """Find support and resistance levels with adaptive window"""
        data_len = len(data)
        
        # Use adaptive window based on available data
        if data_len >= window * 2:
            actual_window = window
        elif data_len >= 20:
            actual_window = 10
        elif data_len >= 10:
            actual_window = 5
        else:
            actual_window = max(2, data_len // 4)
        
        if data_len < actual_window * 2:
            # Return recent high/low as basic support/resistance
            recent_high = data['High'].tail(min(10, data_len)).max()
            recent_low = data['Low'].tail(min(10, data_len)).min()
            return {
                'resistance': [recent_high] if not pd.isna(recent_high) else [],
                'support': [recent_low] if not pd.isna(recent_low) else []
            }
        
        highs = data['High'].rolling(window=actual_window, center=True).max()
        lows = data['Low'].rolling(window=actual_window, center=True).min()
        
        # Find local peaks and troughs
        resistance_levels = []
        support_levels = []
        
        for i in range(actual_window, len(data) - actual_window):
            if data['High'].iloc[i] == highs.iloc[i]:
                resistance_levels.append(data['High'].iloc[i])
            if data['Low'].iloc[i] == lows.iloc[i]:
                support_levels.append(data['Low'].iloc[i])
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        support_levels = sorted(list(set(support_levels)))
        
        return {
            'resistance': resistance_levels[:5],  # Top 5
            'support': support_levels[-5:]  # Bottom 5
        }
    
    def identify_trend(self, data: pd.DataFrame, period: int = 20) -> Dict[str, Any]:
        """Identify trend direction and strength"""
        if len(data) < period:
            return {'trend': 'unknown', 'strength': 0, 'slope': 0}
        
        # Calculate trend using linear regression
        close_prices = data['Close'].tail(period).values
        x = np.arange(len(close_prices))
        
        try:
            # Linear regression
            slope, intercept = np.polyfit(x, close_prices, 1)
            
            # Calculate R-squared for trend strength
            y_pred = slope * x + intercept
            ss_res = np.sum((close_prices - y_pred) ** 2)
            ss_tot = np.sum((close_prices - np.mean(close_prices)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determine trend direction
            if slope > 0.1:
                trend = 'uptrend'
            elif slope < -0.1:
                trend = 'downtrend'
            else:
                trend = 'sideways'
        except:
            trend = 'unknown'
            slope = 0
            r_squared = 0
        
        return {
            'trend': trend,
            'strength': r_squared,
            'slope': slope
        }
    
    def detect_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect chart patterns"""
        patterns = []
        
        if len(data) < 50:
            return patterns
        
        # Calculate moving averages for pattern detection
        ma_20 = data['Close'].rolling(window=20).mean()
        ma_50 = data['Close'].rolling(window=50).mean()
        
        # Golden Cross pattern
        if len(data) >= 2 and not ma_20.isna().all() and not ma_50.isna().all():
            if (not pd.isna(ma_20.iloc[-2]) and not pd.isna(ma_50.iloc[-2]) and 
                not pd.isna(ma_20.iloc[-1]) and not pd.isna(ma_50.iloc[-1])):
                if ma_20.iloc[-2] <= ma_50.iloc[-2] and ma_20.iloc[-1] > ma_50.iloc[-1]:
                    patterns.append({
                        'pattern': 'Golden Cross',
                        'type': 'bullish',
                        'description': '20-day MA crosses above 50-day MA',
                        'confidence': 0.8
                    })
        
        # Death Cross pattern
        if len(data) >= 2 and not ma_20.isna().all() and not ma_50.isna().all():
            if (not pd.isna(ma_20.iloc[-2]) and not pd.isna(ma_50.iloc[-2]) and 
                not pd.isna(ma_20.iloc[-1]) and not pd.isna(ma_50.iloc[-1])):
                if ma_20.iloc[-2] >= ma_50.iloc[-2] and ma_20.iloc[-1] < ma_50.iloc[-1]:
                    patterns.append({
                        'pattern': 'Death Cross',
                        'type': 'bearish',
                        'description': '20-day MA crosses below 50-day MA',
                        'confidence': 0.8
                    })
        
        # Breakout pattern (simple version)
        recent_high = data['High'].tail(20).max()
        recent_low = data['Low'].tail(20).min()
        current_price = data['Close'].iloc[-1]
        
        if current_price > recent_high * 1.02:
            patterns.append({
                'pattern': 'Breakout',
                'type': 'bullish',
                'description': 'Price breaks above recent resistance',
                'confidence': 0.7
            })
        elif current_price < recent_low * 0.98:
            patterns.append({
                'pattern': 'Breakdown',
                'type': 'bearish',
                'description': 'Price breaks below recent support',
                'confidence': 0.7
            })
        
        return patterns
    
    def analyze_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns"""
        if len(data) < 10:
            return {
                'volume_trend': 'unknown',
                'volume_ratio': 1.0,
                'volume_spike': False
            }
        
        # Calculate volume moving average
        volume_ma = data['Volume'].rolling(window=10).mean()
        current_volume = data['Volume'].iloc[-1]
        avg_volume = volume_ma.iloc[-1]
        
        # Volume trend
        recent_volume = data['Volume'].tail(5).mean()
        older_volume = data['Volume'].tail(10).head(5).mean()
        
        if recent_volume > older_volume * 1.1:
            volume_trend = 'increasing'
        elif recent_volume < older_volume * 0.9:
            volume_trend = 'decreasing'
        else:
            volume_trend = 'stable'
        
        # Volume ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volume spike
        volume_spike = volume_ratio > 1.5
        
        return {
            'volume_trend': volume_trend,
            'volume_ratio': volume_ratio,
            'volume_spike': volume_spike
        }
    
    def get_comprehensive_analysis(self, symbol: str, period: str = '1y') -> Dict[str, Any]:
        """Get comprehensive technical analysis"""
        data = self.get_stock_data(symbol, period)
        
        if data is None:
            return {'error': f'No data available for {symbol}'}
        
        # Calculate all indicators
        rsi = self.calculate_rsi(data)
        macd = self.calculate_macd(data)
        bollinger = self.calculate_bollinger_bands(data)
        moving_averages = self.calculate_moving_averages(data)
        stochastic = self.calculate_stochastic(data)
        support_resistance = self.find_support_resistance(data)
        trend = self.identify_trend(data)
        patterns = self.detect_patterns(data)
        volume_analysis = self.analyze_volume(data)
        
        # Get current values with safe handling
        current_price = self._safe_float(data['Close'].iloc[-1])
        current_rsi = self._safe_float(rsi.iloc[-1] if not rsi.empty else np.nan, 50.0)
        current_macd = self._safe_float(macd['macd'].iloc[-1] if not macd['macd'].empty else np.nan, 0.0)
        current_signal = self._safe_float(macd['signal'].iloc[-1] if not macd['signal'].empty else np.nan, 0.0)
        
        # Safe value extraction for other indicators
        bollinger_upper = self._safe_float(bollinger['upper'].iloc[-1] if not bollinger['upper'].empty else np.nan, current_price * 1.1)
        bollinger_middle = self._safe_float(bollinger['middle'].iloc[-1] if not bollinger['middle'].empty else np.nan, current_price)
        bollinger_lower = self._safe_float(bollinger['lower'].iloc[-1] if not bollinger['lower'].empty else np.nan, current_price * 0.9)
        
        sma_20 = self._safe_float(moving_averages['sma_20'].iloc[-1] if not moving_averages['sma_20'].empty else np.nan, current_price)
        sma_50 = self._safe_float(moving_averages['sma_50'].iloc[-1] if not moving_averages['sma_50'].empty else np.nan, current_price)
        sma_200 = self._safe_float(moving_averages['sma_200'].iloc[-1] if not moving_averages['sma_200'].empty else np.nan, current_price)
        
        stoch_k = self._safe_float(stochastic['k'].iloc[-1] if not stochastic['k'].empty else np.nan, 50.0)
        stoch_d = self._safe_float(stochastic['d'].iloc[-1] if not stochastic['d'].empty else np.nan, 50.0)
        
        # Analysis summary
        analysis = {
            'symbol': symbol,
            'current_price': current_price,
            'data_period': period,
            'data_points': len(data),
            'last_updated': datetime.now().isoformat(),
            
            # Technical indicators
            'rsi': {
                'value': current_rsi,
                'signal': self._interpret_rsi(current_rsi),
                'valid': not pd.isna(rsi.iloc[-1] if not rsi.empty else np.nan)
            },
            'macd': {
                'macd': current_macd,
                'signal': current_signal,
                'histogram': current_macd - current_signal,
                'interpretation': self._interpret_macd(current_macd, current_signal),
                'valid': not pd.isna(macd['macd'].iloc[-1] if not macd['macd'].empty else np.nan)
            },
            'bollinger_bands': {
                'upper': bollinger_upper,
                'middle': bollinger_middle,
                'lower': bollinger_lower,
                'position': self._interpret_bollinger_position(current_price, bollinger_upper, bollinger_lower),
                'valid': not pd.isna(bollinger['upper'].iloc[-1] if not bollinger['upper'].empty else np.nan)
            },
            'moving_averages': {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'price_vs_ma': self._interpret_ma_position(current_price, sma_20, sma_50, sma_200),
                'valid_20': not pd.isna(moving_averages['sma_20'].iloc[-1] if not moving_averages['sma_20'].empty else np.nan),
                'valid_50': not pd.isna(moving_averages['sma_50'].iloc[-1] if not moving_averages['sma_50'].empty else np.nan),
                'valid_200': not pd.isna(moving_averages['sma_200'].iloc[-1] if not moving_averages['sma_200'].empty else np.nan)
            },
            'stochastic': {
                'k': stoch_k,
                'd': stoch_d,
                'signal': self._interpret_stochastic(stoch_k, stoch_d),
                'valid': not pd.isna(stochastic['k'].iloc[-1] if not stochastic['k'].empty else np.nan)
            },
            
            # Chart patterns and levels
            'support_resistance': support_resistance,
            'trend_analysis': trend,
            'patterns': patterns,
            'volume_analysis': volume_analysis,
            
            # Overall signals
            'signals': self._generate_trading_signals(current_rsi, current_macd, current_signal, trend, patterns)
        }
        
        return analysis
    
    def _interpret_rsi(self, rsi_value: float) -> str:
        """Interpret RSI value"""
        if pd.isna(rsi_value):
            return 'neutral'
        if rsi_value > 70:
            return 'overbought'
        elif rsi_value < 30:
            return 'oversold'
        else:
            return 'neutral'
    
    def _interpret_macd(self, macd_value: float, signal_value: float) -> str:
        """Interpret MACD signals"""
        if pd.isna(macd_value) or pd.isna(signal_value):
            return 'neutral'
        if macd_value > signal_value:
            return 'bullish'
        elif macd_value < signal_value:
            return 'bearish'
        else:
            return 'neutral'
    
    def _interpret_bollinger_position(self, price: float, upper: float, lower: float) -> str:
        """Interpret price position relative to Bollinger Bands"""
        if pd.isna(upper) or pd.isna(lower):
            return 'within_bands'
        
        if price > upper:
            return 'above_upper_band'
        elif price < lower:
            return 'below_lower_band'
        else:
            return 'within_bands'
    
    def _interpret_ma_position(self, price: float, ma_20: float, ma_50: float, ma_200: float) -> Dict[str, str]:
        """Interpret price position relative to moving averages"""
        return {
            'vs_ma_20': 'above' if not pd.isna(ma_20) and price > ma_20 else 'below' if not pd.isna(ma_20) else 'unavailable',
            'vs_ma_50': 'above' if not pd.isna(ma_50) and price > ma_50 else 'below' if not pd.isna(ma_50) else 'unavailable',
            'vs_ma_200': 'above' if not pd.isna(ma_200) and price > ma_200 else 'below' if not pd.isna(ma_200) else 'unavailable'
        }
    
    def _interpret_stochastic(self, k_value: float, d_value: float) -> str:
        """Interpret Stochastic Oscillator"""
        if pd.isna(k_value):
            return 'neutral'
        if k_value > 80:
            return 'overbought'
        elif k_value < 20:
            return 'oversold'
        else:
            return 'neutral'
    
    def _generate_trading_signals(self, rsi: float, macd: float, signal: float, trend: Dict, patterns: List) -> Dict[str, Any]:
        """Generate overall trading signals"""
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI signals
        if not pd.isna(rsi):
            if rsi < 30:
                bullish_signals += 1
            elif rsi > 70:
                bearish_signals += 1
        
        # MACD signals
        if not pd.isna(macd) and not pd.isna(signal):
            if macd > signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        # Trend signals
        if trend['trend'] == 'uptrend':
            bullish_signals += 2
        elif trend['trend'] == 'downtrend':
            bearish_signals += 2
        
        # Pattern signals
        for pattern in patterns:
            if pattern['type'] == 'bullish':
                bullish_signals += 1
            elif pattern['type'] == 'bearish':
                bearish_signals += 1
        
        # Overall signal
        if bullish_signals > bearish_signals:
            overall_signal = 'bullish'
        elif bearish_signals > bullish_signals:
            overall_signal = 'bearish'
        else:
            overall_signal = 'neutral'
        
        signal_strength = abs(bullish_signals - bearish_signals) / (bullish_signals + bearish_signals) if (bullish_signals + bearish_signals) > 0 else 0
        
        return {
            'overall_signal': overall_signal,
            'signal_strength': signal_strength,
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals
        }

# Initialize the chart analyzer
chart_analyzer = ChartAnalyzer()

@tool("Technical Chart Analysis Tool")
def get_technical_analysis(symbol: str, period: str = '1y') -> str:
    """
    Get comprehensive technical analysis for a stock including indicators, patterns, and signals.
    
    Parameters:
        symbol (str): Stock ticker symbol (e.g., AAPL, TSLA, NIO)
        period (str): Time period for analysis (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
    
    Returns:
        str: Comprehensive technical analysis report
    """
    try:
        analysis = chart_analyzer.get_comprehensive_analysis(symbol, period)
        
        if 'error' in analysis:
            return f"❌ {analysis['error']}"
        
        # Format the analysis report
        report = []
        report.append(f"📊 TECHNICAL ANALYSIS FOR {symbol.upper()}")
        report.append("=" * 50)
        report.append(f"💰 Current Price: ${analysis['current_price']:.2f}")
        report.append(f"⏱️ Analysis Period: {period}")
        report.append(f"📊 Data Points: {analysis['data_points']}")
        report.append(f"📅 Last Updated: {analysis['last_updated'][:19]}")
        
        # Overall signals
        signals = analysis['signals']
        signal_emoji = "🟢" if signals['overall_signal'] == 'bullish' else "🔴" if signals['overall_signal'] == 'bearish' else "🟡"
        report.append(f"\n{signal_emoji} Overall Signal: {signals['overall_signal'].upper()}")
        report.append(f"📈 Signal Strength: {signals['signal_strength']:.1%}")
        report.append(f"   Bullish Signals: {signals['bullish_signals']}")
        report.append(f"   Bearish Signals: {signals['bearish_signals']}")
        
        # Technical indicators
        rsi = analysis['rsi']
        macd = analysis['macd']
        report.append(f"\n📈 TECHNICAL INDICATORS:")
        report.append(f"   RSI (14): {rsi['value']:.1f} ({rsi['signal']})")
        report.append(f"   MACD: {macd['macd']:.2f} vs Signal: {macd['signal']:.2f}")
        report.append(f"   MACD Signal: {macd['interpretation']}")
        
        # Moving averages
        ma = analysis['moving_averages']
        report.append(f"\n📊 MOVING AVERAGES:")
        report.append(f"   SMA 20: ${ma['sma_20']:.2f} ({ma['price_vs_ma']['vs_ma_20']})")
        report.append(f"   SMA 50: ${ma['sma_50']:.2f} ({ma['price_vs_ma']['vs_ma_50']})")
        report.append(f"   SMA 200: ${ma['sma_200']:.2f} ({ma['price_vs_ma']['vs_ma_200']})")
        
        if analysis['data_points'] < 200:
            report.append(f"   ⚠️ Note: Using adaptive periods due to limited data ({analysis['data_points']} points)")
        
        # Bollinger Bands
        bb = analysis['bollinger_bands']
        report.append(f"\n📏 BOLLINGER BANDS:")
        report.append(f"   Upper: ${bb['upper']:.2f}")
        report.append(f"   Middle: ${bb['middle']:.2f}")
        report.append(f"   Lower: ${bb['lower']:.2f}")
        report.append(f"   Position: {bb['position']}")
        
        # Stochastic
        stoch = analysis['stochastic']
        report.append(f"\n⚖️ STOCHASTIC:")
        report.append(f"   %K: {stoch['k']:.1f}")
        report.append(f"   %D: {stoch['d']:.1f}")
        report.append(f"   Signal: {stoch['signal']}")
        
        # Support and resistance
        sr = analysis['support_resistance']
        report.append(f"\n🏗️ SUPPORT & RESISTANCE:")
        if sr['resistance']:
            report.append(f"   Resistance: ${', '.join([f'{r:.2f}' for r in sr['resistance'][:3]])}")
        else:
            report.append(f"   Resistance: Current high ${analysis['current_price']:.2f}")
        if sr['support']:
            report.append(f"   Support: ${', '.join([f'{s:.2f}' for s in sr['support'][:3]])}")
        else:
            report.append(f"   Support: Current low ${analysis['current_price'] * 0.95:.2f}")
        
        # Trend analysis
        trend = analysis['trend_analysis']
        trend_emoji = "📈" if trend['trend'] == 'uptrend' else "📉" if trend['trend'] == 'downtrend' else "➡️"
        report.append(f"\n{trend_emoji} TREND ANALYSIS:")
        report.append(f"   Direction: {trend['trend']}")
        report.append(f"   Strength: {trend['strength']:.1%}")
        
        # Chart patterns
        patterns = analysis['patterns']
        if patterns:
            report.append(f"\n🔍 CHART PATTERNS:")
            for pattern in patterns:
                pattern_emoji = "🟢" if pattern['type'] == 'bullish' else "🔴"
                report.append(f"   {pattern_emoji} {pattern['pattern']}: {pattern['description']}")
                report.append(f"      Confidence: {pattern['confidence']:.1%}")
        else:
            report.append(f"\n🔍 CHART PATTERNS: None detected")
        
        # Volume analysis
        vol = analysis['volume_analysis']
        report.append(f"\n📊 VOLUME ANALYSIS:")
        report.append(f"   Volume Trend: {vol['volume_trend']}")
        report.append(f"   Volume Ratio: {vol['volume_ratio']:.2f}x")
        if vol['volume_spike']:
            report.append(f"   🔥 Volume Spike Detected!")
        
        # Trading recommendations
        report.append(f"\n💡 TRADING RECOMMENDATIONS:")
        if signals['overall_signal'] == 'bullish':
            report.append("   • Consider long positions or holding current positions")
            report.append("   • Watch for confirmation from volume and momentum")
            report.append("   • Set stop losses below key support levels")
        elif signals['overall_signal'] == 'bearish':
            report.append("   • Consider defensive strategies or profit-taking")
            report.append("   • Watch for potential reversal signals")
            report.append("   • Consider short positions with proper risk management")
        else:
            report.append("   • Mixed signals suggest cautious approach")
            report.append("   • Wait for clearer directional signals")
            report.append("   • Focus on risk management and position sizing")
        
        # Data quality note
        total_indicators = 5  # RSI, MACD, Bollinger, Stochastic, MA
        valid_indicators = sum([
            rsi['valid'],
            macd['valid'],
            bb['valid'],
            stoch['valid'],
            ma['valid_20']
        ])
        
        if valid_indicators < total_indicators:
            report.append(f"\n⚠️ DATA QUALITY NOTE:")
            report.append(f"   {valid_indicators}/{total_indicators} indicators have sufficient data")
            report.append(f"   Consider using a longer time period for more complete analysis")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ Error performing technical analysis for {symbol}: {str(e)}"

@tool("Quick Chart Signals")
def get_quick_chart_signals(symbol: str) -> str:
    """
    Get quick technical signals for fast trading decisions.
    
    Parameters:
        symbol (str): Stock ticker symbol (e.g., AAPL, TSLA, NIO)
    
    Returns:
        str: Quick technical signals summary
    """
    try:
        analysis = chart_analyzer.get_comprehensive_analysis(symbol, '3mo')
        
        if 'error' in analysis:
            return f"❌ {analysis['error']}"
        
        signals = analysis['signals']
        rsi = analysis['rsi']
        trend = analysis['trend_analysis']
        
        # Quick summary
        summary = []
        summary.append(f"⚡ QUICK SIGNALS: {symbol.upper()}")
        summary.append("=" * 30)
        
        # Overall signal with emoji
        signal_emoji = "🟢" if signals['overall_signal'] == 'bullish' else "🔴" if signals['overall_signal'] == 'bearish' else "🟡"
        summary.append(f"{signal_emoji} Signal: {signals['overall_signal'].upper()}")
        summary.append(f"💪 Strength: {signals['signal_strength']:.1%}")
        
        # Key metrics
        if rsi['valid']:
            summary.append(f"📊 RSI: {rsi['value']:.1f} ({rsi['signal']})")
        else:
            summary.append(f"📊 RSI: Insufficient data ({rsi['signal']})")
        
        summary.append(f"📈 Trend: {trend['trend']}")
        summary.append(f"💰 Price: ${analysis['current_price']:.2f}")
        summary.append(f"📊 Data Points: {analysis['data_points']}")
        
        # Quick action
        if signals['overall_signal'] == 'bullish':
            summary.append("✅ Action: BUY/HOLD")
        elif signals['overall_signal'] == 'bearish':
            summary.append("❌ Action: SELL/AVOID")
        else:
            summary.append("⏸️ Action: WAIT/WATCH")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error getting quick signals for {symbol}: {str(e)}" 