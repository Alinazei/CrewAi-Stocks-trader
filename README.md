# CrewAI Stock Trader Agents

An intelligent stock trading system powered by CrewAI that can analyze stocks and execute real trades through the StocksTrader API. **NEW**: Features persistent goal-oriented trading that continues daily until targets are achieved!

## Features

- **🎯 Persistent Goal-Oriented Trading**: Set targets like "increase portfolio gains to 10%" and agents trade daily until achieved
- **📊 Real-time Progress Monitoring**: Track progress toward goals with detailed reports and milestone celebrations
- **🔄 Autonomous Trading Loops**: Background trading sessions that continue until goals are completed
- **Intelligent Analysis**: Uses both Yahoo Finance and StocksTrader API for comprehensive stock analysis
- **Real Trading**: Executes actual buy/sell orders through StocksTrader API
- **Risk Management**: Built-in safety checks, position sizing, and risk controls
- **Simulation Mode**: Test strategies without real money
- **Multi-Agent System**: 6 specialized agents working together (analyst, trader, risk, portfolio, news, performance)

## Architecture

### Agents (6 Specialized AI Agents)
- **Analyst Agent**: Performs comprehensive stock analysis using multiple data sources
- **Trader Agent**: Executes trading decisions with proper risk management
- **Risk Management Agent**: Assesses portfolio risks and position sizing
- **Portfolio Management Agent**: Optimizes portfolio allocation and diversification
- **News Sentiment Agent**: Analyzes news sentiment and social media buzz (Twitter integration)
- **Performance Tracking Agent**: Monitors and reports on trading performance

### 🎯 Persistent Trading System
- **Goal Tracker**: Creates and monitors trading goals with SQLite persistence
- **Persistent Trading Loop**: Background threads that trade daily until goals achieved
- **Progress Monitor**: Real-time progress tracking with milestone notifications
- **Goal Completion System**: Automatic goal detection and celebration

### Tools
- **Yahoo Finance Tool**: Historical data and fundamental analysis
- **StocksTrader API Tools**: Real-time quotes, account management, order execution
- **Twitter API Tools**: Social sentiment analysis and trend monitoring
- **Autonomous Improvement Tools**: Self-learning and strategy adaptation
- **Safety Checks**: Risk management and position sizing

## Setup

### 1. Install Dependencies

#### Quick Installation (Recommended)
Use our automated installer for the best experience:

```bash
# Basic installation (all core features)
python install_dependencies.py basic

# Enhanced installation (adds TradingView-level chart analysis)
python install_dependencies.py enhanced

# Development installation (adds development tools)
python install_dependencies.py dev

# Full installation (everything)
python install_dependencies.py full

# Upgrade all packages
python install_dependencies.py upgrade
```

#### Manual Installation Options

**Basic Requirements (Core Features):**
```bash
pip install -r requirements.txt
```

**Enhanced Chart Analysis (Recommended for Professional Trading):**
```bash
pip install -r requirements.txt
pip install -r requirements-enhanced.txt
```

**Development Environment:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 🚀 Enhanced Chart Analysis Features

The enhanced installation unlocks **TradingView-level professional capabilities**:

- ✅ **TradingView-style Interactive Charts** - Professional chart visualization (lightweight-charts)
- ✅ **Professional Financial Data** - Alpha Vantage API integration (FREE tier available)
- ✅ **100+ Advanced Technical Indicators** - TA-Lib + ta + finta libraries
- ✅ **Professional Pattern Recognition** - Advanced candlestick patterns
- ✅ **Multi-timeframe Analysis** - 1min to weekly timeframes
- ✅ **Alternative Technical Analysis** - Always-working fallback libraries
- ✅ **Financial Data Manipulation** - Advanced data processing tools
- ✅ **Professional Market Scanning** - Sector-based opportunity detection

**Platform-Specific Notes:**
- **Windows**: TA-Lib may require manual installation - [download here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
- **macOS**: Run `brew install ta-lib` before installing requirements
- **Linux**: Run `sudo apt-get install libta-lib-dev` before installing

**Troubleshooting:**
- If you encounter `ModuleNotFoundError: No module named 'tools'`, make sure to run from the project root directory
- For package installation issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Alternative packages (`ta`, `finta`) provide fallback if TA-Lib installation fails

### 2. Choose Your AI Model

#### Option A: Use Ollama (Local AI - Recommended)
**Advantages**: Free, private, runs offline, excellent reasoning with DeepSeek-R1:8b

**Quick Setup:**
```bash
python setup_ollama.py
```

This will:
- Guide you through Ollama installation
- Download DeepSeek-R1:8b model (~4.9GB)
- Configure your environment automatically
- Start the system in demo mode

**Manual Setup:**
1. Install Ollama from [ollama.com](https://ollama.com)
2. Download DeepSeek-R1:8b: `ollama pull deepseek-r1:8b`
3. Start Ollama: `ollama serve`
4. Create `.env` file with:
   ```env
   OLLAMA_MODEL=deepseek-r1:8b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

#### Option B: Use Groq API (Cloud-based)
**Advantages**: No local setup required, faster startup

Create a `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key
```

### 3. Live Trading Setup (Optional)

**For demo mode**: Skip this step - the system will use simulated data

**For real trading**, you can use either StocksTrader or Alpaca:

#### Option A: StocksTrader API
1. Sign up at [StocksTrader](https://stockstrader.com)
2. Get your API key from the dashboard
3. Add to `.env` file:
   ```env
   STOCKSTRADER_API_URL=https://api.stockstrader.com
   STOCKSTRADER_API_KEY=your_stockstrader_api_key
   STOCKSTRADER_ACCOUNT_ID=your_account_id
   PRIMARY_BROKER=stockstrader
   ENABLE_LIVE_TRADING=true
   ```

#### Option B: Alpaca Trading
1. Sign up at [Alpaca](https://alpaca.markets)
2. Get your API credentials from the dashboard
3. Add to `.env` file:
   ```env
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_SECRET_KEY=your_alpaca_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets  # For paper trading
   # ALPACA_BASE_URL=https://api.alpaca.markets      # For live trading
   PRIMARY_BROKER=alpaca
   ENABLE_LIVE_TRADING=true
   ```

**⚠️ IMPORTANT**: Start with paper trading before live trading!

## Usage

### 💬 Interactive Chat Interface (NEW!)
```bash
# 🚀 Agent Zero Style Chat (RECOMMENDED)
python agent_zero_chat.py

# Simple conversational chat
python simple_chat.py

# Advanced chat interface
python interactive_chat.py
```

**🚀 Agent Zero Style Chat Features:**
- **Real-time streamed responses** - See agents thinking in real-time
- **Interrupt capability** - Press Ctrl+C to stop and give new instructions
- **Agent switching** - Use @analyst or @trader to switch between agents
- **Conversation context** - Agents remember your conversation history
- **Colored terminal output** - Beautiful, organized chat interface

**Chat with your AI agents using natural language:**
- "analyze TSLA" - Get comprehensive stock analysis
- "what do you think about AAPL?" - Get AI opinion
- "should I buy NVDA?" - Trading recommendation
- "show my positions" - View current holdings
- "what's the market sentiment?" - Market overview

**🎯 NEW: Persistent Goal-Oriented Trading:**
- "@team increase portfolio gains to 10%" - Start persistent trading toward goal
- "@team make $500 daily profit" - Set daily profit targets
- "@team reach $50,000 portfolio value" - Set portfolio value goals
- "!goals" - Monitor active trading goals
- "!progress" - View detailed progress reports
- "!stop-goal <goal_id>" - Stop trading for specific goal

### Quick Start with Ollama (Recommended)
```bash
# 1. Run the setup script
python setup_ollama.py

# 2. Start trading (demo mode)
python main.py

# 3. Or start the Agent Zero style chat (RECOMMENDED)
python agent_zero_chat.py
```

### Basic Usage
```bash
python
```

By default, this will analyze and potentially trade Tesla (TSLA) stock.

**First run with Ollama**: May take 30-60 seconds as the model loads into memory.

### Trading Different Stocks
Edit `main.py` to change the stock:
```python
if __name__ == "__main__":
    run("AAPL")    # For Apple
    run("GOOGL")   # For Google
    run("MSFT")    # For Microsoft
```

### Safety Modes

#### Demo Mode (Default)
- No StocksTrader API credentials required
- Uses simulated account data and quotes
- Perfect for testing AI analysis and reasoning
- No real money involved

#### Simulation Mode
- `ENABLE_LIVE_TRADING=false` (with API credentials)
- Analyzes stocks with real data but simulates trades
- Safe for testing strategies with real market data
- No real money involved

#### Live Trading Mode
- `ENABLE_LIVE_TRADING=true`
- **WARNING**: This will place real orders with real money
- Ensure you understand the risks
- Start with small position sizes

### Live Trading Features

#### Real-Time Market Data
- **Live quotes**: Real-time bid/ask/last prices
- **Account information**: Live balance, equity, buying power
- **Position tracking**: Real-time P&L and position updates
- **Order execution**: Market and limit orders with real money

#### Supported Brokers
- **StocksTrader**: Full-featured API with advanced order types
- **Alpaca**: Commission-free trading with paper trading support(not yet)

#### Order Types Available
- **Market Orders**: Execute immediately at current market price
- **Limit Orders**: Execute only at specified price or better
- **Stop Loss Orders**: Automatic risk management
- **Take Profit Orders**: Automatic profit taking
- **Good Till Cancelled (GTC)**: Orders stay active until filled or cancelled

#### Account Management
- **Balance monitoring**: Real-time account balance tracking
- **Position management**: View and manage open positions
- **Order history**: Complete trading history and performance analytics
- **Risk metrics**: Real-time risk assessment and drawdown monitoring

## 🎯 Persistent Goal-Oriented Trading (NEW!)

The system now features persistent trading that continues daily until your goals are achieved!

### How It Works

1. **Set Your Goal**: Use natural language to set trading targets
   ```
   @team increase portfolio gains to 10%
   @team make $500 daily profit
   @team reach $50,000 portfolio value
   ```

2. **Automatic Goal Creation**: System parses your request and creates a trackable goal
   ```
   🎯 Goal Created: goal_20241201_143022
   Target: 10% portfolio gains
   Status: ACTIVE
   Daily Trading: ENABLED
   ```

3. **Persistent Trading Loop**: Background system trades daily during market hours
   - Monitors market conditions
   - Executes profitable trades
   - Tracks progress toward goal
   - Continues until target achieved

4. **Progress Monitoring**: Real-time tracking with milestone celebrations
   ```
   Progress: 7.2% (72% complete)
   Daily Average: 1.2% gain
   Estimated Completion: 3 days
   Win Rate: 85%
   Total Profit: $1,247.50
   ```

### Goal Types Supported

- **Portfolio Gains**: "increase portfolio gains to X%"
- **Daily Profits**: "make $X daily profit"
- **Portfolio Value**: "reach $X portfolio value"
- **Risk Reduction**: "reduce portfolio risk by X%"
- **Custom Goals**: Flexible goal creation system

### Monitoring Commands

```bash
# View all active goals
!goals

# View detailed progress reports
!progress

# Stop trading for specific goal
!stop-goal goal_20241201_143022

# View system status
!status
```

### Example Workflow

```bash
# 1. Start the Agent Zero chat
python agent_zero_chat.py

# 2. Set a goal
@team increase portfolio gains to 10%

# 3. Monitor progress
!goals
!progress

# 4. System trades daily automatically until goal achieved
# 5. Celebration when goal is completed! 🎉
```

### Features

- **📊 Real-time Progress Tracking**: Know exactly how close you are to your goals
- **🎉 Milestone Celebrations**: Get notified at 25%, 50%, 75%, 90%, 95%, and 100% completion
- **📈 Trend Analysis**: Understand if you're accelerating, steady, or need strategy adjustment
- **🏆 Multiple Goals**: Work toward several objectives simultaneously
- **💾 Persistent Storage**: Goals survive system restarts
- **🔄 Daily Trading**: Automated trading sessions during market hours
- **📱 Smart Recommendations**: AI-powered suggestions based on progress

### Demo

Try the persistent trading demo:
```bash
python demo_persistent_trading.py
```

### 🎯 Live Trading with Persistent Goals

The persistent trading system works seamlessly with live trading:

```bash
# Start live trading toward a goal
@team increase portfolio gains to 15%

# System will:
# 1. Create trackable goal
# 2. Start persistent trading loop
# 3. Execute real trades during market hours
# 4. Track real P&L toward goal
# 5. Celebrate when goal achieved with real profits!
```

**Live Trading Goal Examples:**
- `@team increase portfolio gains to 15%` - Real portfolio growth
- `@team make $100 daily profit` - Real daily profit targets
- `@team reach $25,000 portfolio value` - Real portfolio value goals

### Performance Analytics

The system provides comprehensive performance tracking for live trading:

```
📊 RISK-ADJUSTED PERFORMANCE METRICS
==================================================

📈 RETURN METRICS:
• Total Return: 14.55%
• Annualized Return: 20.03%

⚠️ RISK METRICS:
• Volatility: 30.71%
• Maximum Drawdown: -26.15%
• VaR (95%): -2.91%
• CVaR (95%): -3.62%

🎯 RISK-ADJUSTED RATIOS:
• Sharpe Ratio: 0.555
• Sortino Ratio: 1.013
• Calmar Ratio: 0.766

📊 PERFORMANCE RATING:
• Sharpe Ratio: FAIR
• Drawdown Control: HIGH RISK

🎯 OVERALL ASSESSMENT:
MODERATE - Room for improvement in risk management
```

## Risk Management

### Built-in Safety Features
- **Position Sizing**: Maximum 20% of capital per position
- **Stop Losses**: Automatic 2% stop loss calculation
- **Take Profits**: 2:1 risk-reward ratio targets
- **Spread Checking**: Avoids trading when spreads are too wide
- **Parameter Validation**: Ensures all order parameters are valid

### Configuration
Adjust risk parameters in `.env`:
```env
MAX_POSITION_SIZE=500      # Reduce position size
MAX_RISK_PERCENT=1.0       # Reduce risk per trade
```

### 🔒 Live Trading Safety & Best Practices

When using live trading with real money, follow these safety guidelines:

#### Pre-Trading Checklist
- [ ] Start with **paper trading** to test strategies
- [ ] Set appropriate **position sizes** (start small)
- [ ] Configure **stop losses** and **take profits**
- [ ] Test with **demo goals** before live goals
- [ ] Monitor **account balance** and **risk metrics**

#### Recommended Settings for Live Trading
```env
# Conservative live trading settings
MAX_POSITION_SIZE=100        # Start with small positions
MAX_RISK_PERCENT=0.5         # Risk only 0.5% per trade
ENABLE_STOP_LOSS=true        # Always use stop losses
STOP_LOSS_PERCENT=2.0        # 2% stop loss
TAKE_PROFIT_RATIO=2.0        # 2:1 risk-reward ratio
```

#### Safety Features
- **Position sizing**: Automatic calculation based on account size
- **Risk limits**: Per-trade and portfolio risk limits
- **Stop losses**: Automatic stop loss orders
- **Spread checking**: Avoids trading when spreads are too wide
- **Market hours**: Only trades during regular market hours
- **Balance monitoring**: Real-time account balance tracking

#### Live Trading Workflow
1. **Start with paper trading**: Test strategies without risk
2. **Set conservative goals**: Start with smaller targets
3. **Monitor closely**: Watch the first few trades carefully
4. **Adjust settings**: Fine-tune based on performance
5. **Scale gradually**: Increase position sizes slowly

#### Emergency Commands
```bash
# Stop all trading immediately
!stop-goal <goal_id>

# View current positions
!status

# Check account balance
show my positions

# View recent trades
!progress
```

#### When to Stop Trading
- **High drawdown**: If losses exceed comfort level
- **Consecutive losses**: Multiple losing trades in a row
- **Market volatility**: During extreme market conditions
- **Technical issues**: Any system or API problems
- **Emotional stress**: If trading causes anxiety

## API Integration

### StocksTrader API Features Used
- Account information and balance
- Real-time quotes (bid/ask/last)
- Order placement (market and limit orders)
- Position management
- Order cancellation
- Risk management (stop loss/take profit)

### Available Order Types
- **Market Orders**: Execute immediately at current price
- **Limit Orders**: Execute only at specified price or better
- **Stop Loss**: Automatic risk management
- **Take Profit**: Automatic profit taking

## 💬 Interactive Chat Interface

### Two Chat Modes Available

#### 1. Simple Chat (`simple_chat.py`)
- **Easy to use**: Natural language interface with your existing crew
- **Quick setup**: Uses your current agent configuration
- **Perfect for**: General stock analysis and basic interaction

```bash
python simple_chat.py
```

**Example conversation:**
```
💬 You: analyze TSLA
🤖 AI Trading Team: [Comprehensive TSLA analysis with recommendations]

💬 You: what do you think about AAPL?
🤖 AI Trading Team: [AI opinion on Apple stock with technical analysis]

💬 You: should I buy NVDA?
🤖 AI Trading Team: [Trading recommendation with risk assessment]
```

#### 2. Advanced Chat (`interactive_chat.py`)
- **Full featured**: Specialized agents for different types of queries
- **Advanced routing**: Commands automatically go to the right agent
- **Trading capabilities**: Execute trades through natural language

```bash
python interactive_chat.py
```

**Example conversation:**
```
💬 You: buy 100 shares of AAPL
🤖 AI Agent: [Checks balance, analyzes AAPL, executes trade with confirmations]

💬 You: show my positions
🤖 AI Agent: [Displays current portfolio with P&L]

💬 You: what's the market sentiment?
🤖 AI Agent: [Provides market overview with sentiment analysis]
```

### Natural Language Commands

The system supports natural language commands:

**Analysis Commands:**
- "analyze [SYMBOL]"
- "what do you think about [SYMBOL]?"
- "should I buy/sell [SYMBOL]?"
- "tell me about [SYMBOL]"

**Trading Commands:**
- "buy [QUANTITY] shares of [SYMBOL]"
- "sell [QUANTITY] shares of [SYMBOL]"
- "show my positions"
- "what are my active orders?"
- "what's my account balance?"

**Live Trading Commands:**
- "place market order to buy 100 shares of AAPL"
- "place limit order to sell 50 shares of TSLA at $250"
- "set stop loss at $180 for my NVDA position"
- "cancel all open orders"
- "show my account balance"
- "what's my buying power?"
- "show my trading history"

**🎯 Persistent Goal-Oriented Trading Commands:**
- "@team increase portfolio gains to [X]%" - Start persistent trading toward percentage goal
- "@team make $[X] daily profit" - Set daily profit targets
- "@team reach $[X] portfolio value" - Set portfolio value goals
- "!goals" - View all active trading goals
- "!progress" - View detailed progress reports with trends and recommendations
- "!stop-goal [GOAL_ID]" - Stop trading for a specific goal
- "!memory" - View agent learning and growth statistics
- "!wisdom" - Get AI wisdom and recommendations for current context

**Agent Switching Commands:**
- "@analyst" - Switch to financial analyst agent
- "@trader" - Switch to trading agent
- "@risk" - Switch to risk management agent
- "@portfolio" - Switch to portfolio management agent
- "@news" - Switch to news sentiment agent
- "@performance" - Switch to performance tracking agent
- "@team" - Activate full team collaboration mode

**Market Commands:**
- "what's the market sentiment?"
- "how's the market today?"
- "analyze watchlist TSLA,AAPL,NVDA"

### Safety Features

- **Confirmation prompts** for all trading operations
- **Risk assessment** before executing trades
- **Position size validation** based on account balance
- **Market hours checking** for safety
- **Simulation mode** for testing without real money

## Example Workflow

1. **Analysis Phase**:
   - Analyst agent fetches data from Yahoo Finance
   - Gets real-time quotes from StocksTrader API
   - Performs technical and fundamental analysis
   - Provides trading recommendation

2. **Trading Phase**:
   - Trader agent checks account balance
   - Reviews current positions
   - Validates trading parameters
   - Executes order if analysis is favorable
   - Sets stop loss and take profit

3. **Risk Management**:
   - Validates position size
   - Checks market conditions
   - Ensures proper risk-reward ratio
   - Logs all decisions for audit

## Monitoring and Logging

The system logs all trading decisions and safety checks for audit purposes. Check the console output for:
- Analysis results
- Trading decisions
- Order confirmations
- Risk management actions
- Error messages

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Verify API keys are correct
   - Check internet connection
   - Ensure API endpoints are accessible

2. **Order Placement Fails**:
   - Check account balance
   - Verify position size limits
   - Ensure market is open
   - Check if stock is tradeable

3. **Analysis Errors**:
   - Verify stock symbol is correct
   - Check if stock data is available
   - Ensure both APIs are working

### Getting Help

1. Check the console logs for error messages
2. Verify your `.env` configuration
3. Test in simulation mode first
4. Ensure you have sufficient account balance

## Disclaimer

**⚠️ IMPORTANT DISCLAIMER ⚠️**

This software is for educational and research purposes. Trading involves significant risk and you can lose money. 

- Always test in simulation mode first
- Never trade with money you can't afford to lose
- Past performance does not guarantee future results
- The authors are not responsible for any trading losses
- Use at your own risk

## License

MIT License - See LICENSE file for details
