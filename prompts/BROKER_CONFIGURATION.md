# Broker Configuration Guide

## Overview
The CrewAI Trading System supports multiple brokers and can be configured to use different trading platforms as the primary broker.

## Supported Brokers

### 1. StocksTrader (Default)
- **API**: StocksTrader API
- **Tools**: StocksTrader API tools
- **Configuration**: Set `PRIMARY_BROKER=stockstrader`

### 2. Alpaca
- **API**: Alpaca Trading API
- **Tools**: Alpaca API tools
- **Configuration**: Set `PRIMARY_BROKER=alpaca`

## Environment Configuration

### Required Environment Variables

```bash
# Primary broker selection
PRIMARY_BROKER=stockstrader    # Options: stockstrader, alpaca

# Trading mode
TRADING_MODE=simulation        # Options: simulation, live
ENABLE_LIVE_TRADING=false     # Set to true for real money trading

# Risk management
MAX_POSITION_SIZE=1000        # Maximum shares per trade
MAX_RISK_PERCENT=2.0         # Maximum risk percentage per trade

# Automatic execution
AUTO_EXECUTE_TRADES=false    # Set to true for automatic execution
```

### StocksTrader Configuration

```bash
# StocksTrader API credentials
STOCKSTRADER_API_KEY=your_api_key_here
STOCKSTRADER_ACCOUNT_ID=your_account_id_here
STOCKSTRADER_API_URL=https://api.stockstrader.com

# Enable live trading (optional)
ENABLE_LIVE_TRADING=false
```

### Alpaca Configuration

```bash
# Alpaca API credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading
# ALPACA_BASE_URL=https://api.alpaca.markets      # Live trading

# Enable live trading (optional)
ENABLE_LIVE_TRADING=false
```

## How Broker Selection Works

### 1. Default Configuration
- **Primary Broker**: StocksTrader (default)
- **Fallback**: Alpaca (if StocksTrader is not configured)

### 2. Tool Selection
The system automatically selects the appropriate tools based on the `PRIMARY_BROKER` setting:

```python
if self.primary_broker == "stockstrader":
    # Uses StocksTrader API tools
    account_info = get_account_information()
    quote_info = get_real_time_quote(symbol)
    result = place_market_order(ticker, side, volume)
else:  # alpaca
    # Uses Alpaca API tools
    account_info = get_alpaca_account_info()
    quote_info = get_alpaca_quote(symbol)
    result = place_alpaca_order(symbol, side, quantity)
```

### 3. Agent Configuration
All agents have access to both broker tools but use the primary broker based on the configuration.

## Switching Brokers

### To Use StocksTrader as Primary:
```bash
export PRIMARY_BROKER=stockstrader
# Configure StocksTrader API credentials
export STOCKSTRADER_API_KEY=your_key
export STOCKSTRADER_ACCOUNT_ID=your_account
```

### To Use Alpaca as Primary:
```bash
export PRIMARY_BROKER=alpaca
# Configure Alpaca API credentials
export ALPACA_API_KEY=your_key
export ALPACA_SECRET_KEY=your_secret
```

## Troubleshooting

### Common Issues

1. **"Tool object is not callable" Error**
   - **Solution**: Ensure you're running the latest version with fixed tool imports

2. **"403 Forbidden" Error**
   - **Cause**: Incorrect API credentials or insufficient permissions
   - **Solution**: Check API credentials and account permissions

3. **Wrong broker being used**
   - **Cause**: PRIMARY_BROKER environment variable not set correctly
   - **Solution**: Set `PRIMARY_BROKER=stockstrader` in your environment

### Verification Commands

```bash
# Check current broker configuration
echo $PRIMARY_BROKER

# Verify StocksTrader credentials
echo $STOCKSTRADER_API_KEY
echo $STOCKSTRADER_ACCOUNT_ID

# Verify Alpaca credentials
echo $ALPACA_API_KEY
echo $ALPACA_SECRET_KEY
```

## Best Practices

1. **Use Environment Files**: Create a `.env` file for configuration
2. **Test in Simulation**: Always test with `ENABLE_LIVE_TRADING=false` first
3. **API Key Security**: Never commit API keys to version control
4. **Monitor Usage**: Check API rate limits and usage
5. **Risk Management**: Set appropriate `MAX_POSITION_SIZE` and `MAX_RISK_PERCENT`

## Example .env File

```bash
# Broker Configuration
PRIMARY_BROKER=stockstrader
TRADING_MODE=simulation
ENABLE_LIVE_TRADING=false

# StocksTrader API
STOCKSTRADER_API_KEY=your_stockstrader_key
STOCKSTRADER_ACCOUNT_ID=your_account_id
STOCKSTRADER_API_URL=https://api.stockstrader.com

# Alpaca API (backup)
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management
MAX_POSITION_SIZE=1000
MAX_RISK_PERCENT=2.0

# Automatic Execution
AUTO_EXECUTE_TRADES=false

# Other APIs
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

## Support

For issues with broker configuration:
1. Check the console output for specific error messages
2. Verify API credentials are correct
3. Ensure the broker service is operational
4. Review the TRADING_SYSTEM_FIXES.md for known issues 