#!/usr/bin/env python3
"""
Market Hours Detection Utility
Detects if markets are open/closed and provides appropriate messaging
if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
"""

import datetime
import pytz
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MarketStatus:
    is_open: bool
    status: str
    next_open: Optional[datetime.datetime]
    next_close: Optional[datetime.datetime]
    market_day: bool

class MarketHoursChecker:
    """Check if stock markets are currently open
    if you need eney tool to do your job,ask the coder agent to create it en be specific about the tool you need
    """
    
    def __init__(self):
        self.us_eastern = pytz.timezone('US/Eastern')
        self.utc = pytz.UTC
        
        # US Market hours (Eastern Time)
        self.market_open_time = datetime.time(9, 30)  # 9:30 AM ET
        self.market_close_time = datetime.time(16, 0)  # 4:00 PM ET
        
        # US Market holidays (major ones)
        self.holidays_2024 = [
            datetime.date(2024, 1, 1),   # New Year's Day
            datetime.date(2024, 1, 15),  # Martin Luther King Jr. Day
            datetime.date(2024, 2, 19),  # Presidents Day
            datetime.date(2024, 3, 29),  # Good Friday
            datetime.date(2024, 5, 27),  # Memorial Day
            datetime.date(2024, 6, 19),  # Juneteenth
            datetime.date(2024, 7, 4),   # Independence Day
            datetime.date(2024, 9, 2),   # Labor Day
            datetime.date(2024, 11, 28), # Thanksgiving
            datetime.date(2024, 12, 25), # Christmas
        ]
    
    def get_market_status(self) -> MarketStatus:
        """Get current market status"""
        now_et = datetime.datetime.now(self.us_eastern)
        today = now_et.date()
        
        # Check if it's a weekend
        is_weekend = today.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        # Check if it's a holiday
        is_holiday = today in self.holidays_2024
        
        # Check if it's a market day
        market_day = not (is_weekend or is_holiday)
        
        if not market_day:
            if is_weekend:
                status = "CLOSED - Weekend"
            else:
                status = "CLOSED - Holiday"
            
            next_open = self._get_next_market_open(now_et)
            return MarketStatus(
                is_open=False,
                status=status,
                next_open=next_open,
                next_close=None,
                market_day=False
            )
        
        # Check if market is currently open
        current_time = now_et.time()
        
        if self.market_open_time <= current_time <= self.market_close_time:
            # Market is open
            next_close = now_et.replace(
                hour=self.market_close_time.hour,
                minute=self.market_close_time.minute,
                second=0,
                microsecond=0
            )
            
            return MarketStatus(
                is_open=True,
                status="OPEN",
                next_open=None,
                next_close=next_close,
                market_day=True
            )
        else:
            # Market is closed but it's a trading day
            if current_time < self.market_open_time:
                status = "CLOSED - Pre-market"
                next_open = now_et.replace(
                    hour=self.market_open_time.hour,
                    minute=self.market_open_time.minute,
                    second=0,
                    microsecond=0
                )
            else:
                status = "CLOSED - After-hours"
                next_open = self._get_next_market_open(now_et)
            
            return MarketStatus(
                is_open=False,
                status=status,
                next_open=next_open,
                next_close=None,
                market_day=True
            )
    
    def _get_next_market_open(self, current_time: datetime.datetime) -> datetime.datetime:
        """Get the next market open time"""
        # Start with tomorrow
        next_day = current_time.date() + datetime.timedelta(days=1)
        
        # Find the next weekday that's not a holiday
        while next_day.weekday() >= 5 or next_day in self.holidays_2024:
            next_day += datetime.timedelta(days=1)
        
        return self.us_eastern.localize(datetime.datetime.combine(
            next_day, self.market_open_time
        ))
    
    def get_market_hours_message(self) -> str:
        """Get a formatted message about market hours"""
        status = self.get_market_status()
        
        if status.is_open:
            time_to_close = status.next_close - datetime.datetime.now(self.us_eastern)
            hours, remainder = divmod(time_to_close.seconds, 3600)
            minutes = remainder // 60
            
            return f"🟢 **MARKET OPEN** - Closes in {hours}h {minutes}m"
        else:
            if status.next_open:
                now = datetime.datetime.now(self.us_eastern)
                time_to_open = status.next_open - now
                
                if time_to_open.days > 0:
                    return f"🔴 **{status.status}** - Opens in {time_to_open.days} days"
                else:
                    hours, remainder = divmod(time_to_open.seconds, 3600)
                    minutes = remainder // 60
                    return f"🔴 **{status.status}** - Opens in {hours}h {minutes}m"
            else:
                return f"🔴 **{status.status}**"
    
    def get_trading_recommendations(self) -> str:
        """Get trading recommendations based on market status"""
        status = self.get_market_status()
        
        if status.is_open:
            return """
🟢 **MARKET OPEN - ACTIVE TRADING**
• Live trading and real-time analysis available
• Use '!scan' for current market snapshot
• Monitor positions and execute trades
• Real-time sentiment analysis active
"""
        else:
            return """
🔴 **MARKET CLOSED - ANALYSIS MODE**
• Focus on research and analysis
• Use '!scan' for after-hours analysis
• Review historical performance
• Plan strategies for next trading session
• Monitor pre-market/after-hours sentiment
"""

# Singleton instance
market_checker = MarketHoursChecker()

def get_market_status() -> MarketStatus:
    """Get current market status"""
    return market_checker.get_market_status()

def get_market_hours_message() -> str:
    """Get market hours message"""
    return market_checker.get_market_hours_message()

def get_trading_recommendations() -> str:
    """Get trading recommendations"""
    return market_checker.get_trading_recommendations()

def is_market_open() -> bool:
    """Simple check if market is open"""
    return market_checker.get_market_status().is_open 