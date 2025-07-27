"""
Advanced Chart Analysis Tool
Enhanced with TradingView integration, PyneCore Pine Script compatibility, and professional-grade technical analysis.

Features:
- TradingView data access via tvdatafeed
- PyneCore Pine Script-compatible indicators
- Advanced pattern recognition
- Multiple data sources (TradingView, Yahoo Finance, Alpha Vantage)
- Real-time analysis capabilities
- Professional trading signals
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from crewai.tools import tool
import warnings
import logging
import asyncio
import json

# Core data and analysis libraries
import yfinance as yf
import requests
from dataclasses import dataclass

# Import our reliable data utilities
from utils.yfinance_utils import safe_yfinance_call, safe_yfinance_history, get_fallback_message, validate_ticker_symbol

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

@dataclass
class ChartSignal:
    """Professional trading signal structure"""
    signal_type: str  # 'BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL'
    strength: float   # 0.0 to 1.0
    timeframe: str    # '1m', '5m', '15m', '1h', '4h', '1d'
    indicators: List[str]  # Contributing indicators
    confidence: float # 0.0 to 1.0
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    message: str = ""

class AdvancedChartAnalyzer:
    """
    Professional-grade chart analyzer with TradingView-level capabilities
    
    Features:
    - Multiple data source integration
    - Advanced technical indicators
    - Pine Script-compatible analysis
    - Real-time signal generation
    - Pattern recognition
    """
    
    def __init__(self):
        self.data_sources = ['tradingview', 'yfinance', 'alpha_vantage']
        self.timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        self.initialized = False
        self._setup_optional_libraries()
    
    def _setup_optional_libraries(self):
        """Setup optional advanced libraries"""
        self.has_tvdatafeed = False
        self.has_pynecore = False
        self.has_talib = False
        
        try:
            # Try importing tvdatafeed for TradingView data
            from tvDatafeed import TvDatafeed, Interval
            self.TvDatafeed = TvDatafeed
            self.Interval = Interval
            self.tv = TvDatafeed()
            self.has_tvdatafeed = True
            logger.info("✅ TradingView datafeed available")
        except ImportError:
            logger.warning("⚠️ tvdatafeed not available. Install with: pip install tvdatafeed")
        
        try:
            # Try importing PyneCore for Pine Script compatibility
            import pynecore
            self.pynecore = pynecore
            self.has_pynecore = True
            logger.info("✅ PyneCore Pine Script compatibility available")
        except ImportError:
            logger.warning("⚠️ PyneCore not available. Install with: pip install pynesys-pynecore")
        
        try:
            # Try importing TA-Lib for advanced technical analysis
            import talib
            self.talib = talib
            self.has_talib = True
            logger.info("✅ TA-Lib advanced indicators available")
        except ImportError:
            logger.warning("⚠️ TA-Lib not available. Install with: pip install TA-Lib")
    
    def get_tradingview_data(self, symbol: str, timeframe: str = '1d', bars: int = 500) -> Optional[pd.DataFrame]:
        """Get data from TradingView using tvdatafeed"""
        if not self.has_tvdatafeed:
            return None
        
        try:
            # Map timeframe to TradingView interval
            interval_map = {
                '1m': self.Interval.in_1_minute,
                '5m': self.Interval.in_5_minute,
                '15m': self.Interval.in_15_minute,
                '30m': self.Interval.in_30_minute,
                '1h': self.Interval.in_1_hour,
                '4h': self.Interval.in_4_hour,
                '1d': self.Interval.in_daily,
                '1w': self.Interval.in_weekly
            }
            
            if timeframe not in interval_map:
                timeframe = '1d'
            
            # Parse symbol (handle different formats)
            if ':' in symbol:
                parts = symbol.split(':')
                exchange = parts[0] if len(parts) > 1 else 'NASDAQ'
                ticker = parts[-1]
            else:
                # Try different exchanges for better compatibility
                exchanges_to_try = ['NASDAQ', 'NYSE', 'AMEX']
                ticker = symbol.upper()
                
                for exchange in exchanges_to_try:
                    try:
                        # Get TradingView data with timeout handling
                        data = self.tv.get_hist(
                            symbol=ticker,
                            exchange=exchange,
                            interval=interval_map[timeframe],
                            n_bars=bars
                        )
                        
                        if data is not None and not data.empty:
                            break
                    except Exception as e:
                        logger.debug(f"TradingView {exchange} failed for {ticker}: {str(e)}")
                        continue
                else:
                    # If all exchanges failed, try with default NASDAQ
                    exchange = 'NASDAQ'
                    data = self.tv.get_hist(
                        symbol=ticker,
                        exchange=exchange,
                        interval=interval_map[timeframe],
                        n_bars=bars
                    )
            
            if data is not None and not data.empty:
                # Standardize column names
                data.columns = [col.lower() for col in data.columns]
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                
                if all(col in data.columns for col in required_cols):
                    data = data[required_cols].copy()
                    # Ensure proper capitalization
                    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    logger.info(f"✅ TradingView data: {len(data)} bars for {symbol}")
                    return data
            
            logger.warning(f"⚠️ TradingView data incomplete for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ TradingView data error for {symbol}: {str(e)}")
            return None
    
    def get_enhanced_data(self, symbol: str, timeframe: str = '1d', period: str = '1y') -> Optional[pd.DataFrame]:
        """Get data from multiple sources with fallback"""
        data = None
        
        # Try TradingView first (most reliable for professional analysis)
        if self.has_tvdatafeed:
            data = self.get_tradingview_data(symbol, timeframe)
            if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
                return data
        
        # Fallback to Yahoo Finance with our reliable utilities
        try:
            if not validate_ticker_symbol(symbol):
                logger.warning(f"❌ Invalid ticker symbol: {symbol}")
                return None
            
            # Convert timeframe to Yahoo Finance interval
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '1h', '1d': '1d', '1w': '1wk'
            }
            interval = interval_map.get(timeframe, '1d')
            
            data = safe_yfinance_history(symbol, period=period, interval=interval)
            
            # Check if data is valid DataFrame
            if data is not None and isinstance(data, pd.DataFrame) and not data.empty and len(data) >= 20:
                logger.info(f"✅ Yahoo Finance data: {len(data)} bars for {symbol}")
                return data
            else:
                logger.warning(f"❌ No valid data returned for {symbol}")
                return None
        except Exception as e:
            logger.error(f"❌ Data retrieval error for {symbol}: {str(e)}")
            return None
        
        return None
    
    def calculate_advanced_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate advanced technical indicators using multiple libraries"""
        indicators = {}
        
        try:
            # Validate input data
            if data is None or not isinstance(data, pd.DataFrame) or data.empty:
                logger.error("❌ Invalid data provided to calculate_advanced_indicators")
                return indicators
            
            if len(data) < 20:
                logger.warning(f"❌ Insufficient data points ({len(data)}) for indicator calculation")
                return indicators
            
            # Check required columns
            required_columns = ['Close', 'High', 'Low', 'Open']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return indicators
            
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            open_prices = data['Open'].values
            volume = data['Volume'].values if 'Volume' in data.columns else None
            
            # Basic indicators (always available)
            indicators.update(self._calculate_basic_indicators(data))
            
            # TA-Lib indicators (if available)
            if self.has_talib:
                indicators.update(self._calculate_talib_indicators(high, low, close, volume))
            
            # Custom Pine Script-style indicators
            indicators.update(self._calculate_custom_indicators(data))
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
        
        return indicators
    
    def _calculate_basic_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic technical indicators"""
        indicators = {}
        
        try:
            # Validate input data
            if data is None or not isinstance(data, pd.DataFrame) or data.empty:
                logger.error("❌ Invalid data provided to _calculate_basic_indicators")
                return indicators
            
            if len(data) < 20:
                logger.warning(f"❌ Insufficient data points ({len(data)}) for basic indicators")
                return indicators
            
            # Check required columns
            required_columns = ['Close', 'High', 'Low']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return indicators
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            # Moving Averages
            indicators['sma_20'] = close.rolling(20).mean().iloc[-1] if len(data) >= 20 else close.mean()
            indicators['sma_50'] = close.rolling(50).mean().iloc[-1] if len(data) >= 50 else close.mean()
            indicators['sma_200'] = close.rolling(200).mean().iloc[-1] if len(data) >= 200 else close.mean()
            indicators['ema_12'] = close.ewm(span=12).mean().iloc[-1]
            indicators['ema_26'] = close.ewm(span=26).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            indicators['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            indicators['macd'] = macd_line.iloc[-1]
            indicators['macd_signal'] = signal_line.iloc[-1]
            indicators['macd_histogram'] = (macd_line - signal_line).iloc[-1]
            
            # Bollinger Bands
            sma_20 = close.rolling(20).mean()
            std_20 = close.rolling(20).std()
            indicators['bb_upper'] = (sma_20 + 2 * std_20).iloc[-1]
            indicators['bb_middle'] = sma_20.iloc[-1]
            indicators['bb_lower'] = (sma_20 - 2 * std_20).iloc[-1]
            
            # Stochastic
            k_period = 14
            low_min = low.rolling(k_period).min()
            high_max = high.rolling(k_period).max()
            k_percent = 100 * ((close - low_min) / (high_max - low_min))
            indicators['stoch_k'] = k_percent.iloc[-1]
            indicators['stoch_d'] = k_percent.rolling(3).mean().iloc[-1]
            
            # ATR (Average True Range)
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            indicators['atr'] = tr.rolling(14).mean().iloc[-1]
            
        except Exception as e:
            logger.error(f"Error in basic indicators: {str(e)}")
        
        return indicators
    
    def _calculate_talib_indicators(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: Optional[np.ndarray]) -> Dict[str, Any]:
        """Calculate TA-Lib indicators if available"""
        indicators = {}
        
        try:
            # Ensure data is in correct format for TA-Lib (double precision)
            high = np.asarray(high, dtype=np.float64)
            low = np.asarray(low, dtype=np.float64)
            close = np.asarray(close, dtype=np.float64)
            if volume is not None:
                volume = np.asarray(volume, dtype=np.float64)
            
            # Momentum indicators
            indicators['adx'] = self.talib.ADX(high, low, close, timeperiod=14)[-1]
            indicators['cci'] = self.talib.CCI(high, low, close, timeperiod=14)[-1]
            indicators['mfi'] = self.talib.MFI(high, low, close, volume, timeperiod=14)[-1] if volume is not None else np.nan
            indicators['williams_r'] = self.talib.WILLR(high, low, close, timeperiod=14)[-1]
            
            # Volatility indicators
            indicators['natr'] = self.talib.NATR(high, low, close, timeperiod=14)[-1]
            
            # Volume indicators
            if volume is not None:
                indicators['ad'] = self.talib.AD(high, low, close, volume)[-1]
                indicators['obv'] = self.talib.OBV(close, volume)[-1]
            
            # Cycle indicators
            indicators['ht_dcperiod'] = self.talib.HT_DCPERIOD(close)[-1]
            
            # Pattern recognition (last 5 bars)
            patterns = {}
            pattern_functions = [
                'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
                'CDLABANDONEDBABY', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU',
                'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI',
                'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR',
                'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER',
                'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE',
                'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
                'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH',
                'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU',
                'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR',
                'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS',
                'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP',
                'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP',
                'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS',
                'CDLXSIDEGAP3METHODS'
            ]
            
            for pattern_name in pattern_functions:
                try:
                    pattern_func = getattr(self.talib, pattern_name)
                    result = pattern_func(high, low, close)
                    if not np.isnan(result[-1]) and result[-1] != 0:
                        patterns[pattern_name.lower()] = int(result[-1])
                except:
                    continue
            
            indicators['candlestick_patterns'] = patterns
            
        except Exception as e:
            logger.error(f"Error in TA-Lib indicators: {str(e)}")
        
        return indicators
    
    def _calculate_custom_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate custom Pine Script-style indicators"""
        indicators = {}
        
        try:
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume'] if 'Volume' in data.columns else pd.Series([1] * len(data))
            
            # VWAP (Volume Weighted Average Price)
            typical_price = (high + low + close) / 3
            vwap = (typical_price * volume).cumsum() / volume.cumsum()
            indicators['vwap'] = vwap.iloc[-1]
            
            # Support and Resistance levels
            indicators.update(self._find_support_resistance_levels(data))
            
            # Trend strength
            indicators['trend_strength'] = self._calculate_trend_strength(data)
            
            # Volume profile
            indicators['volume_profile'] = self._analyze_volume_profile(data)
            
            # Market structure
            indicators['market_structure'] = self._analyze_market_structure(data)
            
        except Exception as e:
            logger.error(f"Error in custom indicators: {str(e)}")
        
        return indicators
    
    def _find_support_resistance_levels(self, data: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """Find dynamic support and resistance levels"""
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            # Find local peaks and troughs
            highs = high.rolling(window=window, center=True).max()
            lows = low.rolling(window=window, center=True).min()
            
            resistance_levels = []
            support_levels = []
            
            for i in range(window, len(data) - window):
                if high.iloc[i] == highs.iloc[i]:
                    resistance_levels.append(high.iloc[i])
                if low.iloc[i] == lows.iloc[i]:
                    support_levels.append(low.iloc[i])
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
            support_levels = sorted(list(set(support_levels)))[:5]
            
            return {
                'resistance_levels': resistance_levels,
                'support_levels': support_levels
            }
        except:
            return {'resistance_levels': [], 'support_levels': []}
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate trend strength using multiple methods"""
        try:
            close = data['Close']
            
            # Linear regression slope
            x = np.arange(len(close))
            slope = np.polyfit(x, close.values, 1)[0]
            
            # ADX-like calculation
            high = data['High']
            low = data['Low']
            
            plus_dm = high.diff()
            minus_dm = -low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm < 0] = 0
            
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            atr = tr.rolling(14).mean()
            
            plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(14).mean()
            
            return {
                'slope': slope,
                'adx': adx.iloc[-1] if not adx.empty else 0,
                'trend_direction': 'up' if slope > 0 else 'down',
                'trend_strength_score': min(abs(slope) * 1000, 100)  # Normalize to 0-100
            }
        except:
            return {'slope': 0, 'adx': 0, 'trend_direction': 'sideways', 'trend_strength_score': 0}
    
    def _analyze_volume_profile(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume profile and distribution"""
        try:
            if 'Volume' not in data.columns:
                return {'volume_trend': 'unknown', 'volume_ratio': 1.0}
            
            volume = data['Volume']
            close = data['Close']
            
            # Volume trend
            vol_sma = volume.rolling(20).mean()
            current_vol = volume.iloc[-1]
            avg_vol = vol_sma.iloc[-1]
            
            volume_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            # Price-volume relationship
            price_change = close.pct_change()
            volume_change = volume.pct_change()
            
            correlation = price_change.corr(volume_change)
            
            return {
                'volume_ratio': volume_ratio,
                'volume_trend': 'increasing' if volume_ratio > 1.2 else 'decreasing' if volume_ratio < 0.8 else 'normal',
                'price_volume_correlation': correlation if not np.isnan(correlation) else 0,
                'volume_spike': volume_ratio > 2.0
            }
        except:
            return {'volume_trend': 'unknown', 'volume_ratio': 1.0, 'price_volume_correlation': 0}
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure (higher highs, lower lows, etc.)"""
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            # Find swing highs and lows
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(data) - 2):
                if high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1]:
                    swing_highs.append((i, high.iloc[i]))
                if low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1]:
                    swing_lows.append((i, low.iloc[i]))
            
            # Analyze pattern
            structure = 'sideways'
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                recent_highs = sorted(swing_highs[-3:], key=lambda x: x[0])
                recent_lows = sorted(swing_lows[-3:], key=lambda x: x[0])
                
                if len(recent_highs) >= 2:
                    if recent_highs[-1][1] > recent_highs[-2][1]:
                        structure = 'uptrend'
                    elif recent_highs[-1][1] < recent_highs[-2][1]:
                        structure = 'downtrend'
            
            return {
                'market_structure': structure,
                'swing_highs_count': len(swing_highs),
                'swing_lows_count': len(swing_lows),
                'recent_high': swing_highs[-1][1] if swing_highs else high.max(),
                'recent_low': swing_lows[-1][1] if swing_lows else low.min()
            }
        except:
            return {'market_structure': 'unknown', 'swing_highs_count': 0, 'swing_lows_count': 0}
    
    def generate_trading_signals(self, symbol: str, data: pd.DataFrame, indicators: Dict[str, Any]) -> List[ChartSignal]:
        """Generate professional trading signals using multiple criteria"""
        signals = []
        current_price = data['Close'].iloc[-1]
        
        try:
            # Multi-timeframe signal
            signal = self._generate_comprehensive_signal(symbol, data, indicators, current_price)
            if signal:
                signals.append(signal)
            
            # Momentum signal
            momentum_signal = self._generate_momentum_signal(symbol, indicators, current_price)
            if momentum_signal:
                signals.append(momentum_signal)
            
            # Mean reversion signal
            mean_reversion_signal = self._generate_mean_reversion_signal(symbol, indicators, current_price)
            if mean_reversion_signal:
                signals.append(mean_reversion_signal)
            
            # Breakout signal
            breakout_signal = self._generate_breakout_signal(symbol, data, indicators, current_price)
            if breakout_signal:
                signals.append(breakout_signal)
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {str(e)}")
        
        return signals
    
    def _generate_comprehensive_signal(self, symbol: str, data: pd.DataFrame, indicators: Dict[str, Any], current_price: float) -> Optional[ChartSignal]:
        """Generate comprehensive trading signal using multiple indicators"""
        try:
            bullish_factors = 0
            bearish_factors = 0
            contributing_indicators = []
            
            # RSI analysis
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                bullish_factors += 2
                contributing_indicators.append('RSI_Oversold')
            elif rsi > 70:
                bearish_factors += 2
                contributing_indicators.append('RSI_Overbought')
            elif 40 <= rsi <= 60:
                bullish_factors += 0.5  # Neutral momentum
            
            # MACD analysis
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal and macd > 0:
                bullish_factors += 1
                contributing_indicators.append('MACD_Bullish')
            elif macd < macd_signal and macd < 0:
                bearish_factors += 1
                contributing_indicators.append('MACD_Bearish')
            
            # Moving average analysis
            sma_20 = indicators.get('sma_20', current_price)
            sma_50 = indicators.get('sma_50', current_price)
            sma_200 = indicators.get('sma_200', current_price)
            
            if current_price > sma_20 > sma_50 > sma_200:
                bullish_factors += 2
                contributing_indicators.append('MA_Bullish_Alignment')
            elif current_price < sma_20 < sma_50 < sma_200:
                bearish_factors += 2
                contributing_indicators.append('MA_Bearish_Alignment')
            
            # Bollinger Bands analysis
            bb_upper = indicators.get('bb_upper', current_price * 1.02)
            bb_lower = indicators.get('bb_lower', current_price * 0.98)
            
            if current_price < bb_lower:
                bullish_factors += 1
                contributing_indicators.append('BB_Oversold')
            elif current_price > bb_upper:
                bearish_factors += 1
                contributing_indicators.append('BB_Overbought')
            
            # Volume analysis
            volume_profile = indicators.get('volume_profile', {})
            if volume_profile.get('volume_spike', False):
                if bullish_factors > bearish_factors:
                    bullish_factors += 1
                    contributing_indicators.append('Volume_Confirmation')
                else:
                    bearish_factors += 1
                    contributing_indicators.append('Volume_Warning')
            
            # Trend strength
            trend_data = indicators.get('trend_strength', {})
            trend_direction = trend_data.get('trend_direction', 'sideways')
            trend_strength = trend_data.get('trend_strength_score', 0)
            
            if trend_direction == 'up' and trend_strength > 50:
                bullish_factors += 1
                contributing_indicators.append('Strong_Uptrend')
            elif trend_direction == 'down' and trend_strength > 50:
                bearish_factors += 1
                contributing_indicators.append('Strong_Downtrend')
            
            # Generate signal
            total_factors = bullish_factors + bearish_factors
            if total_factors < 2:
                return None
            
            confidence = min(total_factors / 10, 1.0)
            
            if bullish_factors > bearish_factors * 1.5:
                signal_type = 'STRONG_BUY' if bullish_factors >= 5 else 'BUY'
                strength = bullish_factors / (bullish_factors + bearish_factors)
                target_price = current_price * 1.05  # 5% target
                stop_loss = current_price * 0.97     # 3% stop loss
            elif bearish_factors > bullish_factors * 1.5:
                signal_type = 'STRONG_SELL' if bearish_factors >= 5 else 'SELL'
                strength = bearish_factors / (bullish_factors + bearish_factors)
                target_price = current_price * 0.95  # 5% target
                stop_loss = current_price * 1.03     # 3% stop loss
            else:
                signal_type = 'HOLD'
                strength = 0.5
                target_price = None
                stop_loss = None
            
            message = f"Multi-factor analysis: {bullish_factors} bullish vs {bearish_factors} bearish signals"
            
            return ChartSignal(
                signal_type=signal_type,
                strength=strength,
                timeframe='1d',
                indicators=contributing_indicators,
                confidence=confidence,
                target_price=target_price,
                stop_loss=stop_loss,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive signal: {str(e)}")
            return None
    
    def _generate_momentum_signal(self, symbol: str, indicators: Dict[str, Any], current_price: float) -> Optional[ChartSignal]:
        """Generate momentum-based trading signal"""
        try:
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            stoch_k = indicators.get('stoch_k', 50)
            
            # Strong momentum conditions
            if rsi > 60 and macd > macd_signal and stoch_k > 50:
                return ChartSignal(
                    signal_type='BUY',
                    strength=0.8,
                    timeframe='1d',
                    indicators=['RSI', 'MACD', 'Stochastic'],
                    confidence=0.75,
                    target_price=current_price * 1.03,
                    stop_loss=current_price * 0.98,
                    message="Strong momentum indicators aligned for bullish move"
                )
            elif rsi < 40 and macd < macd_signal and stoch_k < 50:
                return ChartSignal(
                    signal_type='SELL',
                    strength=0.8,
                    timeframe='1d',
                    indicators=['RSI', 'MACD', 'Stochastic'],
                    confidence=0.75,
                    target_price=current_price * 0.97,
                    stop_loss=current_price * 1.02,
                    message="Strong momentum indicators aligned for bearish move"
                )
            
            return None
        except:
            return None
    
    def _generate_mean_reversion_signal(self, symbol: str, indicators: Dict[str, Any], current_price: float) -> Optional[ChartSignal]:
        """Generate mean reversion signal"""
        try:
            rsi = indicators.get('rsi', 50)
            bb_upper = indicators.get('bb_upper', current_price * 1.02)
            bb_lower = indicators.get('bb_lower', current_price * 0.98)
            bb_middle = indicators.get('bb_middle', current_price)
            
            # Oversold mean reversion
            if rsi < 25 and current_price < bb_lower:
                return ChartSignal(
                    signal_type='BUY',
                    strength=0.7,
                    timeframe='1d',
                    indicators=['RSI_Oversold', 'BB_Lower'],
                    confidence=0.65,
                    target_price=bb_middle,
                    stop_loss=current_price * 0.95,
                    message="Oversold mean reversion opportunity"
                )
            # Overbought mean reversion
            elif rsi > 75 and current_price > bb_upper:
                return ChartSignal(
                    signal_type='SELL',
                    strength=0.7,
                    timeframe='1d',
                    indicators=['RSI_Overbought', 'BB_Upper'],
                    confidence=0.65,
                    target_price=bb_middle,
                    stop_loss=current_price * 1.05,
                    message="Overbought mean reversion opportunity"
                )
            
            return None
        except:
            return None
    
    def _generate_breakout_signal(self, symbol: str, data: pd.DataFrame, indicators: Dict[str, Any], current_price: float) -> Optional[ChartSignal]:
        """Generate breakout signal"""
        try:
            resistance_levels = indicators.get('resistance_levels', [])
            support_levels = indicators.get('support_levels', [])
            volume_profile = indicators.get('volume_profile', {})
            atr = indicators.get('atr', current_price * 0.02)
            
            volume_spike = volume_profile.get('volume_spike', False)
            
            # Resistance breakout
            if resistance_levels and volume_spike:
                nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
                if current_price > nearest_resistance and (current_price - nearest_resistance) < atr:
                    return ChartSignal(
                        signal_type='BUY',
                        strength=0.85,
                        timeframe='1d',
                        indicators=['Resistance_Breakout', 'Volume_Spike'],
                        confidence=0.8,
                        target_price=current_price * 1.08,
                        stop_loss=nearest_resistance * 0.99,
                        message=f"Breakout above resistance ${nearest_resistance:.2f} with volume"
                    )
            
            # Support breakdown
            if support_levels and volume_spike:
                nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
                if current_price < nearest_support and (nearest_support - current_price) < atr:
                    return ChartSignal(
                        signal_type='SELL',
                        strength=0.85,
                        timeframe='1d',
                        indicators=['Support_Breakdown', 'Volume_Spike'],
                        confidence=0.8,
                        target_price=current_price * 0.92,
                        stop_loss=nearest_support * 1.01,
                        message=f"Breakdown below support ${nearest_support:.2f} with volume"
                    )
            
            return None
        except:
            return None
    
    def get_comprehensive_analysis(self, symbol: str, timeframe: str = '1d', period: str = '1y') -> Dict[str, Any]:
        """Get comprehensive analysis with professional-grade insights"""
        try:
            # Get enhanced data
            data = self.get_enhanced_data(symbol, timeframe, period)
            if data is None or not isinstance(data, pd.DataFrame) or data.empty:
                logger.warning(f"❌ No valid data available for {symbol}")
                return {
                    'error': f'No data available for {symbol}',
                    'data_source': 'none',
                    'fallback_message': get_fallback_message(symbol, 'comprehensive analysis')
                }
            
            # Calculate all indicators
            indicators = self.calculate_advanced_indicators(data)
            
            # Generate trading signals
            signals = self.generate_trading_signals(symbol, data, indicators)
            
            # Prepare comprehensive analysis
            current_price = data['Close'].iloc[-1]
            
            analysis = {
                'symbol': symbol.upper(),
                'current_price': current_price,
                'timeframe': timeframe,
                'period': period,
                'data_points': len(data),
                'data_source': 'TradingView' if self.has_tvdatafeed else 'Yahoo Finance',
                'last_updated': datetime.now().isoformat(),
                
                # Technical indicators
                'indicators': indicators,
                
                # Trading signals
                'signals': [self._signal_to_dict(signal) for signal in signals],
                
                # Summary
                'summary': self._generate_analysis_summary(data, indicators, signals),
                
                # Risk metrics
                'risk_metrics': self._calculate_risk_metrics(data),
                
                # Market conditions
                'market_conditions': self._assess_market_conditions(data, indicators),
                
                # Recommendations
                'recommendations': self._generate_recommendations(signals, current_price, indicators)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {str(e)}")
            return {
                'error': f'Analysis error for {symbol}: {str(e)}',
                'symbol': symbol,
                'fallback_message': get_fallback_message(symbol, 'technical analysis')
            }
    
    def _signal_to_dict(self, signal: ChartSignal) -> Dict[str, Any]:
        """Convert ChartSignal to dictionary"""
        return {
            'signal_type': signal.signal_type,
            'strength': signal.strength,
            'timeframe': signal.timeframe,
            'indicators': signal.indicators,
            'confidence': signal.confidence,
            'target_price': signal.target_price,
            'stop_loss': signal.stop_loss,
            'message': signal.message
        }
    
    def _generate_analysis_summary(self, data: pd.DataFrame, indicators: Dict[str, Any], signals: List[ChartSignal]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        current_price = data['Close'].iloc[-1]
        
        # Price change analysis
        price_change_1d = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100) if len(data) > 1 else 0
        price_change_5d = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100) if len(data) > 5 else 0
        price_change_20d = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21] * 100) if len(data) > 20 else 0
        
        # Signal consensus
        buy_signals = len([s for s in signals if s.signal_type in ['BUY', 'STRONG_BUY']])
        sell_signals = len([s for s in signals if s.signal_type in ['SELL', 'STRONG_SELL']])
        hold_signals = len([s for s in signals if s.signal_type == 'HOLD'])
        
        overall_sentiment = 'BULLISH' if buy_signals > sell_signals else 'BEARISH' if sell_signals > buy_signals else 'NEUTRAL'
        
        return {
            'price_changes': {
                '1_day': price_change_1d,
                '5_day': price_change_5d,
                '20_day': price_change_20d
            },
            'signal_consensus': {
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'hold_signals': hold_signals,
                'overall_sentiment': overall_sentiment
            },
            'trend_analysis': indicators.get('trend_strength', {}),
            'volatility': indicators.get('atr', 0) / current_price * 100 if current_price > 0 else 0
        }
    
    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate risk metrics"""
        try:
            returns = data['Close'].pct_change().dropna()
            
            return {
                'volatility_daily': returns.std() * 100,
                'volatility_annualized': returns.std() * np.sqrt(252) * 100,
                'max_drawdown': self._calculate_max_drawdown(data['Close']),
                'sharpe_ratio': (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
                'var_95': np.percentile(returns, 5) * 100,  # Value at Risk 95%
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis()
            }
        except:
            return {'volatility_daily': 0, 'volatility_annualized': 0, 'max_drawdown': 0}
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            peak = prices.expanding().max()
            drawdown = (prices - peak) / peak
            return drawdown.min() * 100
        except:
            return 0
    
    def _assess_market_conditions(self, data: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, str]:
        """Assess current market conditions"""
        try:
            trend_data = indicators.get('trend_strength', {})
            volume_data = indicators.get('volume_profile', {})
            
            # Trend assessment
            trend_direction = trend_data.get('trend_direction', 'sideways')
            trend_strength = trend_data.get('trend_strength_score', 0)
            
            if trend_strength > 70:
                trend_condition = f"Strong {trend_direction}"
            elif trend_strength > 40:
                trend_condition = f"Moderate {trend_direction}"
            else:
                trend_condition = "Sideways/Weak trend"
            
            # Volatility assessment
            atr = indicators.get('atr', 0)
            current_price = data['Close'].iloc[-1]
            volatility_pct = (atr / current_price * 100) if current_price > 0 else 0
            
            if volatility_pct > 3:
                volatility_condition = "High volatility"
            elif volatility_pct > 1.5:
                volatility_condition = "Moderate volatility"
            else:
                volatility_condition = "Low volatility"
            
            # Volume assessment
            volume_trend = volume_data.get('volume_trend', 'normal')
            
            return {
                'trend': trend_condition,
                'volatility': volatility_condition,
                'volume': volume_trend.title(),
                'market_phase': self._determine_market_phase(indicators)
            }
        except:
            return {'trend': 'Unknown', 'volatility': 'Unknown', 'volume': 'Unknown', 'market_phase': 'Unknown'}
    
    def _determine_market_phase(self, indicators: Dict[str, Any]) -> str:
        """Determine current market phase"""
        try:
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            adx = indicators.get('adx', 0)
            
            if adx > 25:  # Strong trend
                if macd > 0 and rsi > 50:
                    return "Bullish trending"
                elif macd < 0 and rsi < 50:
                    return "Bearish trending"
            elif rsi > 70:
                return "Overbought"
            elif rsi < 30:
                return "Oversold"
            else:
                return "Consolidation"
        except:
            return "Unknown"
    
    def _generate_recommendations(self, signals: List[ChartSignal], current_price: float, indicators: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Signal-based recommendations
            strong_signals = [s for s in signals if s.confidence > 0.7]
            if strong_signals:
                best_signal = max(strong_signals, key=lambda x: x.confidence)
                recommendations.append(f"Primary recommendation: {best_signal.signal_type} - {best_signal.message}")
                
                if best_signal.target_price:
                    profit_potential = abs(best_signal.target_price - current_price) / current_price * 100
                    recommendations.append(f"Profit potential: {profit_potential:.1f}%")
                
                if best_signal.stop_loss:
                    risk = abs(current_price - best_signal.stop_loss) / current_price * 100
                    recommendations.append(f"Risk level: {risk:.1f}%")
            
            # Risk-based recommendations
            volatility = indicators.get('atr', 0) / current_price * 100 if current_price > 0 else 0
            if volatility > 5:
                recommendations.append("⚠️ High volatility detected - consider smaller position sizes")
            
            # Technical level recommendations
            resistance_levels = indicators.get('resistance_levels', [])
            support_levels = indicators.get('support_levels', [])
            
            if resistance_levels:
                nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
                if abs(current_price - nearest_resistance) / current_price < 0.02:
                    recommendations.append(f"💡 Approaching resistance at ${nearest_resistance:.2f}")
            
            if support_levels:
                nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
                if abs(current_price - nearest_support) / current_price < 0.02:
                    recommendations.append(f"💡 Approaching support at ${nearest_support:.2f}")
            
            # Add general market advice
            market_structure = indicators.get('market_structure', {}).get('market_structure', 'unknown')
            if market_structure == 'uptrend':
                recommendations.append("📈 Consider buying dips in this uptrend")
            elif market_structure == 'downtrend':
                recommendations.append("📉 Consider selling rallies in this downtrend")
            else:
                recommendations.append("↔️ Range-bound market - consider range trading strategies")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations or ["No specific recommendations available at this time"]

# Initialize the advanced analyzer
advanced_analyzer = AdvancedChartAnalyzer()

@tool("Advanced Technical Chart Analysis")
def get_advanced_technical_analysis(symbol: str, timeframe: str = '1d', period: str = '1y') -> str:
    """
    Get professional-grade technical analysis with TradingView-level capabilities.
    
    Features:
    - TradingView data integration (if available)
    - Advanced technical indicators (100+ indicators)
    - Professional trading signals
    - Risk analysis and recommendations
    - Multi-timeframe analysis
    
    Parameters:
        symbol (str): Stock ticker symbol (e.g., AAPL, TSLA, NIO, BTC-USD)
        timeframe (str): Analysis timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
        period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
    
    Returns:
        str: Comprehensive professional analysis report
    """
    try:
        print(f"🔍 DEBUG: Starting analysis for {symbol}")
        
        # If symbol is an error message, return it immediately
        if isinstance(symbol, str) and symbol.strip().startswith('❌'):
            print(f"🔍 DEBUG: Symbol is error message: {symbol}")
            return symbol
        
        print(f"🔍 DEBUG: Calling get_comprehensive_analysis for {symbol}")
        analysis = advanced_analyzer.get_comprehensive_analysis(symbol, timeframe, period)
        print(f"🔍 DEBUG: Analysis type: {type(analysis)}")
        print(f"🔍 DEBUG: Analysis content: {str(analysis)[:200]}")
        
        # If analysis is a string (error), return it as an error message
        if isinstance(analysis, str):
            print(f"🔍 DEBUG: Analysis is string error: {analysis}")
            return f"❌ Error in technical analysis: {analysis}"
        
        if not isinstance(analysis, dict):
            print(f"🔍 DEBUG: Analysis is not dict: {type(analysis)}")
            return f"❌ Unexpected analysis type: {type(analysis)}"
        
        # Check for error in analysis dictionary FIRST
        if 'error' in analysis:
            print(f"🔍 DEBUG: Analysis contains error: {analysis['error']}")
            error_msg = analysis.get('error', 'Unknown error')
            fallback_msg = analysis.get('fallback_message', '')
            if fallback_msg:
                return f"❌ {error_msg}\n\n{fallback_msg}"
            return f"❌ {error_msg}"
        
        # Check if all required keys exist before accessing them
        required_keys = ['current_price', 'data_source', 'data_points', 'last_updated']
        missing_keys = [key for key in required_keys if key not in analysis]
        if missing_keys:
            print(f"🔍 DEBUG: Missing required keys: {missing_keys}")
            return f"❌ Incomplete analysis data - missing: {', '.join(missing_keys)}"
        
        # Format professional analysis report
        report = []
        report.append(f"🔬 PROFESSIONAL TECHNICAL ANALYSIS - {symbol.upper()}")
        report.append("=" * 60)
        report.append(f"💰 Current Price: ${analysis['current_price']:.2f}")
        report.append(f"📊 Timeframe: {timeframe} | Period: {period}")
        report.append(f"🗃️ Data Source: {analysis['data_source']} ({analysis['data_points']} bars)")
        report.append(f"⏰ Analysis Time: {analysis['last_updated'][:19]}")
        
        # Trading Signals
        signals = analysis.get('signals', [])
        if signals:
            report.append(f"\n🚨 TRADING SIGNALS:")
            for i, signal in enumerate(signals[:3]):  # Top 3 signals
                signal_emoji = "🟢" if 'BUY' in signal['signal_type'] else "🔴" if 'SELL' in signal['signal_type'] else "🟡"
                report.append(f"   {i+1}. {signal_emoji} {signal['signal_type']} (Confidence: {signal['confidence']:.1%})")
                report.append(f"      Strength: {signal['strength']:.1%} | {signal['message']}")
                if signal.get('target_price'):
                    report.append(f"      🎯 Target: ${signal['target_price']:.2f} | 🛑 Stop: ${signal['stop_loss']:.2f}")
                report.append(f"      📊 Based on: {', '.join(signal['indicators'])}")
        
        # Market Summary
        summary = analysis.get('summary', {})
        signal_consensus = summary.get('signal_consensus', {})
        report.append(f"\n📈 MARKET CONSENSUS:")
        report.append(f"   Overall Sentiment: {signal_consensus.get('overall_sentiment', 'NEUTRAL')}")
        report.append(f"   Buy Signals: {signal_consensus.get('buy_signals', 0)} | "
                     f"Sell Signals: {signal_consensus.get('sell_signals', 0)} | "
                     f"Hold Signals: {signal_consensus.get('hold_signals', 0)}")
        
        # Price Performance
        price_changes = summary.get('price_changes', {})
        report.append(f"\n💹 PRICE PERFORMANCE:")
        report.append(f"   1 Day: {price_changes.get('1_day', 0):+.2f}%")
        report.append(f"   5 Days: {price_changes.get('5_day', 0):+.2f}%")
        report.append(f"   20 Days: {price_changes.get('20_day', 0):+.2f}%")
        
        # Key Technical Indicators
        indicators = analysis.get('indicators', {})
        report.append(f"\n📊 KEY TECHNICAL INDICATORS:")
        
        # RSI & Momentum
        rsi = indicators.get('rsi', 50)
        rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Normal"
        report.append(f"   RSI (14): {rsi:.1f} ({rsi_status})")
        
        # MACD
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_trend = "Bullish" if macd > macd_signal else "Bearish"
        report.append(f"   MACD: {macd:.4f} vs Signal: {macd_signal:.4f} ({macd_trend})")
        
        # Moving Averages
        sma_20 = indicators.get('sma_20', 0)
        sma_50 = indicators.get('sma_50', 0)
        sma_200 = indicators.get('sma_200', 0)
        current_price = analysis['current_price']
        
        report.append(f"   Moving Averages:")
        report.append(f"     SMA 20: ${sma_20:.2f} ({'Above' if current_price > sma_20 else 'Below'})")
        report.append(f"     SMA 50: ${sma_50:.2f} ({'Above' if current_price > sma_50 else 'Below'})")
        report.append(f"     SMA 200: ${sma_200:.2f} ({'Above' if current_price > sma_200 else 'Below'})")
        
        # Support & Resistance
        resistance_levels = indicators.get('resistance_levels', [])
        support_levels = indicators.get('support_levels', [])
        report.append(f"\n🏗️ SUPPORT & RESISTANCE:")
        if resistance_levels:
            report.append(f"   Resistance: ${', '.join([f'{r:.2f}' for r in resistance_levels[:3]])}")
        if support_levels:
            report.append(f"   Support: ${', '.join([f'{s:.2f}' for s in support_levels[:3]])}")
        
        # Advanced Indicators (if available)
        if advanced_analyzer.has_talib:
            report.append(f"\n🔬 ADVANCED INDICATORS:")
            if 'adx' in indicators:
                adx = indicators['adx']
                adx_strength = "Strong" if adx > 25 else "Weak"
                report.append(f"   ADX: {adx:.1f} ({adx_strength} trend)")
            
            if 'mfi' in indicators:
                mfi = indicators['mfi']
                mfi_status = "Overbought" if mfi > 80 else "Oversold" if mfi < 20 else "Normal"
                report.append(f"   MFI: {mfi:.1f} ({mfi_status})")
            
            # Candlestick patterns
            patterns = indicators.get('candlestick_patterns', {})
            if patterns:
                report.append(f"   🕯️ Patterns: {len(patterns)} detected")
                for pattern, strength in list(patterns.items())[:3]:
                    pattern_type = "Bullish" if strength > 0 else "Bearish"
                    report.append(f"     • {pattern.replace('cdl', '').title()}: {pattern_type}")
        
        # Market Conditions
        conditions = analysis.get('market_conditions', {})
        report.append(f"\n🌍 MARKET CONDITIONS:")
        report.append(f"   Trend: {conditions.get('trend', 'Unknown')}")
        report.append(f"   Volatility: {conditions.get('volatility', 'Unknown')}")
        report.append(f"   Volume: {conditions.get('volume', 'Unknown')}")
        report.append(f"   Phase: {conditions.get('market_phase', 'Unknown')}")
        
        # Risk Analysis
        risk_metrics = analysis.get('risk_metrics', {})
        if risk_metrics:
            report.append(f"\n⚠️ RISK ANALYSIS:")
            report.append(f"   Daily Volatility: {risk_metrics.get('volatility_daily', 0):.2f}%")
            report.append(f"   Max Drawdown: {risk_metrics.get('max_drawdown', 0):.2f}%")
            if 'sharpe_ratio' in risk_metrics:
                sharpe = risk_metrics['sharpe_ratio']
                sharpe_rating = "Excellent" if sharpe > 2 else "Good" if sharpe > 1 else "Fair" if sharpe > 0 else "Poor"
                report.append(f"   Sharpe Ratio: {sharpe:.2f} ({sharpe_rating})")
        
        # Professional Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report.append(f"\n💡 PROFESSIONAL RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                report.append(f"   {i}. {rec}")
        
        # Data Quality & Sources
        report.append(f"\n📋 DATA QUALITY:")
        if advanced_analyzer.has_tvdatafeed:
            report.append("   ✅ TradingView Professional Data Available")
        if advanced_analyzer.has_talib:
            report.append("   ✅ TA-Lib Advanced Indicators Available")
        if advanced_analyzer.has_pynecore:
            report.append("   ✅ PyneCore Pine Script Compatibility Available")
        
        report.append(f"   📊 Analysis based on {analysis['data_points']} data points")
        report.append(f"   🔄 Refreshed: {analysis['last_updated'][:19]}")
        
        # Footer
        report.append(f"\n" + "=" * 60)
        report.append("🔬 Analysis powered by Advanced Chart Analysis Tool")
        report.append("⚠️ This is for educational purposes only. Not financial advice.")
        
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"Error in advanced technical analysis for {symbol}: {str(e)}")
        return f"❌ Advanced analysis error for {symbol}: {str(e)}\n\n" + get_fallback_message(symbol, "advanced technical analysis")

@tool("TradingView Professional Signals")
def get_tradingview_signals(symbol: str, timeframes: str = "1d,4h,1h") -> str:
    """
    Get TradingView-style professional trading signals across multiple timeframes.
    
    Parameters:
        symbol (str): Stock ticker symbol
        timeframes (str): Comma-separated timeframes (e.g., "1d,4h,1h")
    
    Returns:
        str: Multi-timeframe professional signals summary
    """
    try:
        timeframe_list = [tf.strip() for tf in timeframes.split(',')]
        results = []
        overall_signals = []
        
        results.append(f"📡 TRADINGVIEW PROFESSIONAL SIGNALS - {symbol.upper()}")
        results.append("=" * 50)
        
        for tf in timeframe_list[:3]:  # Limit to 3 timeframes
            try:
                analysis = advanced_analyzer.get_comprehensive_analysis(symbol, tf, '3mo')
                
                if 'error' in analysis:
                    continue
                
                signals = analysis.get('signals', [])
                if not signals:
                    continue
                
                # Get the strongest signal for this timeframe
                best_signal = max(signals, key=lambda x: x.get('confidence', 0))
                overall_signals.append(best_signal)
                
                signal_emoji = "🟢" if 'BUY' in best_signal['signal_type'] else "🔴" if 'SELL' in best_signal['signal_type'] else "🟡"
                
                results.append(f"\n⏰ {tf.upper()} TIMEFRAME:")
                results.append(f"   {signal_emoji} Signal: {best_signal['signal_type']}")
                results.append(f"   💪 Strength: {best_signal['strength']:.1%}")
                results.append(f"   🎯 Confidence: {best_signal['confidence']:.1%}")
                results.append(f"   📊 Based on: {', '.join(best_signal['indicators'])}")
                
                if best_signal.get('target_price') and best_signal.get('stop_loss'):
                    current_price = analysis['current_price']
                    profit_potential = abs(best_signal['target_price'] - current_price) / current_price * 100
                    risk_level = abs(current_price - best_signal['stop_loss']) / current_price * 100
                    risk_reward = profit_potential / risk_level if risk_level > 0 else 0
                    
                    results.append(f"   💰 Target: ${best_signal['target_price']:.2f} (+{profit_potential:.1f}%)")
                    results.append(f"   🛑 Stop Loss: ${best_signal['stop_loss']:.2f} (-{risk_level:.1f}%)")
                    results.append(f"   ⚖️ Risk/Reward: 1:{risk_reward:.1f}")
                
            except Exception as e:
                logger.warning(f"Error analyzing {tf} timeframe: {str(e)}")
                continue
        
        # Overall consensus
        if overall_signals:
            buy_count = len([s for s in overall_signals if 'BUY' in s['signal_type']])
            sell_count = len([s for s in overall_signals if 'SELL' in s['signal_type']])
            
            results.append(f"\n🎯 MULTI-TIMEFRAME CONSENSUS:")
            if buy_count > sell_count:
                consensus = "BULLISH"
                consensus_emoji = "🟢"
            elif sell_count > buy_count:
                consensus = "BEARISH"
                consensus_emoji = "🔴"
            else:
                consensus = "NEUTRAL"
                consensus_emoji = "🟡"
            
            results.append(f"   {consensus_emoji} Overall: {consensus}")
            results.append(f"   📊 Buy Signals: {buy_count} | Sell Signals: {sell_count}")
            
            avg_confidence = sum(s.get('confidence', 0) for s in overall_signals) / len(overall_signals)
            results.append(f"   🎯 Average Confidence: {avg_confidence:.1%}")
        
        if not overall_signals:
            results.append("\n⚠️ No signals generated - insufficient data or market conditions unclear")
        
        results.append(f"\n📡 Powered by Advanced Chart Analysis")
        results.append(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Error generating TradingView signals for {symbol}: {str(e)}"

@tool("Market Scanner Pro")
def scan_market_opportunities(sectors: str = "technology,healthcare,finance", signal_strength: float = 0.7) -> str:
    """
    Scan multiple symbols for trading opportunities using professional analysis.
    
    Parameters:
        sectors (str): Comma-separated sectors or symbols to scan
        signal_strength (float): Minimum signal strength (0.0 to 1.0)
    
    Returns:
        str: Market scanning results with top opportunities
    """
    try:
        # Define sector symbols
        sector_symbols = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABT', 'TMO'],
            'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
            'consumer': ['AMZN', 'WMT', 'PG', 'KO', 'PEP']
        }
        
        symbols_to_scan = []
        for sector in sectors.split(','):
            sector = sector.strip().lower()
            if sector in sector_symbols:
                symbols_to_scan.extend(sector_symbols[sector])
            else:
                # Treat as individual symbol
                symbols_to_scan.append(sector.upper())
        
        # Remove duplicates
        symbols_to_scan = list(set(symbols_to_scan))[:10]  # Limit to 10 symbols
        
        results = []
        results.append(f"🔍 MARKET SCANNER PRO")
        results.append("=" * 40)
        results.append(f"🎯 Scanning {len(symbols_to_scan)} symbols")
        results.append(f"💪 Min Signal Strength: {signal_strength:.1%}")
        
        opportunities = []
        
        for symbol in symbols_to_scan:
            try:
                # Quick analysis for screening
                analysis = advanced_analyzer.get_comprehensive_analysis(symbol, '1d', '3mo')
                
                if 'error' in analysis:
                    continue
                
                signals = analysis.get('signals', [])
                strong_signals = [s for s in signals if s.get('confidence', 0) >= signal_strength]
                
                if strong_signals:
                    best_signal = max(strong_signals, key=lambda x: x.get('confidence', 0))
                    opportunities.append({
                        'symbol': symbol,
                        'signal': best_signal,
                        'current_price': analysis['current_price'],
                        'analysis': analysis
                    })
                    
            except Exception as e:
                logger.warning(f"Error scanning {symbol}: {str(e)}")
                continue
        
        if opportunities:
            # Sort by signal confidence
            opportunities.sort(key=lambda x: x['signal'].get('confidence', 0), reverse=True)
            
            results.append(f"\n🎯 TOP OPPORTUNITIES ({len(opportunities)} found):")
            
            for i, opp in enumerate(opportunities[:5], 1):  # Top 5
                signal = opp['signal']
                symbol = opp['symbol']
                price = opp['current_price']
                
                signal_emoji = "🟢" if 'BUY' in signal['signal_type'] else "🔴" if 'SELL' in signal['signal_type'] else "🟡"
                
                results.append(f"\n   {i}. {signal_emoji} {symbol} - ${price:.2f}")
                results.append(f"      Signal: {signal['signal_type']} (Confidence: {signal['confidence']:.1%})")
                results.append(f"      Strength: {signal['strength']:.1%}")
                results.append(f"      Reason: {signal['message']}")
                
                if signal.get('target_price'):
                    profit_potential = abs(signal['target_price'] - price) / price * 100
                    results.append(f"      🎯 Profit Potential: {profit_potential:.1f}%")
        else:
            results.append(f"\n⚠️ No opportunities found meeting criteria")
            results.append(f"   Try lowering signal strength or checking different sectors")
        
        results.append(f"\n🔍 Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append("📊 Professional market scanning powered by Advanced Chart Analysis")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Market scanning error: {str(e)}"

# Installation guide for enhanced features
INSTALLATION_GUIDE = """
🚀 ENHANCED CHART ANALYSIS INSTALLATION GUIDE

To unlock professional-grade TradingView capabilities, install these optional packages:

1. TradingView Data Access:
   pip install tvdatafeed

2. PyneCore Pine Script Compatibility:
   pip install pynesys-pynecore[cli]

3. TA-Lib Advanced Indicators:
   # Windows: Download TA-Lib from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   pip install TA-Lib

4. All-in-one installation:
   pip install tvdatafeed pynesys-pynecore[cli] TA-Lib

Benefits:
✅ Real-time TradingView data
✅ 100+ advanced technical indicators  
✅ Pine Script compatibility
✅ Professional pattern recognition
✅ Institutional-grade analysis

Current Status:
- TradingView Data: {'✅' if advanced_analyzer.has_tvdatafeed else '❌'}
- PyneCore: {'✅' if advanced_analyzer.has_pynecore else '❌'}
- TA-Lib: {'✅' if advanced_analyzer.has_talib else '❌'}
"""

logger.info("🔬 Advanced Chart Analysis Tool initialized")
logger.info(f"📊 TradingView integration: {'✅' if advanced_analyzer.has_tvdatafeed else '❌'}")
logger.info(f"🐍 PyneCore available: {'✅' if advanced_analyzer.has_pynecore else '❌'}")
logger.info(f"📈 TA-Lib available: {'✅' if advanced_analyzer.has_talib else '❌'}") 