# 📊 StocksTrader API Tool Guide for AI Agents

## 🎯 Overview
This guide provides comprehensive instructions for AI agents on how to use the enhanced StocksTrader API tool. The tool provides complete access to account management, position tracking, order management, and real-time market data.

## ⚡ **PRIORITY TOOL USAGE** (Updated)

### **✅ RECOMMENDED: StocksTrader API Tools**
**Use these tools FIRST for all trading operations:**
- `get_account_information()` - Account details and balance
- `get_current_positions()` - Active positions with P&L
- `get_real_time_quote(ticker)` - Live market prices
- `place_market_order()` / `place_limit_order()` - Execute trades
- `close_position(deal_id)` - Close positions
- `execute_profit_taking_strategy()` - Automated profit realization

### **⚠️ USE WITH CAUTION: Portfolio Optimization Tools**
**These tools may have data limitations:**
- `Portfolio Analysis Tool` - May fail with validation errors
- `Portfolio Optimization Tool` - May return "No price data available"
- **Alternative**: Use StocksTrader API for real portfolio data

### **🚀 NEW: Automated Profit-Taking Strategy**
The system now includes automated profit-taking capabilities:
```python
# Execute comprehensive profit-taking strategy
execute_profit_taking_strategy(profit_threshold=2.0, analysis_symbols="AAPL,NIO,TSLA")

# Quick profit check
check_profitable_positions(min_profit_usd=10.0)
```

## 🚀 Available Tool Functions

## 📋 **SUPPORTED ORDER SIDES**

The StocksTrader API supports exactly 4 order sides:

### **Order Types (Create New Deals):**
- **`"buy"`** - Open a long position (bet on price increase)
- **`"sell"`** - Open a short position (bet on price decrease)
- **`"sell_short"`** - Open a short position (explicit short selling)
- **`"buy_to_cover"`** - Close a short position (cover existing short)

### **Position Closing (Close Existing Deals):**
- **`close_position(deal_id)`** - Close ANY position (long or short) using deal ID
- **DO NOT use order sides to close positions** - This is incorrect usage

### **CRITICAL API UNDERSTANDING:**
- ❌ **INCORRECT**: Using "sell" to close long positions
- ✅ **CORRECT**: Using `close_position(deal_id)` to close any position
- ❌ **NOT SUPPORTED**: "short", "close" - These will cause API errors
- ✅ **SUPPORTED**: "buy", "sell", "sell_short", "buy_to_cover"

### **Trading Workflow:**
```
1. Place order → Creates deal when executed
2. Monitor deal → Use get_current_positions()
3. Close position → Use close_position(deal_id)
```

### 1. Account Management Tools

#### `get_all_accounts()`
**Purpose**: Get list of all user accounts
**Parameters**: None
**Returns**: List of available trading accounts with details
**Usage**:
```python
account_list = get_all_accounts()
```

#### `get_account_information()`
**Purpose**: Get detailed account information including balance, equity, and P&L
**Parameters**: None
**Returns**: Formatted account summary with cash and margin details
**Usage**:
```python
account_info = get_account_information()
```

#### `get_all_instruments()`
**Purpose**: Get list of all available trading instruments
**Parameters**: None
**Returns**: List of tradeable instruments with contract details
**Usage**:
```python
instruments = get_all_instruments()
```

#### `get_instrument_trading_info(ticker)`
**Purpose**: Get detailed trading conditions for a specific instrument
**Parameters**: 
- `ticker` (str): Instrument ticker symbol
**Returns**: Trading conditions, leverage, volume limits
**Usage**:
```python
trading_info = get_instrument_trading_info("AAPL")
```

### 2. Market Data Tools

#### `get_real_time_quote(ticker)`
**Purpose**: Get real-time bid/ask/last price for a ticker
**Parameters**:
- `ticker` (str): Stock ticker symbol (e.g., "AAPL", "TSLA")
**Returns**: Real-time quote with bid, ask, last price, and spread
**Usage**:
```python
quote = get_real_time_quote("AAPL")
```

### 3. Position Management Tools

#### `get_current_positions()`
**Purpose**: Get all current open positions with P&L
**Parameters**: None
**Returns**: List of open positions with real-time P&L calculations
**Usage**:
```python
positions = get_current_positions()
```

#### `get_position_history(limit=50)`
**Purpose**: Get historical position data
**Parameters**:
- `limit` (int): Maximum number of positions to retrieve (default: 50)
**Returns**: Historical position data with P&L results
**Usage**:
```python
history = get_position_history(limit=20)
```

#### `modify_position(deal_id, stop_loss=None, take_profit=None)`
**Purpose**: Modify an existing position's stop loss or take profit
**Parameters**:
- `deal_id` (str): Position/deal ID to modify
- `stop_loss` (float, optional): New stop loss price
- `take_profit` (float, optional): New take profit price
**Returns**: Modification result
**Usage**:
```python
result = modify_position("001389", stop_loss=245.00, take_profit=265.00)
```

#### `close_position(deal_id)`
**Purpose**: Close an open position
**Parameters**:
- `deal_id` (str): Position/deal ID to close
**Returns**: Position closure result
**Usage**:
```python
result = close_position("001389")
```

### 4. Order Management Tools

#### `get_active_orders()`
**Purpose**: Get list of all active/pending orders
**Parameters**: None
**Returns**: List of active orders with details
**Usage**:
```python
active_orders = get_active_orders()
```

#### `get_order_history(status="all", limit=50)`
**Purpose**: Get order history with filtering
**Parameters**:
- `status` (str): Order status filter ("filled", "rejected", "canceled", "active", "all")
- `limit` (int): Maximum number of orders to retrieve
**Returns**: Filtered order history
**Usage**:
```python
filled_orders = get_order_history(status="filled", limit=10)
all_orders = get_order_history(status="all", limit=25)
```

### 5. Order Placement Tools

#### `place_market_order(ticker, side, volume, stop_loss=None, take_profit=None)`
**Purpose**: Place a market order (executes immediately at current price)
**Parameters**:
- `ticker` (str): Stock ticker symbol
- `side` (str): "buy", "sell", "sell_short", or "buy_to_cover"
- `volume` (float): Number of shares to trade
- `stop_loss` (float, optional): Stop loss price
- `take_profit` (float, optional): Take profit price
**Returns**: Order placement result with order ID
**Usage**:
```python
# Long positions
result = place_market_order("AAPL", "buy", 100, stop_loss=170.00, take_profit=190.00)
result = place_market_order("AAPL", "sell", 100)  # Close long position

# Short positions
result = place_market_order("TSLA", "sell_short", 50, stop_loss=270.00, take_profit=250.00)
result = place_market_order("TSLA", "buy_to_cover", 50)  # Close short position
```

#### `place_limit_order(ticker, side, volume, price, stop_loss=None, take_profit=None)`
**Purpose**: Place a limit order (executes only at specified price or better)
**Parameters**:
- `ticker` (str): Stock ticker symbol
- `side` (str): "buy", "sell", "sell_short", or "buy_to_cover"
- `volume` (float): Number of shares to trade
- `price` (float): Limit price
- `stop_loss` (float, optional): Stop loss price
- `take_profit` (float, optional): Take profit price
**Returns**: Order placement result with order ID
**Usage**:
```python
# Long positions
result = place_limit_order("AAPL", "buy", 100, 175.00, stop_loss=165.00, take_profit=185.00)
result = place_limit_order("AAPL", "sell", 100, 180.00)  # Close long position

# Short positions
result = place_limit_order("TSLA", "sell_short", 50, 260.00, stop_loss=270.00, take_profit=250.00)
result = place_limit_order("TSLA", "buy_to_cover", 50, 250.00)  # Close short position
```

#### `place_stop_order(ticker, side, volume, price, stop_loss=None, take_profit=None)`
**Purpose**: Place a stop order (triggers when price reaches specified level)
**Parameters**:
- `ticker` (str): Stock ticker symbol
- `side` (str): "buy", "sell", "sell_short", or "buy_to_cover"
- `volume` (float): Number of shares to trade
- `price` (float): Stop price (trigger level)
- `stop_loss` (float, optional): Stop loss price
- `take_profit` (float, optional): Take profit price
**Returns**: Order placement result with order ID
**Usage**:
```python
# Long positions
result = place_stop_order("GOOGL", "buy", 25, 145.00, stop_loss=140.00, take_profit=155.00)
result = place_stop_order("GOOGL", "sell", 25, 140.00)  # Stop loss for long position

# Short positions
result = place_stop_order("META", "sell_short", 30, 350.00, stop_loss=360.00, take_profit=330.00)
result = place_stop_order("META", "buy_to_cover", 30, 360.00)  # Stop loss for short position
```

### 6. Order Modification Tools

#### `modify_order(order_id, volume=None, price=None, stop_loss=None, take_profit=None)`
**Purpose**: Modify an existing order's parameters
**Parameters**:
- `order_id` (str): Order ID to modify
- `volume` (float, optional): New volume
- `price` (float, optional): New price
- `stop_loss` (float, optional): New stop loss price
- `take_profit` (float, optional): New take profit price
**Returns**: Modification result
**Usage**:
```python
result = modify_order("12345", volume=150, price=175.00, stop_loss=165.00)
```

#### `cancel_order(order_id)`
**Purpose**: Cancel an active order
**Parameters**:
- `order_id` (str): Order ID to cancel
**Returns**: Cancellation result
**Usage**:
```python
result = cancel_order("12346")
```

## 🎯 Best Practices for AI Agents

### 1. Information Gathering Sequence
```python
# Start with account overview
account_info = get_account_information()
current_positions = get_current_positions()
active_orders = get_active_orders()

# Get market data for analysis
quote = get_real_time_quote("AAPL")
trading_info = get_instrument_trading_info("AAPL")
```

### 2. Risk Management
- Always check account balance before placing orders
- Use stop loss orders for risk management
- Monitor position sizes relative to account equity
- Check instrument trading conditions (min/max volume, leverage)

### 3. Order Management Flow
```python
# 1. Get current market price
quote = get_real_time_quote("AAPL")

# 2. Check trading conditions
trading_info = get_instrument_trading_info("AAPL")

# 3. Place order with risk management
result = place_limit_order("AAPL", "buy", 100, 175.00, stop_loss=165.00, take_profit=185.00)

# 4. Monitor order status
active_orders = get_active_orders()
```

### 4. Position Monitoring
```python
# Regular position monitoring
positions = get_current_positions()

# Check for positions needing attention
for position in positions:
    if position.unrealized_pnl < -500:  # Example threshold
        # Consider adjusting stop loss or closing position
        modify_position(position.deal_id, stop_loss=new_stop_price)
```

## ⚠️ Trading Modes

### Demo Mode
- Activated when API credentials are not configured
- Returns simulated data for testing
- No real trades are executed
- Identified by "DEMO" or "SIMULATION" in responses

### Live Trading Mode
- Activated when `ENABLE_LIVE_TRADING=true` and API credentials are set
- Executes real trades on live markets
- Uses real account balance and positions
- **USE WITH CAUTION** - real money is at risk

## 🔧 Error Handling

### Common Error Responses
- `"❌ Error: API credentials not configured"` - Set up API keys
- `"❌ Error placing order: Unknown error"` - Check order parameters
- `"❌ Error getting positions: Unknown error"` - API connection issue

### Error Handling Pattern
```python
# Example: Opening a long position
result = place_market_order("AAPL", "buy", 100)
if "❌ Error" in result:
    # Handle error - check credentials, parameters, etc.
    return "Trading operation failed: " + result
elif "✅" in result:
    # Success - continue with next steps
    return "Order placed successfully: " + result

# Example: Opening a short position
result = place_market_order("TSLA", "sell_short", 50)
if "❌ Error" in result:
    return "Short position failed: " + result
elif "✅" in result:
    return "Short position opened: " + result
```

## 📊 Response Format Understanding

### Success Indicators
- `✅` - Successful operation
- `🎯 SIMULATION` - Demo mode operation
- Order ID provided for tracking

### Data Format
- Emojis indicate data types (💰 prices, 📊 volumes, ⏰ times)
- Formatted tables with clear sections
- Real-time timestamps for market data

## 🚨 Safety Guidelines

### 1. Volume Limits
- Check `max_volume` from `get_instrument_trading_info()`
- Respect position size limits
- Consider account equity when sizing positions

### 2. Price Validation
- Verify prices are within reasonable ranges
- Check bid/ask spreads before placing orders
- Use limit orders for better price control

### 3. Order Management
- Always set stop losses for risk management
- Monitor active orders regularly
- Cancel stale orders that are no longer needed

## 🔄 Workflow Examples

### Complete Trading Workflow
```python
# 1. Account Assessment
account = get_account_information()
available_funds = extract_available_funds(account)

# 2. Market Analysis
quote = get_real_time_quote("AAPL")
current_price = extract_current_price(quote)

# 3. Position Sizing
position_size = calculate_position_size(available_funds, current_price)

# 4. Order Placement
result = place_limit_order("AAPL", "buy", position_size, 
                          price=current_price * 0.99,  # Slightly below market
                          stop_loss=current_price * 0.95,  # 5% stop loss
                          take_profit=current_price * 1.10)  # 10% profit target

# Alternative: Short position example
# result = place_limit_order("TSLA", "sell_short", position_size,
#                           price=current_price * 1.01,  # Slightly above market
#                           stop_loss=current_price * 1.05,  # 5% stop loss
#                           take_profit=current_price * 0.90)  # 10% profit target

# 5. Order Monitoring
active_orders = get_active_orders()
# Check if order was filled, modify if needed
```

### Portfolio Review Workflow
```python
# 1. Get complete portfolio picture
account_info = get_account_information()
positions = get_current_positions()
active_orders = get_active_orders()

# 2. Analyze each position
for position in positions:
    quote = get_real_time_quote(position.ticker)
    # Analyze performance, adjust stops if needed
    if position.unrealized_pnl < threshold:
        modify_position(position.deal_id, stop_loss=new_stop)

# 3. Review order status
for order in active_orders:
    # Cancel stale orders, modify prices if needed
    if order.age > max_age:
        cancel_order(order.id)
```

## 📈 Integration with Other Tools

### Market Analysis Integration
```python
# Combine with market research tools
stock_analysis = research_stock("AAPL")
quote = get_real_time_quote("AAPL")

# Make informed trading decisions
if stock_analysis.recommendation == "BUY":
    result = place_limit_order("AAPL", "buy", 100, quote.bid_price)
elif stock_analysis.recommendation == "SELL_SHORT":
    result = place_limit_order("AAPL", "sell_short", 100, quote.ask_price)
```

### Risk Management Integration
```python
# Use with risk management tools
risk_assessment = calculate_portfolio_risk()
account_info = get_account_information()

# Adjust position sizes based on risk
if risk_assessment.risk_level > "MODERATE":
    # Reduce position sizes or close risky positions
    positions = get_current_positions()
    for position in high_risk_positions:
        close_position(position.deal_id)
```

## 🚨 **COMMON ERRORS & TROUBLESHOOTING** (Updated)

### **❌ Portfolio Tool Validation Errors**
**Problem**: `weights field required` or `No price data available`
**Solution**: Use StocksTrader API tools instead:
```python
# Instead of: Portfolio Analysis Tool
# Use: StocksTrader API
positions = get_current_positions()
account = get_account_information()
```

### **❌ Chart Analysis & Portfolio Tool Callable Errors**
**Problem**: `'Tool' object is not callable` in profit-taking strategy and portfolio tools
**Solution**: ✅ FIXED - Both issues resolved:
```python
# ✅ FIXED: Profit-taking strategy now works correctly
execute_profit_taking_strategy(profit_threshold=2.0)

# ✅ FIXED: Portfolio tools now recommend StocksTrader API
# Instead of portfolio tools with data limitations, use:
get_current_positions()  # Real portfolio data
get_account_information()  # Real account data
```

### **❌ Incorrect Deal ID Format**
**Problem**: `Unknown error` when closing positions with descriptive text
**Solution**: Use numeric deal ID from get_current_positions():
```python
# ❌ WRONG: close_position("AAPL SELL 20 shares")
# ✅ CORRECT: close_position("001158278405")
```

### **⚠️ Tool Priority Guidelines**
1. **First choice**: StocksTrader API tools (always reliable)
2. **Second choice**: Market research tools (usually work)
3. **Use carefully**: Portfolio optimization tools (may fail)

## 📝 Notes for AI Agents

1. **Always check account balance** before placing orders
2. **Use appropriate order types** (market for immediate execution, limit for price control)
3. **Implement proper risk management** with stop losses
4. **Monitor positions regularly** and adjust as needed
5. **Handle errors gracefully** and provide clear feedback to users
6. **Respect trading hours** and market conditions
7. **Keep detailed logs** of all trading activities for analysis
8. **🆕 Use numeric deal IDs** from get_current_positions() for closing positions
9. **🆕 Prefer StocksTrader API** over portfolio optimization tools
10. **🆕 Use automated profit-taking** for systematic profit realization

## 🎯 Quick Reference (Updated)

### **🏆 PRIORITY 1: StocksTrader API Functions**
- `get_account_information()` - Account overview & balance
- `get_current_positions()` - Current holdings with P&L
- `get_real_time_quote(ticker)` - Live market prices
- `place_market_order(ticker, side, volume)` - Instant execution
- `close_position(deal_id)` - Exit positions (use numeric ID!)
- `get_active_orders()` - Pending orders

### **🚀 PRIORITY 2: New Profit-Taking Functions**
- `execute_profit_taking_strategy(profit_threshold, symbols)` - Automated profit realization
- `check_profitable_positions(min_profit_usd)` - Quick profit assessment

### **🛡️ Risk Management Functions**
- `modify_position(deal_id, stop_loss, take_profit)` - Adjust risk parameters
- `cancel_order(order_id)` - Cancel pending orders
- `get_position_history(limit)` - Review past performance

### **📊 Analysis Functions (Use Carefully)**
- `get_order_history(status, limit)` - Trading history
- `get_instrument_trading_info(ticker)` - Trading conditions
- Market research tools - Usually reliable
- Portfolio optimization tools - May have data issues

### **⚡ Quick Trading Workflow**
```python
# 1. Check account
account = get_account_information()

# 2. Check positions
positions = get_current_positions()

# 3. Execute profit-taking if needed
execute_profit_taking_strategy(profit_threshold=2.0)

# 4. Get real-time price
quote = get_real_time_quote("AAPL")

# 5. Place trade
order = place_market_order("AAPL", "buy", 100)
```

---

**🔒 Remember**: Real trading involves financial risk. Always use appropriate risk management and never risk more than you can afford to lose. 