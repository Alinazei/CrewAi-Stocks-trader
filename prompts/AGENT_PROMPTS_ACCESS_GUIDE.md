# Agent Documentation Access Guide - Updated System

## 🎯 **AGENT ACCESS TO DOCUMENTATION**

This guide explains how AI agents in our **optimized 8-agent trading system** can access and use the documentation in the `prompts` directory to get the latest API guidance and system information.

## ✅ **UPDATED DOCUMENTATION ACCESS**

### **1. Direct Documentation Integration**
**Status**: ✅ **DOCUMENTATION BUILT INTO AGENTS**

With our **optimized system**, all agents have **direct access** to essential documentation:

#### **Integrated Documentation:**
- ✅ **StocksTrader API schema** built into agent prompts
- ✅ **Tool usage guidance** embedded in agent configurations
- ✅ **Trading workflow** integrated into task descriptions
- ✅ **Best practices** included in agent backstories

#### **Key Benefits:**
- **No dependency** on external file reading
- **Faster execution** with integrated knowledge
- **Consistent information** across all agents
- **Production-stable** documentation access

### **2. Essential Documentation Files**
**Status**: ✅ **STREAMLINED AND FOCUSED**

Our documentation is now **optimized** for the 8-agent system:

#### **Core Files for Trading:**
- ✅ `STOCKSTRADER_TOOL_GUIDE.md` - Complete API reference
- ✅ `SYSTEM_OVERVIEW.md` - 8-agent system architecture
- ✅ `UPDATED_AGENT_GUIDE.md` - Agent roles and tools
- ✅ `ALL_TASKS_VERIFICATION.md` - Task configuration verification

## 📋 **CRITICAL API INFORMATION FOR ALL AGENTS**

### **1. StocksTrader API Schema - BUILT INTO AGENTS**
**Purpose**: Correct API usage for all trading operations
**Access**: **Integrated into all trading agents**

#### **Essential Order Sides:**
```
✅ CORRECT ORDER SIDES:
- "buy" - Open long position (bet on price increase)
- "sell" - Open short position (bet on price decrease) 
- "sell_short" - Open short position (explicit short selling)
- "buy_to_cover" - Close short position

✅ POSITION CLOSING:
- Use close_position(deal_id) for ANY position closure
- DO NOT use order sides to close positions

❌ UNSUPPORTED SIDES:
- "close", "short" - These cause API errors
```

#### **Key API Functions:**
```
Account Management:
- get_account_information() - Account status
- get_current_positions() - Current positions

Order Management:
- place_market_order(symbol, side, quantity) - Place orders
- close_position(deal_id) - Close positions
- modify_deal(deal_id, stop_loss, take_profit) - Modify deals
- cancel_order(order_id) - Cancel orders

Market Data:
- get_real_time_quote(symbol) - Live quotes
- check_market_status() - Market hours
```

### **2. Agent Roles and Responsibilities - OPTIMIZED SYSTEM**
**Purpose**: Clear role definition for 8 specialized agents
**Access**: **Built into agent configurations**

#### **8-Agent System:**
```
📊 @analyst      → Stock analysis and research
📰 @news         → News and sentiment analysis
⚠️ @risk         → Risk assessment and management
💼 @portfolio    → Portfolio optimization
💰 @trader       → Trading execution
📈 @performance  → Performance tracking
🎯 @order_leader → Order management coordination
🔍 @scan         → Stock discovery and opportunities
🤝 @team         → ALL AGENTS COLLABORATE
```

### **3. Trading Workflow - STREAMLINED PROCESS**
**Purpose**: Efficient collaboration between agents
**Access**: **Integrated into task workflows**

#### **Sequential Process:**
```
1. 📊 Analyst → Market Analysis
2. 📰 News → Sentiment Analysis  
3. ⚠️ Risk → Risk Assessment
4. 💼 Portfolio → Portfolio Optimization
5. 💰 Trader → Trading Decisions
6. 📈 Performance → Performance Analysis
7. 🎯 Order Leader → Final Coordination
8. 🔍 Scan → Opportunity Discovery
```

## 🚀 **AGENT DOCUMENTATION BEST PRACTICES**

### **1. API Usage Guidelines**
```
✅ DO:
- Use correct order sides: buy, sell, sell_short, buy_to_cover
- Close positions with close_position(deal_id)
- Validate market hours before trading
- Include proper error handling

❌ DON'T:
- Use unsupported sides: "close", "short"
- Try to close positions with order sides
- Trade outside market hours without checking
- Make assumptions about API behavior
```

### **2. Agent Collaboration**
```
✅ DO:
- Use @team for complex decisions
- Pass information between specialized agents
- Coordinate through Order Management Leader
- Cross-validate important recommendations

❌ DON'T:
- Work in isolation for major decisions
- Duplicate analysis across agents
- Skip risk assessment for trades
- Ignore other agents' expertise
```

### **3. Error Handling**
```
✅ DO:
- Retry failed API calls with backoff
- Validate inputs before API calls
- Log errors for debugging
- Provide fallback strategies

❌ DON'T:
- Ignore API errors
- Continue with invalid data
- Skip validation steps
- Assume all calls succeed
```

## 📊 **DOCUMENTATION ACCESS METHODS**

### **Method 1: Built-in Knowledge (Primary)**
- **Status**: ✅ **ACTIVE** - All agents have integrated documentation
- **Benefits**: Fast, reliable, consistent information
- **Usage**: Automatic - no special commands needed

### **Method 2: Team Collaboration (Secondary)**
- **Status**: ✅ **ACTIVE** - Agents can consult each other
- **Benefits**: Cross-validation, multiple perspectives
- **Usage**: Use @team command for complex questions

### **Method 3: Error Messages (Fallback)**
- **Status**: ✅ **ACTIVE** - API provides helpful error messages
- **Benefits**: Real-time feedback on incorrect usage
- **Usage**: Automatic when API calls fail

## 💡 **QUICK REFERENCE COMMANDS**

### **For Users:**
```
@analyst "Analyze AAPL" → Get stock analysis
@team "Should I buy TSLA?" → Get team recommendation
!status → Check system status
!scan → Find opportunities
```

### **For Agents (Internal):**
```
get_account_information() → Account status
place_market_order("AAPL", "buy", 100) → Buy 100 AAPL
close_position("12345") → Close position by deal ID
check_market_status() → Verify market hours
```

## 🎯 **SUMMARY**

**✅ DOCUMENTATION ACCESS - OPTIMIZED**

Our **8-agent trading system** now features:
- **Integrated documentation** built into every agent
- **Consistent API knowledge** across all agents
- **Streamlined access** without file dependencies
- **Production-ready** documentation system

**No external file reading required - all agents have built-in access to essential trading documentation!** 🚀 