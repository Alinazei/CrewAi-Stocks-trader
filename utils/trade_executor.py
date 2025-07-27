"""
Trade Executor Utility - Handles parsing and execution of trading recommendations
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class TradeAction:
    """Represents a trading action to be executed"""
    symbol: str
    action: str  # buy, sell, hold
    quantity: int  # CRITICAL: Always integer for API compatibility
    price: Optional[float] = None
    reason: str = ""
    confidence: float = 0.0

class TradeExecutor:
    """Handles parsing of agent recommendations and execution of trades"""
    
    def __init__(self):
        self.stockstrader_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the StocksTrader API client"""
        try:
            from tools.stockstrader_api_tool import get_stockstrader_client
            self.stockstrader_client = get_stockstrader_client()
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize StocksTrader client: {e}")
    
    def execute_team_recommendations(self, team_output: str) -> Dict[str, Any]:
        """
        Parse team recommendations and execute trades
        
        Args:
            team_output (str): Raw output from CrewAI team execution
            
        Returns:
            Dict containing execution results and summary
        """
        print(f"⚡ EXECUTING TRADING RECOMMENDATIONS...")
        
        # Validate input - FIX for NoneType split error
        if not team_output or not isinstance(team_output, str) or team_output.strip() == "" or team_output.lower() == "none":
            return {
                "success": False,
                "error": "No valid team output to parse",
                "trades_executed": 0,
                "total_value": 0.0,
                "recommendations": []
            }
        
        # Parse recommendations from team output
        recommendations = self._parse_recommendations(team_output)
        
        if not recommendations:
            return {
                "success": False,
                "error": "No valid trading recommendations found in team output",
                "trades_executed": 0,
                "total_value": 0.0,
                "recommendations": [],
                "raw_output": team_output[:500] + "..." if len(team_output) > 500 else team_output
            }
        
        # Execute trades
        execution_results = []
        total_value = 0.0
        successful_trades = 0
        
        for trade_action in recommendations:
            try:
                result = self._execute_single_trade(trade_action)
                execution_results.append(result)
                
                if result["success"]:
                    successful_trades += 1
                    total_value += result.get("trade_value", 0.0)
                    
            except Exception as e:
                execution_results.append({
                    "success": False,
                    "symbol": trade_action.symbol,
                    "action": trade_action.action,
                    "error": f"Execution error: {str(e)}",
                    "trade_value": 0.0
                })
        
        return {
            "success": successful_trades > 0,
            "trades_executed": successful_trades,
            "total_trades_attempted": len(recommendations),
            "total_value": total_value,
            "execution_results": execution_results,
            "recommendations": [self._trade_action_to_dict(ta) for ta in recommendations]
        }
    
    def _parse_recommendations(self, text: str) -> List[TradeAction]:
        """Parse trading recommendations from text output"""
        recommendations = []
        
        # Common patterns for trading recommendations
        patterns = [
            # Pattern: "BUY 100 shares of AAPL at $150"
            r'(BUY|SELL)\s+(\d+)\s+shares?\s+of\s+([A-Z]{1,5})\s*(?:at\s*\$?(\d+\.?\d*))?',
            # Pattern: "AAPL: BUY 100 shares"
            r'([A-Z]{1,5}):\s*(BUY|SELL)\s+(\d+)\s+shares?',
            # Pattern: "Recommend buying 50 TSLA"
            r'(?:recommend|suggest)\s+(buying|selling)\s+(\d+)\s+([A-Z]{1,5})',
            # Pattern: "Action: BUY, Symbol: AAPL, Quantity: 100"
            r'Action:\s*(BUY|SELL).*?Symbol:\s*([A-Z]{1,5}).*?Quantity:\s*(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text.upper(), re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    
                    if len(groups) >= 3:
                        if 'BUY' in groups[0].upper() or 'BUYING' in groups[0].upper():
                            action = 'buy'
                            if pattern == patterns[0]:  # "BUY 100 shares of AAPL"
                                quantity = int(groups[1])
                                symbol = groups[2]
                                price = float(groups[3]) if groups[3] else None
                            elif pattern == patterns[1]:  # "AAPL: BUY 100 shares"
                                symbol = groups[0]
                                quantity = int(groups[2])
                                price = None
                            elif pattern == patterns[2]:  # "recommend buying 50 TSLA"
                                quantity = int(groups[1])
                                symbol = groups[2]
                                price = None
                            else:  # Action/Symbol/Quantity format
                                symbol = groups[1]
                                quantity = int(groups[2])
                                price = None
                                
                        elif 'SELL' in groups[0].upper() or 'SELLING' in groups[0].upper():
                            action = 'sell'
                            if pattern == patterns[0]:
                                quantity = int(groups[1])
                                symbol = groups[2]
                                price = float(groups[3]) if groups[3] else None
                            elif pattern == patterns[1]:
                                symbol = groups[0]
                                quantity = int(groups[2])
                                price = None
                            elif pattern == patterns[2]:
                                quantity = int(groups[1])
                                symbol = groups[2]
                                price = None
                            else:
                                symbol = groups[1]
                                quantity = int(groups[2])
                                price = None
                        else:
                            continue
                        
                        # CRITICAL FIX: Ensure quantity is always a positive integer
                        quantity = max(1, int(abs(quantity)))
                        
                        trade_action = TradeAction(
                            symbol=symbol.upper(),
                            action=action,
                            quantity=quantity,
                            price=price,
                            reason=f"Parsed from team recommendation",
                            confidence=0.8
                        )
                        
                        recommendations.append(trade_action)
                        
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Warning: Could not parse recommendation from: {match.group()}")
                    continue
        
        # Remove duplicates (same symbol + action)
        unique_recommendations = []
        seen = set()
        
        for rec in recommendations:
            key = f"{rec.symbol}_{rec.action}"
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _execute_single_trade(self, trade_action: TradeAction) -> Dict[str, Any]:
        """Execute a single trade action"""
        if not self.stockstrader_client:
            return self._create_error_result("StocksTrader API not available", trade_action)
        
        try:
            # Get current price for position sizing
            quote_response = self.stockstrader_client.get_quote(trade_action.symbol)
            if not quote_response or not quote_response.get('success'):
                return self._create_error_result("Could not get current price", trade_action)
            
            current_price = float(quote_response.get('data', {}).get('price', 0))
            if current_price <= 0:
                return self._create_error_result("Invalid current price", trade_action)
            
            # Use provided price or current market price
            execution_price = trade_action.price if trade_action.price else current_price
            
            # For buy orders, validate against account buying power
            if trade_action.action.lower() == 'buy':
                account_response = self.stockstrader_client.get_account()
                if account_response and account_response.get('success'):
                    buying_power = float(account_response.get('data', {}).get('buyingPower', 0))
                    required_capital = trade_action.quantity * execution_price
                    
                    if required_capital > buying_power:
                        # Adjust quantity to fit buying power
                        max_quantity = int(buying_power / execution_price)
                        if max_quantity < 1:
                            return self._create_error_result("Insufficient buying power", trade_action)
                        trade_action.quantity = max_quantity
            
            # CRITICAL FIX: Convert to whole shares (integers) for StocksTrader API
            trade_action.quantity = int(round(trade_action.quantity))
            
            # Basic safety checks
            if trade_action.quantity <= 0:
                return self._create_error_result("Invalid quantity - must be at least 1 whole share", trade_action)
            
            position_value = trade_action.quantity * execution_price
            
            # Execute the trade via StocksTrader API
            print(f"🚀 Executing {trade_action.action.upper()}: {trade_action.quantity} shares of {trade_action.symbol} @ ${execution_price:.2f}")
            
            order_response = self.stockstrader_client.place_order(
                symbol=trade_action.symbol,
                side=trade_action.action.lower(),
                quantity=int(trade_action.quantity),  # Ensure integer for API
                order_type='market'
            )
            
            if order_response and order_response.get('success'):
                return {
                    "success": True,
                    "symbol": trade_action.symbol,
                    "action": trade_action.action,
                    "quantity": trade_action.quantity,
                    "price": execution_price,
                    "trade_value": position_value,
                    "order_id": order_response.get('data', {}).get('orderId'),
                    "message": f"✅ Successfully {trade_action.action} {trade_action.quantity} shares of {trade_action.symbol}"
                }
            else:
                error_msg = order_response.get('error', 'Unknown API error') if order_response else 'No response from API'
                return self._create_error_result(f"API Error: {error_msg}", trade_action)
                
        except Exception as e:
            return self._create_error_result(f"Execution exception: {str(e)}", trade_action)
    
    def _create_error_result(self, error: str, trade_action: TradeAction) -> Dict[str, Any]:
        """Create a standardized error result"""
        return {
            "success": False,
            "symbol": trade_action.symbol,
            "action": trade_action.action,
            "quantity": trade_action.quantity,
            "error": error,
            "trade_value": 0.0,
            "message": f"❌ Failed to {trade_action.action} {trade_action.symbol}: {error}"
        }
    
    def _trade_action_to_dict(self, trade_action: TradeAction) -> Dict[str, Any]:
        """Convert TradeAction to dictionary"""
        return {
            "symbol": trade_action.symbol,
            "action": trade_action.action,
            "quantity": trade_action.quantity,
            "price": trade_action.price,
            "reason": trade_action.reason,
            "confidence": trade_action.confidence
        } 

# Create global executor instance
_executor = TradeExecutor()

def execute_team_recommendations(team_output: str) -> Dict[str, Any]:
    """
    Execute team recommendations using the global trade executor
    
    Args:
        team_output (str): Raw output from CrewAI team execution
        
    Returns:
        Dict containing execution results and summary
    """
    return _executor.execute_team_recommendations(team_output)

def parse_recommendations(team_output: str) -> List[Dict[str, Any]]:
    """
    Parse team recommendations without executing them
    
    Args:
        team_output (str): Raw output from CrewAI team execution
        
    Returns:
        List of parsed trade recommendations
    """
    return _executor._parse_recommendations(team_output) 