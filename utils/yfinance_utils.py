"""
Shared utilities for safe Yahoo Finance API calls with error handling and rate limiting
"""

import yfinance as yf
import time
import json
import requests
from typing import Optional, Dict, Any, List
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Circuit breaker for Yahoo Finance API
class YFinanceCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_minutes=10):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_minutes * 60
        self.failure_count = 0
        self.last_failure_time = 0
        self.is_open = False
    
    def record_failure(self):
        """Record a failure and potentially open the circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Yahoo Finance circuit breaker OPENED after {self.failure_count} failures")
    
    def record_success(self):
        """Record a success and reset the circuit"""
        self.failure_count = 0
        self.is_open = False
    
    def can_proceed(self):
        """Check if we can proceed with API calls"""
        if not self.is_open:
            return True
        
        # Check if timeout has passed
        if time.time() - self.last_failure_time > self.timeout_seconds:
            self.is_open = False
            self.failure_count = 0
            logger.info("Yahoo Finance circuit breaker RESET - attempting calls again")
            return True
        
        return False

# Global circuit breaker
yfinance_circuit_breaker = YFinanceCircuitBreaker()

class RateLimiter:
    """Rate limiter to prevent hitting Yahoo Finance API limits"""
    
    def __init__(self, max_calls_per_minute=8):
        self.max_calls = max_calls_per_minute
        self.calls = []
        
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        if len(self.calls) >= self.max_calls:
            sleep_time = 60 - (now - self.calls[0]) + 1
            logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        
        self.calls.append(now)

# Global rate limiter - shared across all tools
global_rate_limiter = RateLimiter(max_calls_per_minute=4)  # More conservative - reduced from 8 to 4

def safe_yfinance_call(ticker_symbol: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    Safely call Yahoo Finance with retry logic and error handling
    
    Args:
        ticker_symbol: Stock symbol to fetch
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with stock info or None if failed
    """
    # Check circuit breaker first
    if not yfinance_circuit_breaker.can_proceed():
        logger.info(f"Yahoo Finance circuit breaker is OPEN - skipping call for {ticker_symbol}")
        return None
    
    for attempt in range(max_retries):
        try:
            # Rate limiting protection
            global_rate_limiter.wait_if_needed()
            
            logger.debug(f"Attempting to fetch data for {ticker_symbol} (attempt {attempt + 1}/{max_retries})")
            
            # Create ticker and get info
            ticker = yf.Ticker(ticker_symbol)
            
            # Try to get basic info first
            try:
                info = ticker.info
                if not info or len(info) < 5:  # Very basic validation
                    raise ValueError("Insufficient data returned")
                
                # Record success in circuit breaker
                yfinance_circuit_breaker.record_success()
                return info
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON/Data error for {ticker_symbol}: {str(e)}")
                yfinance_circuit_breaker.record_failure()
                
                if attempt < max_retries - 1:
                    sleep_time = min((attempt + 1) * 3, 30)  # Cap at 30 seconds, increased base delay
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise e
                    
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):  # Rate limit error
                yfinance_circuit_breaker.record_failure()
                sleep_time = min((attempt + 1) * 15, 60)  # Longer wait for rate limits, cap at 60s
                logger.warning(f"Rate limit hit for {ticker_symbol}, waiting {sleep_time} seconds")
                time.sleep(sleep_time)
                
                # If this is the last attempt and still getting 429, return None gracefully
                if attempt == max_retries - 1:
                    logger.error(f"Persistent rate limiting for {ticker_symbol} after {max_retries} attempts")
                    return None
                continue
            else:
                logger.error(f"HTTP error for {ticker_symbol}: {str(e)}")
                yfinance_circuit_breaker.record_failure()
                if attempt == max_retries - 1:
                    raise e
                    
        except Exception as e:
            logger.error(f"Unexpected error for {ticker_symbol}: {str(e)}")
            yfinance_circuit_breaker.record_failure()
            if attempt == max_retries - 1:
                return None  # Graceful failure instead of raising
            time.sleep((attempt + 1) * 3)
    
    return None

def safe_yfinance_history(ticker_symbol: str, period: str = "1y", interval: str = "1d", max_retries: int = 3):
    """
    Safely get historical data from Yahoo Finance
    
    Args:
        ticker_symbol: Stock symbol to fetch
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        max_retries: Maximum number of retry attempts
        
    Returns:
        Pandas DataFrame with historical data or None if failed
    """
    for attempt in range(max_retries):
        try:
            # Rate limiting protection
            global_rate_limiter.wait_if_needed()
            
            logger.debug(f"Fetching history for {ticker_symbol} (attempt {attempt + 1}/{max_retries})")
            
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise ValueError("No historical data returned")
                
            return hist
            
        except requests.exceptions.HTTPError as e:
            if "429" in str(e):
                sleep_time = min((attempt + 1) * 15, 60)  # Longer wait, capped at 60s
                logger.warning(f"Rate limit hit for {ticker_symbol} history, waiting {sleep_time} seconds")
                time.sleep(sleep_time)
                
                # If this is the last attempt and still getting 429, return None gracefully
                if attempt == max_retries - 1:
                    logger.error(f"Persistent rate limiting for {ticker_symbol} history after {max_retries} attempts")
                    return None
                continue
            else:
                logger.error(f"HTTP error for {ticker_symbol} history: {str(e)}")
                if attempt == max_retries - 1:
                    return None  # Graceful failure
                    
        except Exception as e:
            logger.error(f"Error fetching history for {ticker_symbol}: {str(e)}")
            if attempt == max_retries - 1:
                return None  # Graceful failure
            time.sleep((attempt + 1) * 3)
    
    return None

def get_fallback_message(ticker_symbol: str, operation: str = "data fetch") -> str:
    """
    Generate a user-friendly fallback message when Yahoo Finance fails
    
    Args:
        ticker_symbol: Stock symbol that failed
        operation: Type of operation that failed
        
    Returns:
        Formatted error message with suggestions
    """
    # Check if circuit breaker is open
    if not yfinance_circuit_breaker.can_proceed():
        return f"""
⚠️ Yahoo Finance temporarily disabled for {ticker_symbol.upper()}

🔒 **Circuit Breaker Active**
• Status: Yahoo Finance API temporarily disabled due to persistent failures
• Auto-retry: Will resume automatically in {int((yfinance_circuit_breaker.timeout_seconds - (time.time() - yfinance_circuit_breaker.last_failure_time)) / 60)} minutes
• Reason: Multiple consecutive API failures detected

💡 **Alternative Actions:**
• Use StocksTrader API for real-time quotes (more reliable)
• Check company news and recent announcements
• Wait for automatic retry or restart the system

📊 **Note**: Circuit breaker prevents overwhelming failed API
"""
    
    return f"""
⚠️ Yahoo Finance {operation} temporarily unavailable for {ticker_symbol.upper()}

🔄 **Fallback Information:**
• Symbol: {ticker_symbol.upper()}
• Status: {operation.title()} failed - Yahoo Finance may be experiencing issues
• Suggestion: Try again in a few minutes or check financial news sources

💡 **Alternative Actions:**
• Check company news and recent announcements
• Review analyst reports and recommendations  
• Monitor social media sentiment
• Consider using StocksTrader API for real-time quotes

📊 **Note**: This may be due to:
- Yahoo Finance rate limiting (429 errors)
- Temporary API issues  
- Symbol delisting or changes
- Network connectivity issues
- JSON parsing errors
"""

def validate_ticker_symbol(symbol: str) -> bool:
    """
    Basic validation for ticker symbols
    
    Args:
        symbol: Ticker symbol to validate
        
    Returns:
        True if symbol appears valid, False otherwise
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    symbol = symbol.strip().upper()
    
    # Basic checks
    if len(symbol) < 1 or len(symbol) > 10:
        return False
    
    # Should contain only letters, numbers, dots, and hyphens
    if not all(c.isalnum() or c in '.-' for c in symbol):
        return False
    
    return True

def batch_safe_yfinance_call(ticker_symbols: List[str], max_retries: int = 3) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Safely fetch data for multiple tickers with rate limiting
    
    Args:
        ticker_symbols: List of ticker symbols to fetch
        max_retries: Maximum retry attempts per symbol
        
    Returns:
        Dictionary mapping symbols to their data (or None if failed)
    """
    results = {}
    
    for symbol in ticker_symbols:
        if not validate_ticker_symbol(symbol):
            logger.warning(f"Invalid ticker symbol: {symbol}")
            results[symbol] = None
            continue
            
        try:
            results[symbol] = safe_yfinance_call(symbol, max_retries)
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            results[symbol] = None
    
    return results 