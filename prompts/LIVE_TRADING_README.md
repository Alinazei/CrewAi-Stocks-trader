# 🚀 CrewAI Live Trading System

A comprehensive AI-powered trading system that combines real-time market data, news sentiment analysis, technical chart analysis, and live trading execution using local AI models.

## 🌟 Features

### 🤖 AI-Powered Analysis
- **Local AI Processing**: DeepSeek-R1:8b model via Ollama (completely private and offline)
- **Multi-Agent System**: Specialized financial analyst and strategic trader agents
- **Real-time Decision Making**: Instant analysis and trade execution

### 📊 Market Data & Analysis
- **Real-time Market Data**: Live quotes, bid-ask spreads, and volume data
- **News Sentiment Analysis**: Automated analysis of financial news and market sentiment
- **Technical Chart Analysis**: RSI, MACD, Bollinger Bands, moving averages, and pattern recognition
- **Support/Resistance Levels**: Automated identification of key price levels

### 📈 Technical Indicators
- **RSI (Relative Strength Index)**: Overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Momentum and trend signals
- **Bollinger Bands**: Volatility and price channel analysis
- **Moving Averages**: SMA 20/50/200 and EMA 12/26 for trend analysis
- **Stochastic Oscillator**: Momentum indicator for entry/exit timing
- **Volume Analysis**: Trading volume patterns and anomalies

### 🛡️ Risk Management
- **Position Sizing**: Automatic calculation based on account balance
- **Stop Loss Management**: Automated stop loss placement and adjustment
- **Take Profit Targets**: Technical-based profit-taking levels
- **Risk Percentage Controls**: Maximum risk per trade and daily limits
- **Market Hours Enforcement**: Trading only during market hours

### 🔄 Trading Modes
- **Demo Mode**: Completely simulated data for system testing
- **Simulation Mode**: Real market data with simulated trades
- **Live Trading Mode**: Real trades with real money (use with caution)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd crewai-stock-trader-agents-main

# Install dependencies
pip install -r requirements.txt

# Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull deepseek-r1:8b
ollama serve
```

### 2. Configuration

```bash
# Copy the environment template
cp live_trading_env_template.txt .env

# Edit .env with your configuration
nano .env
```

### 3. Basic Usage

```bash
# Analyze a single stock
python live_trading_main.py TSLA

# Analyze multiple stocks
python live_trading_main.py --watchlist TSLA AAPL GOOGL MSFT

# Force simulation mode
python live_trading_main.py TSLA --mode simulation
```

## 📋 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_MODEL=deepseek-r1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Trading Configuration
TRADING_MODE=simulation
ENABLE_LIVE_TRADING=false

# StocksTrader API (for live/simulation trading)
STOCKSTRADER_API_KEY=your_api_key_here
STOCKSTRADER_ACCOUNT_ID=your_account_id_here

# Risk Management
MAX_POSITION_SIZE=1000
MAX_RISK_PERCENT=2.0
DEFAULT_STOP_LOSS_PERCENT=3.0
DEFAULT_TAKE_PROFIT_PERCENT=6.0

# Optional: Enhanced News Coverage
NEWS_API_KEY=your_newsapi_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### Trading Modes

| Mode | Description | Market Data | Trading |
|------|-------------|-------------|---------|
| **Demo** | Testing only | Simulated | Simulated |
| **Simulation** | Real analysis | Real-time | Simulated |
| **Live** | Real trading | Real-time | **REAL MONEY** |

## 🎯 Usage Examples

### Single Stock Analysis
```bash
# Comprehensive analysis of Tesla
python live_trading_main.py TSLA

# Analyze Apple with simulation mode
python live_trading_main.py AAPL --mode simulation
```

### Watchlist Analysis
```bash
# Analyze multiple tech stocks
python live_trading_main.py --watchlist TSLA AAPL GOOGL MSFT NVDA

# Analyze popular stocks
python live_trading_main.py --watchlist SPY QQQ DIA TSLA AMZN
```

### Original System (for comparison)
```bash
# Run the original system
python main.py
```

## 📊 Analysis Output

The system provides comprehensive analysis including:

### Market Data Analysis
- Current price and daily change
- Real-time bid/ask spreads
- Volume patterns and anomalies
- Market liquidity assessment

### News Sentiment Analysis
- Overall sentiment score (-1.0 to +1.0)
- Recent headlines and their impact
- Sentiment breakdown (positive/negative/neutral)
- Trading implications based on news

### Technical Analysis
- **RSI**: Current value and signal (overbought/oversold/neutral)
- **MACD**: MACD line, signal line, and histogram
- **Bollinger Bands**: Price position relative to bands
- **Moving Averages**: Price position vs. SMA 20/50/200
- **Support/Resistance**: Key price levels
- **Chart Patterns**: Detected patterns with confidence levels

### Trading Signals
- Combined signal strength (bullish/bearish/neutral)
- Entry and exit price targets
- Position sizing recommendations
- Risk management suggestions

## 🛡️ Risk Management

### Built-in Safety Features
- **Position Sizing**: Maximum 10% of capital per trade
- **Stop Losses**: Automatic placement 3-5% below entry
- **Take Profits**: Technical-based profit targets
- **Daily Limits**: Maximum trades per day
- **Market Hours**: Trading only during market hours
- **Risk Percentage**: Maximum 2% risk per trade

### Manual Risk Controls
```env
# Customize risk parameters in .env
MAX_POSITION_SIZE=1000        # Maximum dollars per position
MAX_RISK_PERCENT=2.0          # Maximum risk per trade
DAILY_LOSS_LIMIT=5.0          # Daily loss limit percentage
MAX_TRADES_PER_DAY=10         # Maximum trades per day
```

## 🔧 API Integration

### StocksTrader API
- Real-time quotes and market data
- Order placement and management
- Account information and positions
- Trade execution and confirmation

### News APIs (Optional)
- **NewsAPI**: Financial news aggregation
- **Alpha Vantage**: Market news and sentiment
- **Polygon.io**: Real-time news feed

### Technical Analysis
- **Yahoo Finance**: Historical price data
- **Custom Indicators**: RSI, MACD, Bollinger Bands
- **Pattern Recognition**: Automated chart pattern detection

## 📈 Performance Monitoring

### Trade Logging
- All trades logged with timestamp
- Performance metrics tracked
- Risk metrics calculated
- P&L tracking and analysis

### System Metrics
- Analysis duration and efficiency
- API response times
- Error rates and handling
- Daily/weekly performance summaries

## 🚨 Important Warnings

### Live Trading Risks
- **Real Money**: Live mode uses real money for trades
- **Market Risk**: All trading involves risk of loss
- **System Risk**: Technical failures can cause losses
- **Regulatory Risk**: Ensure compliance with local regulations

### Recommendations
1. **Start Small**: Begin with small position sizes
2. **Test Thoroughly**: Use demo/simulation modes extensively
3. **Monitor Closely**: Watch your trades actively
4. **Set Limits**: Use appropriate risk management settings
5. **Stay Informed**: Keep up with market conditions

## 🔄 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Live Trading System                      │
├─────────────────────────────────────────────────────────────┤
│  🤖 AI Agents                                               │
│  ├── Financial Market Analyst                               │
│  └── Strategic Stock Trader                                 │
├─────────────────────────────────────────────────────────────┤
│  📊 Data Sources                                            │
│  ├── Yahoo Finance (Historical data)                        │
│  ├── StocksTrader API (Real-time quotes)                    │
│  ├── News APIs (Market sentiment)                           │
│  └── Technical Indicators (Chart analysis)                  │
├─────────────────────────────────────────────────────────────┤
│  🛡️ Risk Management                                         │
│  ├── Position Sizing                                        │
│  ├── Stop Loss/Take Profit                                  │
│  ├── Daily Limits                                           │
│  └── Market Hours Control                                   │
├─────────────────────────────────────────────────────────────┤
│  🔄 Execution Engine                                        │
│  ├── Order Management                                       │
│  ├── Trade Execution                                        │
│  ├── Position Monitoring                                    │
│  └── Performance Tracking                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🆘 Troubleshooting

### Common Issues

#### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Pull the model if not available
ollama pull deepseek-r1:8b
```

#### API Key Issues
```bash
# Check your .env file
cat .env | grep API

# Verify API keys are correctly set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('STOCKSTRADER_API_KEY'))"
```

#### Trading Mode Issues
```bash
# Check current trading mode
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TRADING_MODE'))"

# Override trading mode
python live_trading_main.py TSLA --mode simulation
```

### Error Messages

| Error | Solution |
|-------|----------|
| "STOCKSTRADER_API_KEY environment variable is required" | Add API key to .env file |
| "Ollama connection failed" | Start Ollama server: `ollama serve` |
| "Model not found" | Pull model: `ollama pull deepseek-r1:8b` |
| "Market is closed" | Disable market hours check or trade during market hours |
| "Daily trading limit reached" | Increase limit or wait for next day |

## 📞 Support

### Documentation
- Check the `live_trading_env_template.txt` for configuration options
- Review the error messages for specific guidance
- Monitor the system logs for detailed information

### Community
- Report issues on GitHub
- Join the discussion forums
- Share your trading strategies and results

## 🎉 What's New

### Version 2.0 Features
- ✅ Real-time news sentiment analysis
- ✅ Advanced technical chart analysis
- ✅ Multi-timeframe analysis
- ✅ Pattern recognition system
- ✅ Enhanced risk management
- ✅ Watchlist analysis mode
- ✅ Comprehensive logging
- ✅ Live trading capabilities

### Coming Soon
- 🔜 Portfolio optimization
- 🔜 Backtesting framework
- 🔜 Email/SMS notifications
- 🔜 Web dashboard
- 🔜 Machine learning models
- 🔜 Options trading support

---

## ⚠️ Disclaimer

This software is for educational and informational purposes only. Trading stocks involves risk of loss. Past performance does not guarantee future results. The creators are not responsible for any financial losses incurred through the use of this system. Always consult with a qualified financial advisor before making investment decisions.

**USE AT YOUR OWN RISK** 