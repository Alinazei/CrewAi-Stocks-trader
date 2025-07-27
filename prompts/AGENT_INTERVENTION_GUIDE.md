# 🔄 Agent Intervention System Guide

## Overview
The Agent Intervention System allows you to **queue new tasks** and **interrupt running agent teams** to add priority tasks without stopping the current execution.

## 🎯 Key Features

### ✅ **Non-Disruptive Intervention**
- Current team execution continues uninterrupted
- New tasks are queued for immediate execution after current team completes
- No data loss or process interruption

### 🕒 **Real-Time Task Queuing**
- Add high-priority tasks during team execution
- View all queued tasks with timestamps
- Automatic processing of queued tasks

### 💡 **Smart Execution Flow**
- Queued tasks execute automatically after current team completes
- Maintains conversation history and context
- Seamless integration with existing workflow

## 📋 Commands

### `!interrupt`
**Queue a new priority task during team execution**

**Usage:**
```
!interrupt
```

**What happens:**
1. If team is running: Prompts for new task to queue
2. If no team running: Shows message to use normal commands
3. Queued task executes after current team completes

**Example:**
```
👤 You: !interrupt
⚠️ INTERRUPTION REQUEST - Crew is currently running
│ Current execution will complete, then new task will be queued
│ Enter your new priority task:
➤ Analyze NVDA earnings impact immediately

✅ Task queued: Analyze NVDA earnings impact immediately
│ Will execute after current team completes
```

### `!queue`
**Show all queued tasks**

**Usage:**
```
!queue
```

**Example Output:**
```
📋 QUEUED TASKS (2)
│ 1. [HIGH] Analyze NVDA earnings impact immediately
│    Queued at: 14:35:22
│ 2. [HIGH] Review portfolio risk after market close
│    Queued at: 14:36:45
│
Use '@team' to process queued tasks
```

## 🚀 Usage Scenarios

### **Scenario 1: Urgent Market News**
```
# Team is analyzing your portfolio
@team comprehensive portfolio analysis

# Breaking news about TSLA
!interrupt
➤ URGENT: Analyze TSLA price drop impact on portfolio

# Current analysis continues, TSLA analysis queued
```

### **Scenario 2: Multiple Priority Tasks**
```
# Add multiple urgent tasks
!interrupt
➤ Check AAPL pre-market sentiment

!interrupt  
➤ Analyze Fed announcement impact

!queue  # Check what's queued
```

### **Scenario 3: Market Hours Changes**
```
# During market hours analysis
@team monitor real-time market sentiment

# Market closes unexpectedly
!interrupt
➤ Switch to after-hours analysis mode
```

## 🔧 Technical Details

### **Queue Structure**
```python
{
    'task': 'Task description',
    'timestamp': datetime.now(),
    'priority': 'high'  # All interrupted tasks are high priority
}
```

### **Execution Flow**
1. **Team Starts**: `crew_running = True`
2. **User Interrupts**: Task added to `queued_tasks[]`
3. **Team Completes**: Processes all queued tasks automatically
4. **Queue Cleared**: `crew_running = False`

### **Error Handling**
- Keyboard interrupts (Ctrl+C) are handled gracefully
- Failed tasks don't block queue processing
- System state is always restored after exceptions

## 🎯 Best Practices

### **When to Use Interrupts**
- ✅ Breaking market news
- ✅ Urgent portfolio changes needed
- ✅ Time-sensitive analysis requests
- ✅ Priority shifts during execution

### **When NOT to Use Interrupts**
- ❌ Non-urgent questions
- ❌ General information requests
- ❌ Tasks that can wait
- ❌ Routine analysis

### **Tips for Effective Interruption**
1. **Be Specific**: "Analyze TSLA earnings impact" vs "Check TSLA"
2. **Use Context**: Reference current market conditions
3. **Priority Order**: Most urgent tasks first
4. **Check Queue**: Use `!queue` to see what's pending

## 📊 Integration with Market Hours

The intervention system works seamlessly with market hours awareness:

### **Market Open**
- Interrupts for real-time analysis
- Live trading decisions
- Breaking news reactions

### **Market Closed**
- Research and planning tasks
- After-hours sentiment analysis
- Strategy preparation

## 🔄 Workflow Examples

### **Complete Workflow**
```
1. Start team analysis:
   @team analyze current market conditions

2. Breaking news appears:
   !interrupt
   ➤ Analyze Fed rate decision impact

3. Check what's queued:
   !queue

4. Team completes automatically:
   ✅ Original analysis complete
   🔄 Processing queued tasks...
   ✅ Fed analysis complete
```

### **Multiple Interventions**
```
@team portfolio optimization

# First interrupt
!interrupt
➤ Check AAPL earnings premarket

# Second interrupt  
!interrupt
➤ Analyze sector rotation signals

# Both execute after main team completes
```

## 🛠️ Advanced Features

### **Automatic Queue Processing**
- No manual intervention needed
- Processes all queued tasks in order
- Maintains conversation context

### **State Management**
- Thread-safe execution
- Proper cleanup on errors
- Consistent system state

### **Context Preservation**
- All analysis maintains conversation history
- Recommendations build on previous work
- Seamless user experience

## 🔍 Troubleshooting

### **Common Issues**
1. **"No crew running"**: Use normal commands instead of `!interrupt`
2. **Queue not processing**: Check for system errors in team execution
3. **Tasks not queuing**: Ensure you're typing task description after prompt

### **Debug Commands**
```
!status  # Check system status
!queue   # View current queue
!clear   # Clear conversation (doesn't affect queue)
```

## 📈 Performance Impact

### **Minimal Overhead**
- Queue operations are lightweight
- No impact on team execution speed
- Efficient memory usage

### **Scalability**
- Handles multiple queued tasks efficiently
- No limit on queue size (reasonable use)
- Fast processing of queued items

---

## 🎉 Summary

The Agent Intervention System provides **professional-grade task management** for your trading agents, allowing you to:

- **React quickly** to market changes
- **Maintain workflow continuity** 
- **Prioritize urgent tasks** without disruption
- **Scale your analysis** efficiently

Perfect for active traders who need responsive, intelligent assistance that adapts to rapidly changing market conditions! 