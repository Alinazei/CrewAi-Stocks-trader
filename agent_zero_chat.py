#!/usr/bin/env python3
"""
Agent Zero Style Chat Interface for CrewAI Trading Agents
========================================================

A real-time, interactive chat interface inspired by Agent Zero that allows
direct communication with AI trading agents. Features:
- Real-time streamed responses
- Interactive terminal interface
- Direct agent communication
- Multi-agent cooperation
- Intervention capabilities
- hacking
Usage:
    python agent_zero_chat.py
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import colorama
from colorama import Fore, Back, Style

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import warnings
warnings.filterwarnings('ignore')

# Initialize colorama for colored output
colorama.init(autoreset=True)

# Import all available agents
from agents.analyst_agent import create_analyst_agent
from agents.trader_agent import create_trader_agent
from agents.risk_management_agent import create_risk_management_agent
from agents.portfolio_management_agent import create_portfolio_management_agent
from agents.news_sentiment_agent import create_news_sentiment_agent
from agents.performance_tracking_agent import create_performance_tracking_agent
from agents.order_management_leader_agent import create_order_management_leader_agent
# from agents.scan_agent import scan_agent  # REMOVED
# Import all available tasks from tasks folder
from tasks.analyse_task import get_stock_analysis
from tasks.news_sentiment_task import news_sentiment_analysis_task
from tasks.trade_task import trade_decision
from tasks.risk_management_task import risk_assessment_task
from tasks.performance_tracking_task import performance_analysis_task
from tasks.portfolio_management_task import portfolio_optimization_task
from tasks.order_management_task import order_management_task

from utils.model_config import get_llm_config
from utils.market_hours import get_market_hours_message, get_trading_recommendations, is_market_open
from utils.agent_memory import memory_system, record_experience, get_agent_wisdom
from utils.goal_tracker import goal_tracker, GoalType, GoalStatus, create_portfolio_gain_goal
from utils.persistent_trading import initialize_persistent_trading, start_persistent_trading, stop_goal_trading, get_trading_status
from utils.goal_progress_monitor import start_progress_monitoring, get_progress_report, get_goals_summary, get_goals_leaderboard
from utils.trade_executor import execute_team_recommendations, parse_recommendations
from utils.master_task_system import recognize_and_execute_master_task, get_master_tasks_status

# Import the collaborative trading crew for team functionality
# Note: Import crew only when needed to avoid startup issues

load_dotenv()

def get_default_watchlist():
    watchlist = os.getenv("DEFAULT_WATCHLIST", "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI")
    if not watchlist:
        watchlist = "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI"
    return [s.strip() for s in watchlist.split(",") if s.strip()]

# Show watchlist options to user
def show_watchlist_options():
    watchlist = get_default_watchlist()
    print(f"📋 DEFAULT WATCHLIST: {', '.join(watchlist)}")
    print("💡 Type a stock symbol or '!scan' to analyze all watchlist stocks")

class AgentZeroStyleChat:
    """Agent Zero inspired chat interface"""
    def __init__(self):
        load_dotenv()
        self.session_start = datetime.now()
        self.conversation_history = []
        self.current_agent = None
        self.interrupt_flag = False
        self.queued_tasks = []
        self.crew_running = False
        self.last_team_output = None  # Store last team collaboration output
        self.auto_execute_trades = os.getenv("AUTO_EXECUTE_TRADES", "false").lower() == "true"
        
        # Configuration
        self.trading_mode = os.getenv("TRADING_MODE", "simulation").lower()
        self.enable_live_trading = os.getenv("ENABLE_LIVE_TRADING", "false").lower() == "true"
        self.primary_broker = os.getenv("PRIMARY_BROKER", "stockstrader").lower()
        
        # Agent setup - All 9 specialized agents + team collaboration
        self.agents = {
            'analyst': create_analyst_agent(),
            'trader': create_trader_agent(),
            'risk': create_risk_management_agent(),
            'portfolio': create_portfolio_management_agent(),
            'news': create_news_sentiment_agent(),
            'performance': create_performance_tracking_agent(),
            # 'coder': coder_agent,  # Removed - not essential for core trading
            'order_leader': create_order_management_leader_agent(),
            # 'scan': scan_agent,  # REMOVED
            'team': 'collaborative_crew'  # Special team mode
        }
        
        self.current_agent_name = 'analyst'  # Default to analyst
        
        # Initialize persistent trading and goal systems
        self.persistent_trading = initialize_persistent_trading(self._run_team_collaboration)
        
        # Start progress monitoring
        start_progress_monitoring()
        
        # Set up goal completion notifications
        from utils.goal_progress_monitor import add_progress_notification_callback
        add_progress_notification_callback(self._handle_goal_notification)
        
        self._display_welcome()
    
    def _check_twitter_credentials(self):
        """Check if Twitter API credentials are configured"""
        required_keys = [
            'TWITTER_BEARER_TOKEN',
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET'
        ]
        
        for key in required_keys:
            if not os.getenv(key):
                return False
        return True
    
    def _display_welcome(self):
        """Display Agent Zero style welcome message"""
        # Clear screen for clean Agent Zero-style start
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Agent Zero style header
        print(f"{Fore.BLUE}╔{'═'*78}╗")
        print(f"{Fore.BLUE}║{' '*28}{Fore.WHITE}🤖 AGENT ZERO{' '*29}{Fore.BLUE}║")
        print(f"{Fore.BLUE}║{' '*26}{Fore.CYAN}Trading Agents{' '*27}{Fore.BLUE}║")
        print(f"{Fore.BLUE}╚{'═'*78}╝")
        
        # Status panel
        print(f"\n{Fore.GREEN}🟢 SYSTEM STATUS")
        print(f"{Fore.CYAN}├─ Trading Mode: {Fore.WHITE}{self.trading_mode.upper()}")
        print(f"{Fore.CYAN}├─ Live Trading: {Fore.WHITE}{'🟢 ENABLED' if self.enable_live_trading else '🔴 DISABLED'}")
        print(f"{Fore.CYAN}├─ Auto-Execute: {Fore.WHITE}{'🟢 ENABLED' if self.auto_execute_trades else '🔴 DISABLED'}")
        print(f"{Fore.CYAN}├─ Twitter API: {Fore.WHITE}{'🟢 CONFIGURED' if self._check_twitter_credentials() else '🔴 DEMO MODE'}")
        print(f"{Fore.CYAN}└─ Session: {Fore.WHITE}{self.session_start.strftime('%H:%M:%S')}")
        
        # Available agents
        print(f"\n{Fore.YELLOW}🤖 AGENTS ONLINE")
        print(f"{Fore.CYAN}├─ 📊 {Fore.WHITE}analyst{Fore.CYAN} - Market Analysis")
        print(f"{Fore.CYAN}├─ ⚡ {Fore.WHITE}trader{Fore.CYAN} - Trading Execution") 
        print(f"{Fore.CYAN}├─ 🛡️ {Fore.WHITE}risk{Fore.CYAN} - Risk Management")
        print(f"{Fore.CYAN}├─ 💼 {Fore.WHITE}portfolio{Fore.CYAN} - Portfolio Manager")
        print(f"{Fore.CYAN}├─ 📰 {Fore.WHITE}news{Fore.CYAN} - News & Sentiment")
        print(f"{Fore.CYAN}├─ 📈 {Fore.WHITE}performance{Fore.CYAN} - Performance Tracking")
        print(f"{Fore.CYAN}├─ 🎯 {Fore.WHITE}order_leader{Fore.CYAN} - Order Management")
        print(f"{Fore.CYAN}└─ 🌟 {Fore.WHITE}team{Fore.CYAN} - All Agents Collaboration")
        
        # Watchlist
        watchlist = os.getenv("DEFAULT_WATCHLIST", "NIO,SNDL,IGC,TLRY,UGRO,CGC,EGO,OGI")
        print(f"\n{Fore.MAGENTA}📋 WATCHLIST")
        print(f"{Fore.CYAN}└─ {Fore.WHITE}{watchlist}")
        
        # Quick usage
        print(f"\n{Fore.GREEN}💡 QUICK START")
        print(f"{Fore.WHITE}   @team Check my portfolio and optimize")
        print(f"{Fore.WHITE}   @analyst Analyze NIO technical signals") 
        print(f"{Fore.WHITE}   !scan - Quick market scan")
        print(f"{Fore.WHITE}   !tasks - Check Master Tudor's active tasks")
        
        # Master Tudor's tasks
        print(f"\n{Fore.YELLOW}👑 MASTER TUDOR'S CONTINUOUS TASKS")
        print(f"{Fore.MAGENTA}   This week make me $500 profit    {Fore.CYAN}← Trades till $500 earned")
        print(f"{Fore.MAGENTA}   Make $1000 profit today           {Fore.CYAN}← Never stops till done")
        print(f"{Fore.MAGENTA}   Increase portfolio by 20%         {Fore.CYAN}← Works continuously")
        print(f"{Fore.MAGENTA}   Generate $250 daily profit        {Fore.CYAN}← Daily persistent trading")
        
        # Footer
        print(f"\n{Fore.BLUE}{'─'*80}")
        print(f"{Fore.CYAN}Type your command or message. Press Ctrl+C to interrupt anytime.")
        print(f"{Fore.BLUE}{'─'*80}")

    
    def _print_agent_header(self, agent_name: str):
        """Print simple Agent Zero style header"""
        if agent_name == 'team':
            print(f"\n{Fore.YELLOW}Agent (Team): {Fore.WHITE}", end="")
        else:
            print(f"\n{Fore.YELLOW}Agent ({agent_name}): {Fore.WHITE}", end="")
    
    def _print_agent_footer(self):
        """Print agent footer"""
        print()
    
    def _print_user_input(self, user_input: str):
        """Print user input (Agent Zero doesn't show user input again)"""
        pass
    
    def _print_system_message(self, message: str):
        """Print system message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Fore.MAGENTA}┌─ {Fore.WHITE}⚙️  System {Fore.MAGENTA}─ {timestamp} ─┐")
        print(f"{Fore.MAGENTA}│ {Fore.WHITE}{message}")
        print(f"{Fore.MAGENTA}└─────────────────────────────────────────────────────────────────┘")
    
    def _handle_special_commands(self, user_input: str) -> bool:
        user_input = user_input.strip().lower()
        # Natural language command parsing
        if "switch to analyst" in user_input:
            self.current_agent_name = 'analyst'
            self._print_system_message("Switched to ANALYST agent")
            return True
        if "show my portfolio" in user_input or "portfolio status" in user_input:
            self.current_agent_name = 'portfolio'
            self._print_system_message("Switched to PORTFOLIO agent")
            return True
        if "scan my watchlist" in user_input or "analyze my watchlist" in user_input:
            self._scan_watchlist()
            return True
        # ... existing @ and ! command handling ...
        
        # Agent switching
        if user_input.startswith('@'):
            agent_name = user_input[1:].lower()
            if agent_name in self.agents:
                self.current_agent_name = agent_name
                self._print_system_message(f"Switched to {agent_name.upper()} agent")
                return True
            else:
                self._print_system_message(f"Unknown agent: {agent_name}")
                return True
        
        # Clear history
        elif user_input == '!clear':
            self.conversation_history = []
            os.system('cls' if os.name == 'nt' else 'clear')
            self._display_welcome()
            return True
        
        # Status
        elif user_input == '!status':
            twitter_status = "CONFIGURED" if self._check_twitter_credentials() else "DEMO MODE"
            self._print_system_message(f"""
Current Agent: {self.current_agent_name.upper()}
Trading Mode: {self.trading_mode.upper()}
Live Trading: {'ENABLED' if self.enable_live_trading else 'DISABLED'}
Primary Broker: {self.primary_broker.upper()}
Twitter API: {twitter_status}\
Conversation Length: {len(self.conversation_history)} messages
Session Duration: {datetime.now() - self.session_start}
""")
            return True
        
        # Scan watchlist
        elif user_input == '!scan' or user_input.lower() == 'scan':
            self._scan_watchlist()
            return True
        
        # Exit
        elif user_input == '!exit':
            self._print_system_message("Goodbye! Thanks for using Agent Zero Style Trading Chat!")
            return True
        
        # Master Tudor's task status
        elif user_input == '!tasks' or user_input == '!status':
            status = get_master_tasks_status()
            if status:
                self._print_system_message("👑 MASTER TUDOR'S ACTIVE TASKS")
                for task in status:
                    print(f"{Fore.CYAN}├─ 🎯 {task['description']}")
                    print(f"{Fore.CYAN}│  └─ Progress: {Fore.GREEN}{task['progress_percentage']:.1f}%")
                    print(f"{Fore.CYAN}│  └─ Current: ${task['current_progress']:.2f} / Target: ${task['target']:.2f}")
                    print(f"{Fore.CYAN}│  └─ Time left: {task['time_remaining']}")
            else:
                self._print_system_message("No active Master Tudor tasks")
            return True
        
        # Force task as Master Tudor
        elif user_input.startswith('!master '):
            task_text = user_input[8:]  # Remove '!master '
            # Add Master Tudor identifier to ensure recognition
            task_text = f"Master Tudor says: {task_text}"
            task_id = recognize_and_execute_master_task(task_text)
            if task_id:
                self._print_system_message(f"👑 Task submitted as Master Tudor: {task_id}")
            else:
                self._print_system_message("Failed to parse task. Try format: 'Make $500 profit today'")
            return True
        
        # Interrupt/Queue new task
        elif user_input == '!interrupt' or user_input.lower() == 'interrupt':
            self._handle_interrupt()
            return True
        
        # Show queued tasks
        elif user_input == '!queue' or user_input.lower() == 'queue':
            self._show_queued_tasks()
            return True
        
        # Show agent learning and growth
        elif user_input == '!memory' or user_input.lower() == 'memory':
            self._show_agent_memory()
            return True
        
        # Show agent wisdom for current context
        elif user_input == '!wisdom' or user_input.lower() == 'wisdom':
            self._show_agent_wisdom()
            return True
        
        # Show active goals
        elif user_input == '!goals' or user_input.lower() == 'goals':
            self._show_active_goals()
            return True
        
        # Show progress reports
        elif user_input == '!progress' or user_input.lower() == 'progress':
            self._show_progress_reports()
            return True
        
        # Stop goal trading
        elif user_input.startswith('!stop-goal'):
            parts = user_input.split()
            if len(parts) > 1:
                goal_id = parts[1]
                result = stop_goal_trading(goal_id)
                self._print_system_message(result)
            else:
                self._print_system_message("❌ Usage: !stop-goal <goal_id>")
            return True
        
        # Execute last recommendations
        elif user_input == '!execute' or user_input.lower() == 'execute':
            self._execute_last_recommendations()
            return True
        
        # Toggle auto-execute
        elif user_input == '!auto-execute' or user_input.lower() == 'auto-execute':
            self._toggle_auto_execute()
            return True
        
        # Start profit optimization
        elif user_input == '!profit' or user_input.lower() == 'profit':
            self._start_profit_optimization()
            return True
        
        # Run manual optimization
        elif user_input == '!optimize' or user_input.lower() == 'optimize':
            self._run_manual_optimization()
            return True
        
        # Execute profit-taking strategy
        elif user_input == '!take-profits' or user_input.lower() == 'take-profits':
            self._execute_profit_taking_strategy()
            return True
        
        # Check profitable positions
        elif user_input == '!check-profits' or user_input.lower() == 'check-profits':
            self._check_profitable_positions()
            return True
        
        # Trigger hacker assessment
        if user_input == '!hacker-assess':
            from crewai import Crew
            # Note: hacker_task is not defined, so this command is disabled
            self._print_system_message("❌ Hacker assessment feature not available - task not defined")
            return True
        
        # Show prompts directory
        if user_input == '!prompts':
            self._show_prompts_directory()
            return True
        
        # Trigger scan agent for undervalued stocks
        # REMOVED - SCAN AGENT NO LONGER AVAILABLE
        # if user_input == '!scan-opportunities' or user_input.lower() == 'scan-opportunities':
        #     from crewai import Crew
        #     from tasks.scan_task import scan_opportunities_task
        #     crew = Crew(agents=[scan_agent], tasks=[scan_opportunities_task])
        #     result = crew.kickoff()
        #     self._print_system_message(f"Scan Agent Results:\n{result}")
        #     return True
        
        # REMOVED - SCAN AGENT NO LONGER AVAILABLE
        # Trigger news-based stock discovery
        # if user_input == '!discover-stocks' or user_input.lower() == 'discover-stocks':
        #     from crewai import Crew
        #     from tasks.scan_task import scan_opportunities_task
        #     crew = Crew(agents=[scan_agent], tasks=[scan_opportunities_task])
        #     result = crew.kickoff()
        #     self._print_system_message(f"News Discovery Results:\n{result}")
        #     return True
        
        # REMOVED - SCAN AGENT NO LONGER AVAILABLE
        # Trigger team report generation
        # if user_input == '!team-report' or user_input.lower() == 'team-report':
        #     from crewai import Crew
        #     from tasks.scan_task import scan_opportunities_task
        #     crew = Crew(agents=[scan_agent], tasks=[scan_opportunities_task])
        #     result = crew.kickoff()
        #     self._print_system_message(f"Team Report Results:\n{result}")
        #     return True
        
        # REMOVED - SCAN AGENT NO LONGER AVAILABLE
        # Trigger scan and execute workflow
        # if user_input == '!scan-execute' or user_input.lower() == 'scan-execute':
        #     from crewai import Crew
        #     from tasks.scan_task import scan_opportunities_task
        #     crew = Crew(agents=[scan_agent], tasks=[scan_opportunities_task])
        #     result = crew.kickoff()
        #     self._print_system_message(f"Scan and Execute Results:\n{result}")
        #     return True
        
        return False
    
    def _scan_watchlist(self):
        """Scan all stocks in the DEFAULT_WATCHLIST"""
        try:
            watchlist = get_default_watchlist()
            
            # Print scan header with market status
            market_status = get_market_hours_message()
            self._print_system_message(f"🔍 SCANNING WATCHLIST: {', '.join(watchlist)}")
            print(f"{Fore.CYAN}│ {Fore.WHITE}📊 Quick analysis of {len(watchlist)} stocks...")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}⏰ {market_status}")
            print(f"{Fore.CYAN}│")
            
            # Create the dynamic team collaboration for watchlist scan
            from crewai import Crew, Task
            
            # Import agents
            from agents.analyst_agent import create_analyst_agent
            from agents.news_sentiment_agent import create_news_sentiment_agent
            
            # Create watchlist scan task
            watchlist_scan_task = Task(
                description=f"""
Perform a QUICK SCAN of the following watchlist stocks: {', '.join(watchlist)}

For each stock, provide:
1. Current price and daily change
2. Overall sentiment (positive/negative/neutral)
3. Key technical signal (bullish/bearish/neutral)
4. Brief recommendation (buy/sell_short/close/hold)

Present results in a clear, organized format showing:
- Stock symbol and current price
- Daily change percentage
- Technical signal
- News sentiment
- Quick recommendation

Focus on speed and key insights rather than detailed analysis.
""",
                expected_output="Quick scan results for all watchlist stocks with key metrics and recommendations",
                agent=create_analyst_agent()
            )
            
            # Create crew for watchlist scan
            scan_crew = Crew(
                agents=[create_analyst_agent(), create_news_sentiment_agent()],
                tasks=[watchlist_scan_task],
                verbose=True,
                process="sequential",
                memory=False,  # Disable memory for quick scan
                max_rpm=30
            )
            
            # Execute scan
            result = scan_crew.kickoff()
            
            # Display results
            print(f"\n{Fore.GREEN}┌─ {Fore.WHITE}📊 WATCHLIST SCAN RESULTS {Fore.GREEN}─┐")
            print(f"{Fore.GREEN}│ {Fore.WHITE}{result}")
            print(f"{Fore.GREEN}└─────────────────────────────────────────────────────────────────┘")
            
            # Add to conversation history
            self._add_to_history(f"!scan watchlist: {', '.join(watchlist)}", str(result))
            
        except Exception as e:
            error_msg = f"Error scanning watchlist: {str(e)}"
            self._print_system_message(f"❌ {error_msg}")
            print(f"{Fore.RED}│ {Fore.WHITE}Try individual stock analysis instead")
    
    def _handle_interrupt(self):
        """Handle interruption during agent execution"""
        if self.crew_running:
            self._print_system_message("⚠️  INTERRUPTION REQUEST - Crew is currently running")
            print(f"{Fore.YELLOW}│ Current execution will complete, then new task will be queued")
            print(f"{Fore.YELLOW}│ Enter your new priority task:")
            
            # Get new task from user
            new_task = input(f"{Fore.CYAN}➤ {Fore.WHITE}").strip()
            
            if new_task and new_task.lower() != 'cancel':
                self.queued_tasks.append({
                    'task': new_task,
                    'timestamp': datetime.now(),
                    'priority': 'high'
                })
                self._print_system_message(f"✅ Task queued: {new_task}")
                print(f"{Fore.GREEN}│ Will execute after current team completes")
            else:
                self._print_system_message("❌ Interrupt cancelled")
        else:
            self._print_system_message("⚠️  No crew currently running - use normal commands")
    
    def _show_queued_tasks(self):
        """Show all queued tasks"""
        if not self.queued_tasks:
            self._print_system_message("📋 No queued tasks")
            return
        
        self._print_system_message(f"📋 QUEUED TASKS ({len(self.queued_tasks)})")
        for i, task in enumerate(self.queued_tasks, 1):
            timestamp = task['timestamp'].strftime("%H:%M:%S")
            priority = task['priority'].upper()
            print(f"{Fore.CYAN}│ {i}. [{priority}] {task['task']}")
            print(f"{Fore.CYAN}│    Queued at: {timestamp}")
        
        print(f"{Fore.CYAN}│")
        print(f"{Fore.WHITE}Use '@team' to process queued tasks")
    
    def _process_queued_tasks(self):
        """Process all queued tasks"""
        if not self.queued_tasks:
            return
        
        self._print_system_message(f"🔄 Processing {len(self.queued_tasks)} queued tasks...")
        
        for task in self.queued_tasks:
            print(f"{Fore.CYAN}│ Processing: {task['task']}")
            response = self._run_team_collaboration(task['task'])
            print(f"{Fore.WHITE}{response}")
            print(f"{Fore.CYAN}│ Task completed ✅")
        
        self.queued_tasks = []  # Clear queue
        self._print_system_message("✅ All queued tasks completed")
    
    def _show_agent_memory(self):
        """Show agent learning and memory statistics"""
        try:
            current_agent = self.current_agent_name
            insights = memory_system.generate_learning_insights(current_agent)
            
            self._print_system_message(f"🧠 AGENT MEMORY - {current_agent.upper()}")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 📊 Learning Statistics:")
            print(f"{Fore.CYAN}│   • Total Experiences: {insights['total_experiences']}")
            print(f"{Fore.CYAN}│   • Learned Patterns: {insights['learned_patterns']}")
            print(f"{Fore.CYAN}│   • Average Success: {insights['average_success_rate']:.1%}")
            print(f"{Fore.CYAN}│   • Personality Changes: {insights['personality_changes']}")
            
            confidence_evo = insights['confidence_evolution']
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 🎯 Confidence Evolution:")
            print(f"{Fore.CYAN}│   • Trend: {confidence_evo['trend'].upper()}")
            print(f"{Fore.CYAN}│   • Change: {confidence_evo.get('change', 0):+.2f}")
            
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 🚀 Learning Trajectory: {insights['learning_trajectory'].replace('_', ' ').title()}")
            
            if insights['strongest_patterns']:
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ 🔍 Top Learned Patterns:")
                for i, pattern in enumerate(insights['strongest_patterns'], 1):
                    print(f"{Fore.CYAN}│   {i}. {pattern.expected_outcome} (Success: {pattern.success_rate:.1%})")
            
            specializations = insights['current_specializations']
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 🎓 Current Specializations: {', '.join(specializations)}")
            
        except Exception as e:
            self._print_system_message(f"❌ Error accessing memory: {str(e)}")
    
    def _show_agent_wisdom(self):
        """Show agent wisdom for current context"""
        try:
            current_agent = self.current_agent_name
            
            # Get recent conversation context
            recent_context = ""
            if self.conversation_history:
                recent_context = " ".join([entry['user'] for entry in self.conversation_history[-3:]])
            
            wisdom = get_agent_wisdom(current_agent, recent_context)
            
            self._print_system_message(f"🔮 AGENT WISDOM - {current_agent.upper()}")
            print(f"{Fore.CYAN}│")
            
            # Show relevant experiences
            if wisdom['relevant_experiences']:
                print(f"{Fore.CYAN}│ 📚 Relevant Past Experiences:")
                for i, exp in enumerate(wisdom['relevant_experiences'][:3], 1):
                    print(f"{Fore.CYAN}│   {i}. {exp.action} → {exp.outcome} (Success: {exp.success_score:.1%})")
            
            # Show applicable patterns
            if wisdom['applicable_patterns']:
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ 🔍 Applicable Patterns:")
                for i, pattern in enumerate(wisdom['applicable_patterns'][:2], 1):
                    print(f"{Fore.CYAN}│   {i}. {pattern.expected_outcome} (Success: {pattern.success_rate:.1%})")
            
            # Show personality traits
            personality = wisdom['personality']
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 🎭 Current Personality:")
            print(f"{Fore.CYAN}│   • Risk Tolerance: {personality.risk_tolerance:.1%}")
            print(f"{Fore.CYAN}│   • Confidence Threshold: {personality.confidence_threshold:.1%}")
            print(f"{Fore.CYAN}│   • Decision Speed: {personality.decision_speed:.1%}")
            
            # Show recommendations
            if wisdom['recommendations']:
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ 💡 Wisdom-Based Recommendations:")
                for i, rec in enumerate(wisdom['recommendations'], 1):
                    print(f"{Fore.CYAN}│   {i}. {rec}")
            
        except Exception as e:
            self._print_system_message(f"❌ Error accessing wisdom: {str(e)}")
    
    def _show_active_goals(self):
        """Show active trading goals"""
        try:
            goals_summary = get_goals_summary()
            active_goals = goal_tracker.get_active_goals()
            
            self._print_system_message(f"🎯 ACTIVE TRADING GOALS ({len(active_goals)})")
            
            if not active_goals:
                print(f"{Fore.CYAN}│ No active goals. Use '@team increase portfolio gains to 10%' to start goal-oriented trading!")
                return
            
            for i, goal in enumerate(active_goals, 1):
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ {i}. {goal.description}")
                print(f"{Fore.CYAN}│    Goal ID: {goal.id}")
                print(f"{Fore.CYAN}│    Target: {goal.target_value}%")
                print(f"{Fore.CYAN}│    Current: {goal.current_value:.2f}%")
                print(f"{Fore.CYAN}│    Progress: {goal.progress_percentage:.1f}%")
                print(f"{Fore.CYAN}│    Status: {goal.status.value.upper()}")
                print(f"{Fore.CYAN}│    Daily Trading: {'✅ ENABLED' if goal.daily_trading_enabled else '❌ DISABLED'}")
                
                if goal.deadline:
                    days_left = goal.days_remaining()
                    print(f"{Fore.CYAN}│    Deadline: {days_left} days remaining")
            
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ 💡 Use '!progress' for detailed progress reports")
            print(f"{Fore.CYAN}│ 💡 Use '!stop-goal <goal_id>' to stop trading for a specific goal")
            
        except Exception as e:
            self._print_system_message(f"❌ Error showing goals: {str(e)}")
    
    def _show_progress_reports(self):
        """Show detailed progress reports for all active goals"""
        try:
            active_goals = goal_tracker.get_active_goals()
            
            if not active_goals:
                self._print_system_message("📊 No active goals to report on")
                return
            
            self._print_system_message(f"📊 PROGRESS REPORTS ({len(active_goals)} goals)")
            
            for i, goal in enumerate(active_goals, 1):
                report = get_progress_report(goal.id)
                if not report:
                    continue
                
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ {i}. {report.goal_description}")
                print(f"{Fore.CYAN}│    Progress: {report.progress_percentage:.1f}% ({report.current_value:.2f}% / {report.target_value}%)")
                print(f"{Fore.CYAN}│    Days Active: {report.days_active}")
                print(f"{Fore.CYAN}│    Daily Average: {report.daily_average_progress:.3f}%")
                
                if report.estimated_completion_days:
                    print(f"{Fore.CYAN}│    Est. Completion: {report.estimated_completion_days} days")
                
                print(f"{Fore.CYAN}│    Recent Sessions: {len(report.recent_sessions)} (last 7 days)")
                print(f"{Fore.CYAN}│    Win Rate: {report.performance_metrics['win_rate']:.1%}")
                print(f"{Fore.CYAN}│    Total Profit: ${report.performance_metrics['total_profit']:.2f}")
                print(f"{Fore.CYAN}│    Trend: {report.trend_analysis.get('trend', 'N/A').upper()}")
                
                if report.recommendations:
                    print(f"{Fore.CYAN}│    Recommendations:")
                    for rec in report.recommendations[:3]:  # Show top 3
                        print(f"{Fore.CYAN}│      • {rec}")
            
            # Show leaderboard
            leaderboard = get_goals_leaderboard()
            if len(leaderboard) > 1:
                print(f"{Fore.CYAN}│")
                print(f"{Fore.CYAN}│ 🏆 GOALS LEADERBOARD:")
                for i, entry in enumerate(leaderboard[:3], 1):
                    print(f"{Fore.CYAN}│    {i}. {entry['description'][:50]}... ({entry['progress_percentage']:.1f}%)")
            
        except Exception as e:
            self._print_system_message(f"❌ Error showing progress reports: {str(e)}")
    
    def _parse_goal_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Parse user input to detect goal-oriented requests"""
        try:
            # Use the goal tracker's parsing function
            goal_info = goal_tracker.parse_goal_from_text(user_input)
            return goal_info
        except Exception as e:
            return None
    
    def _handle_goal_oriented_request(self, goal_info: Tuple, user_input: str) -> str:
        """Handle goal-oriented trading requests with automatic execution"""
        try:
            goal_type, target_value, description, deadline = goal_info
            
            print(f"{Fore.CYAN}│ {Fore.YELLOW}🎯 GOAL-ORIENTED TRADING DETECTED")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Goal: {description}")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Target: {target_value}%")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Type: {goal_type.value.upper()}")
            print(f"{Fore.CYAN}│")
            
            # Create the goal
            goal_id = goal_tracker.create_goal(
                goal_type=goal_type,
                target_value=target_value,
                description=description,
                deadline=deadline,
                daily_trading=True,
                priority=1
            )
            
            # Activate the goal
            goal_tracker.activate_goal(goal_id)
            
            print(f"{Fore.CYAN}│ {Fore.GREEN}✅ Goal created: {goal_id}")
            print(f"{Fore.CYAN}│")
            
            # Start persistent trading
            result = start_persistent_trading(goal_id, user_input)
            
            # Run initial team collaboration
            print(f"{Fore.CYAN}│ {Fore.YELLOW}🚀 STARTING INITIAL TRADING SESSION...")
            print(f"{Fore.CYAN}│")
            
            initial_result = self._create_dynamic_team_collaboration(user_input)
            
            # AUTOMATICALLY EXECUTE RECOMMENDATIONS
            print(f"{Fore.CYAN}│ {Fore.MAGENTA}⚡ EXECUTING TRADING RECOMMENDATIONS...")
            print(f"{Fore.CYAN}│")
            
            execution_result = execute_team_recommendations(initial_result, goal_id)
            
            # Format execution results
            execution_summary = self._format_execution_results(execution_result)
            
            # Combine results
            combined_result = f"""
{result}

📊 **INITIAL TRADING SESSION RESULTS:**
{initial_result}

⚡ **AUTOMATIC TRADE EXECUTION:**
{execution_summary}

🎯 **PERSISTENT TRADING STATUS:**
• Goal ID: {goal_id}
• Target: {target_value}%
• Status: ACTIVE
• Daily Trading: ENABLED
• Auto-Execution: ENABLED

The team will continue trading daily until this goal is achieved!
Use '!goals' to monitor progress or '!stop-goal {goal_id}' to pause.
"""
            
            return combined_result
            
        except Exception as e:
            return f"❌ Error handling goal-oriented request: {str(e)}"
    
    def _handle_goal_notification(self, notification: Dict[str, Any]):
        """Handle goal milestone and completion notifications"""
        try:
            if notification['type'] == 'milestone':
                milestone = notification['milestone']
                goal_description = notification['goal_description']
                
                if milestone == 100:
                    # Goal completed!
                    self._display_goal_completion(notification)
                else:
                    # Milestone achieved
                    self._display_milestone_achievement(notification)
                    
        except Exception as e:
            print(f"Error handling goal notification: {e}")
    
    def _display_goal_completion(self, notification: Dict[str, Any]):
        """Display goal completion celebration"""
        goal_id = notification['goal_id']
        goal_description = notification['goal_description']
        
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}🎉 GOAL ACHIEVED! 🎉")
        print(f"{Fore.YELLOW}{'='*80}")
        print(f"{Fore.GREEN}✅ {goal_description}")
        print(f"{Fore.GREEN}✅ Goal ID: {goal_id}")
        print(f"{Fore.GREEN}✅ Status: COMPLETED")
        print(f"{Fore.GREEN}✅ Achievement Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.YELLOW}{'='*80}")
        print(f"{Fore.CYAN}🎊 Congratulations! Your persistent trading goal has been achieved!")
        print(f"{Fore.CYAN}The team successfully completed the mission through daily trading sessions.")
        print(f"{Fore.CYAN}Use '!goals' to see all your achievements or set a new goal with '@team'.")
        print(f"{Fore.YELLOW}{'='*80}")
    
    def _display_milestone_achievement(self, notification: Dict[str, Any]):
        """Display milestone achievement notification"""
        milestone = notification['milestone']
        goal_description = notification['goal_description']
        
        print(f"\n{Fore.BLUE}┌─ {Fore.YELLOW}🎯 MILESTONE ACHIEVED! {Fore.BLUE}─┐")
        print(f"{Fore.BLUE}│ {Fore.WHITE}{goal_description}")
        print(f"{Fore.BLUE}│ {Fore.YELLOW}Progress: {milestone}% complete!")
        print(f"{Fore.BLUE}│ {Fore.WHITE}Keep up the excellent work! 🚀")
        print(f"{Fore.BLUE}└─────────────────────────────────────────────────────────────────┘")
    
    def _format_execution_results(self, execution_result: Dict[str, Any]) -> str:
        """Format trade execution results for display"""
        if not execution_result.get("success", False):
            return f"❌ No trades executed: {execution_result.get('message', 'Unknown error')}"
        
        executed_trades = execution_result.get("executed_trades", [])
        failed_trades = execution_result.get("failed_trades", [])
        
        if not executed_trades and not failed_trades:
            return "ℹ️ No trading recommendations found to execute"
        
        result_lines = []
        
        # Successful trades
        if executed_trades:
            result_lines.append(f"✅ **EXECUTED TRADES ({len(executed_trades)}):**")
            for trade in executed_trades:
                result_lines.append(f"   • {trade['action']} {trade['symbol']}: {trade['shares']:.2f} shares @ ${trade['price']:.2f}")
                result_lines.append(f"     Value: ${trade['value']:,.2f} | Reason: {trade['reason']}")
        
        # Failed trades
        if failed_trades:
            result_lines.append(f"\n❌ **FAILED TRADES ({len(failed_trades)}):**")
            for failed in failed_trades:
                try:
                    action = failed.get('action')
                    error = failed.get('error', 'Unknown error')
                    
                    if action and hasattr(action, 'action') and hasattr(action, 'symbol'):
                        # Valid TradeAction object
                        result_lines.append(f"   • {action.action} {action.symbol}: {error}")
                    elif action and isinstance(action, str):
                        # String representation of action
                        result_lines.append(f"   • {action}: {error}")
                    else:
                        # Fallback for malformed action
                        result_lines.append(f"   • Unknown action: {error}")
                except Exception as e:
                    # Safety fallback if anything goes wrong
                    result_lines.append(f"   • Error processing failed trade: {str(e)}")
        
        # Summary
        total_value = execution_result.get("total_value_traded", 0)
        result_lines.append(f"\n📊 **EXECUTION SUMMARY:**")
        result_lines.append(f"   • Total Trades: {execution_result.get('total_trades', 0)}")
        result_lines.append(f"   • Successful: {execution_result.get('successful_trades', 0)}")
        result_lines.append(f"   • Failed: {execution_result.get('failed_trades_count', 0)}")
        result_lines.append(f"   • Total Value: ${total_value:,.2f}")
        result_lines.append(f"   • Execution Time: {execution_result.get('execution_time', 'N/A')}")
        
        return "\n".join(result_lines)
    
    def _execute_last_recommendations(self):
        """Execute recommendations from the last team collaboration"""
        if not self.last_team_output:
            self._print_system_message("❌ No previous team collaboration found to execute")
            return
        
        # Parse recommendations
        recommendations = parse_recommendations(self.last_team_output)
        
        if not recommendations:
            self._print_system_message("ℹ️ No trading recommendations found in last team output")
            return
        
        # Show recommendations before execution
        self._print_system_message(f"📋 Found {len(recommendations)} trading recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{Fore.CYAN}│ {i}. {rec.action} {rec.symbol} - {rec.reason}")
        
        # Ask for confirmation
        print(f"{Fore.CYAN}│")
        confirm = input(f"{Fore.CYAN}│ Execute these trades? (y/N): {Fore.WHITE}").strip().lower()
        
        if confirm not in ['y', 'yes']:
            self._print_system_message("❌ Trade execution cancelled")
            return
        
        # Execute trades
        self._print_system_message("⚡ EXECUTING TRADING RECOMMENDATIONS...")
        print(f"{Fore.CYAN}│")
        
        execution_result = execute_team_recommendations(self.last_team_output)
        execution_summary = self._format_execution_results(execution_result)
        
        self._print_system_message("⚡ EXECUTION COMPLETE")
        print(f"{Fore.CYAN}│")
        print(f"{Fore.CYAN}│ {execution_summary}")
    
    def _toggle_auto_execute(self):
        """Toggle automatic execution of team recommendations"""
        self.auto_execute_trades = not self.auto_execute_trades
        status = "ENABLED" if self.auto_execute_trades else "DISABLED"
        color = Fore.GREEN if self.auto_execute_trades else Fore.RED
        
        self._print_system_message(f"⚡ AUTO-EXECUTE: {color}{status}")
        print(f"{Fore.CYAN}│")
        
        if self.auto_execute_trades:
            print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠️  WARNING: Team recommendations will be executed automatically!")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Make sure you understand the risks before proceeding.")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Use '!auto-execute' again to disable.")
        else:
            print(f"{Fore.CYAN}│ {Fore.WHITE}Team recommendations will only be displayed.")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Use '!execute' to manually execute or '!auto-execute' to enable.")
    
    def _start_profit_optimization(self):
        """Start the profit optimization system"""
        try:
            from utils.profit_optimization_system import initialize_profit_optimization, get_optimization_status
            
            result = initialize_profit_optimization()
            self._print_system_message("🚀 PROFIT OPTIMIZATION SYSTEM")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.GREEN}✅ {result}")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}🎯 System Features:")
            print(f"{Fore.CYAN}│   • Monitors open positions every 5 minutes")
            print(f"{Fore.CYAN}│   • Automatically closes profitable positions")
            print(f"{Fore.CYAN}│   • Adjusts stop losses to protect profits")
            print(f"{Fore.CYAN}│   • Coordinates with news and technical analysis")
            print(f"{Fore.CYAN}│   • Targets 2% daily profit")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Use '!optimize' for manual optimization")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Use '!progress' to monitor performance")
            
        except Exception as e:
            self._print_system_message(f"❌ Error starting profit optimization: {str(e)}")
    
    def _run_manual_optimization(self):
        """Run manual profit optimization"""
        try:
            from utils.profit_optimization_system import run_manual_optimization
            
            self._print_system_message("🔧 MANUAL PROFIT OPTIMIZATION")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.WHITE}🔄 Running Order Management Leader Agent...")
            print(f"{Fore.CYAN}│")
            
            result = run_manual_optimization()
            
            print(f"{Fore.CYAN}│ {Fore.GREEN}✅ {result}")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.WHITE}Check above for detailed profit optimization actions")
            
        except Exception as e:
            self._print_system_message(f"❌ Error running manual optimization: {str(e)}")
    
    def _execute_profit_taking_strategy(self):
        """Execute profit-taking and rebalancing strategy"""
        try:
            from tools.profit_taking_strategy_tool import execute_profit_taking_strategy
            
            self._print_system_message("🎯 PROFIT-TAKING & REBALANCING STRATEGY")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.WHITE}🔄 Executing automated strategy...")
            print(f"{Fore.CYAN}│   • Closing profitable positions")
            print(f"{Fore.CYAN}│   • Analyzing charts for opportunities")
            print(f"{Fore.CYAN}│   • Opening new positions")
            print(f"{Fore.CYAN}│")
            
            # Execute the strategy with DEFAULT_WATCHLIST (empty string uses DEFAULT_WATCHLIST)
            result = execute_profit_taking_strategy(profit_threshold=2.0, analysis_symbols="")
            
            # Display the result
            print(f"{Fore.CYAN}│ {Fore.GREEN}📊 STRATEGY RESULTS:")
            print(f"{Fore.CYAN}│")
            
            for line in result.split('\n'):
                if line.strip():
                    print(f"{Fore.CYAN}│ {Fore.WHITE}{line}")
            
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}💡 Strategy completed! Check positions with '@order_leader'")
            
        except Exception as e:
            self._print_system_message(f"❌ Error executing profit-taking strategy: {str(e)}")
    
    def _check_profitable_positions(self):
        """Check profitable positions quickly"""
        try:
            from tools.profit_taking_strategy_tool import check_profitable_positions
            
            self._print_system_message("💰 CHECKING PROFITABLE POSITIONS")
            print(f"{Fore.CYAN}│")
            
            # Check profitable positions with $10 minimum
            result = check_profitable_positions(min_profit_usd=10.0)
            
            # Display the result
            for line in result.split('\n'):
                if line.strip():
                    print(f"{Fore.CYAN}│ {Fore.WHITE}{line}")
            
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}💡 Use '!take-profits' to execute profit-taking strategy")
            
        except Exception as e:
            self._print_system_message(f"❌ Error checking profitable positions: {str(e)}")
    
    def _show_prompts_directory(self):
        """Show available prompts directory files"""
        try:
            prompts_dir = "prompts"
            if not os.path.exists(prompts_dir):
                self._print_system_message("❌ Prompts directory not found")
                return
            
            self._print_system_message("📄 PROMPTS DIRECTORY CONTENTS")
            print(f"{Fore.CYAN}│")
            
            # List all files in prompts directory
            files = os.listdir(prompts_dir)
            for file in sorted(files):
                if file.endswith('.md'):
                    file_path = os.path.join(prompts_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"{Fore.CYAN}│ 📄 {Fore.WHITE}{file} ({file_size:,} bytes)")
            
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}🔧 Key Files:")
            print(f"{Fore.CYAN}│   • STOCKSTRADER_TOOL_GUIDE.md - API documentation and examples")
            print(f"{Fore.CYAN}│   • AGENT_PROMPTS_ACCESS_GUIDE.md - How agents access prompts")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.GREEN}💡 Agents can read these files using the Coder Agent:")
            print(f"{Fore.CYAN}│   • read_file_enhanced('prompts/STOCKSTRADER_TOOL_GUIDE.md')")
            print(f"{Fore.CYAN}│   • search_files_enhanced('sell_short', 'prompts', '*.md')")
            print(f"{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.MAGENTA}✅ All agents have been informed about these updates!")
            
        except Exception as e:
            self._print_system_message(f"❌ Error showing prompts directory: {str(e)}")
    
    def _record_agent_experience(self, user_input: str, agent_response: str, success_score: float = 0.5):
        """Record an experience for agent learning"""
        try:
            from utils.market_hours import get_market_status
            
            # Get current market conditions
            market_status = get_market_status()
            market_conditions = {
                'is_open': market_status.is_open,
                'status': market_status.status,
                'market_day': market_status.market_day,
                'timestamp': datetime.now().isoformat()
            }
            
            # Determine success score based on response quality and user feedback
            # This is a simplified version - in practice, you'd want more sophisticated scoring
            confidence = 0.7 if len(agent_response) > 100 else 0.5
            
            experience_id = record_experience(
                agent_type=self.current_agent_name,
                action=user_input[:100],  # Truncate for storage
                context=user_input,
                outcome=agent_response[:200],  # Truncate for storage
                success_score=success_score,
                market_conditions=market_conditions,
                confidence=confidence
            )
            
            # Update agent personality based on accumulated performance
            self._update_agent_personality()
            
        except Exception as e:
            # Don't let memory errors break the main flow
            pass
    
    def _update_agent_personality(self):
        """Update agent personality based on recent performance"""
        try:
            current_agent = self.current_agent_name
            recent_experiences = memory_system.get_relevant_experiences(current_agent, "", limit=20)
            
            if len(recent_experiences) >= 10:  # Need enough data
                avg_success = sum(exp.success_score for exp in recent_experiences) / len(recent_experiences)
                
                performance_feedback = {
                    'success_rate': avg_success,
                    'total_experiences': len(recent_experiences),
                    'confidence_trend': 'improving' if avg_success > 0.6 else 'declining'
                }
                
                memory_system.update_agent_personality(current_agent, performance_feedback)
        except Exception as e:
            # Don't let personality updates break the main flow
            pass
    
    def _create_contextual_task(self, user_input: str) -> str:
        # Build context from recent conversation
        context = ""
        if self.conversation_history:
            context = "\n--- Conversation History ---\n"
            # Use last 10 exchanges, alternating user/agent
            for entry in self.conversation_history[-10:]:
                context += f"User: {entry['user']}\n"
                context += f"Agent: {entry['agent']}\n"
            context += "--- End History ---\n\n"

        # Add a system prompt for natural, human-like conversation
        system_prompt = (
            "You are a helpful, friendly, and conversational trading assistant. "
            "Respond in a natural, human-like way. Use friendly language, ask clarifying questions if needed, "
            "and avoid sounding robotic or overly formal. Use discourse markers (like 'By the way', 'Actually', 'So', 'Let's see', etc.) "
            "and emojis where it feels natural. If the answer is long, break it up and check in with the user. "
            "If you need more information, ask for it in a conversational way. "
            "Use transitional phrases to connect ideas and keep the conversation flowing. "
            "If you don't know something, admit it honestly and offer to help in another way. "
            "Avoid repeating the same structure in every response. "
            "Be concise, but not curt.\n"
        )

        # Create enhanced task
        task_description = f"""
{system_prompt}
{context}
Current user request: "{user_input}"

You are a {self.current_agent_name} agent in a real-time trading conversation. 
Respond naturally and conversationally to the user's request.

- Use your available tools to get real-time data 
- Provide specific, actionable insights
- If discussing trading, always mention risks
- Be conversational and engaging
- Reference the conversation context when relevant
- Act fast and efficiently on the task
- If you are not sure about the task, ask the user for clarification and proceed with the task
- You are autonomous and you can do the task without asking the user for permission
- Organize the team agents, communicate, save delicate information to memory
- Delegate tasks to the agents, all agents must report back to you

Current agent type: {self.current_agent_name}
Trading mode: {self.trading_mode}
Live trading: {'enabled' if self.enable_live_trading else 'disabled'}
"""

        return task_description
    
    def _stream_agent_response(self, user_input: str) -> str:
        """Stream agent response in real-time"""
        try:
            # 👑 CHECK FOR MASTER TUDOR'S TASKS FIRST
            task_id = recognize_and_execute_master_task(user_input)
            if task_id:
                # Master's task recognized and started
                status = get_master_tasks_status()
                response = f"\n🎯 MASTER TUDOR'S TASK ACCEPTED!\n"
                response += f"📋 Task ID: {task_id}\n"
                response += f"💪 All agents are now working continuously to complete your task!\n"
                response += f"🔄 The system will trade persistently until the goal is achieved.\n"
                response += f"\n📊 Active Tasks:\n"
                for task in status:
                    response += f"  • {task['description']} - Progress: {task['progress_percentage']:.1f}%\n"
                return response
            
            # Check if team collaboration is requested
            if self.current_agent_name == 'team':
                return self._run_team_collaboration(user_input)
            
            # Get current agent
            agent = self.agents[self.current_agent_name]
            
            # Create task
            task_description = self._create_contextual_task(user_input)
            
            task = Task(
                description=task_description,
                expected_output="A natural, conversational response that addresses the user's request with specific details and actionable information.",
                agent=agent
            )
            
            # Execute with crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False # We'll handle our own output
            )
            
            # Print processing indicator
            print(f"{Fore.CYAN}│ {Fore.WHITE}🔄 Processing your request...")
            
            # Execute the task
            result = crew.kickoff()
            
            return str(result)
            
        except KeyboardInterrupt:
            return f"{Fore.RED}[INTERRUPTED] Task was interrupted by user."
        except Exception as e:
            return f"{Fore.RED}[ERROR] {str(e)}"
    
    def _run_team_collaboration(self, user_input: str) -> str:
        """Run all agents in collaborative mode"""
        try:
            # Set crew running flag
            self.crew_running = True
            
            # 👑 CHECK FOR MASTER TUDOR'S TASKS IN TEAM MODE
            task_id = recognize_and_execute_master_task(user_input)
            if task_id:
                # Master's task recognized - agents will work continuously
                status = get_master_tasks_status()
                response = f"\n👑 MASTER TUDOR'S TASK RECOGNIZED!\n"
                response += f"🤖 ALL 8 AGENTS ACTIVATED FOR CONTINUOUS EXECUTION\n"
                response += f"🎯 Task: {status[0]['description'] if status else user_input}\n"
                response += f"💪 The team will work CONTINUOUSLY until your goal is achieved!\n"
                response += f"📊 Progress will be monitored and reported automatically.\n"
                response += f"\n⚡ Using ALL available tools:\n"
                response += f"  • Technical Analysis\n"
                response += f"  • Market Scanning\n"
                response += f"  • News Sentiment\n"
                response += f"  • Risk Assessment\n"
                response += f"  • Portfolio Optimization\n"
                response += f"  • Profit Taking Strategy\n"
                response += f"  • Continuous Trading Engine\n"
                return response
            
            # Check if this is a goal-oriented request
            goal_info = self._parse_goal_request(user_input)
            if goal_info:
                return self._handle_goal_oriented_request(goal_info, user_input)
            
            # Print team collaboration header
            print(f"{Fore.CYAN}│ {Fore.YELLOW}⭐ TEAM COLLABORATION MODE ACTIVATED (8 AGENTS)")
            print(f"{Fore.CYAN}│ {Fore.WHITE}🔄 All 8 agents working together...")
            print(f"{Fore.CYAN}│")
            
            # Create dynamic team collaboration
            result = self._create_dynamic_team_collaboration(user_input)
            
            # Process any queued tasks after completion
            self._process_queued_tasks()
            
            return result
            
        except KeyboardInterrupt:
            return f"{Fore.RED}[INTERRUPTED] Team collaboration was interrupted by user."
        except Exception as e:
            return f"{Fore.RED}[ERROR] Team collaboration failed: {str(e)}"
        finally:
            # Always reset crew running flag
            self.crew_running = False
    
    def _needs_default_target(self, user_input: str) -> bool:
        """Check if user input needs a default trading target"""
        # If user input is very general or doesn't specify a clear goal
        general_requests = [
            "analyze", "check", "status", "update", "what", "how", "help",
            "portfolio", "positions", "market", "news", "sentiment"
        ]
        
        # Check if user input is too general and needs profit optimization focus
        user_lower = user_input.lower()
        
        # If it's a short/general request without specific goals
        if (len(user_input.split()) <= 3 or 
            any(word in user_lower for word in general_requests)):
            return True
            
        # If no clear trading target is mentioned
        target_keywords = [
            "$", "percent", "%", "profit", "gain", "target", "goal", 
            "buy", "sell", "close", "open", "increase", "decrease",
            "make", "earn", "achieve", "reach"
        ]
        
        has_target = any(keyword in user_lower for keyword in target_keywords)
        return not has_target

    def _add_default_target(self, user_input: str) -> str:
        """Add a default trading target when none is specified"""
        # Check if user already has a specific target
        if not self._needs_default_target(user_input):
            return user_input
        
        # Default targets based on current market conditions
        default_targets = [
            "Optimize current positions for maximum profit - close profitable positions and reinvest in new opportunities from DEFAULT_WATCHLIST",
            "Execute profit-taking strategy - target 5% portfolio gains through systematic position management",
            "Analyze DEFAULT_WATCHLIST for trading opportunities and optimize current holdings for profit",
            "the task is to trade continue to monitor the market in opening hours en increase the portfolio profit whit 30%"
        ]
        
        # Choose default target (you can make this more sophisticated)
        default_target = default_targets[0]
        
        # Enhance user input with default target
        enhanced_input = f"{user_input}. {default_target}"
        
        print(f"{Fore.CYAN}│ {Fore.YELLOW}🎯 DEFAULT TARGET ADDED: {default_target}")
        print(f"{Fore.CYAN}│")
        
        return enhanced_input

    def _should_continue_trading(self, result: str, cycle: int, max_cycles: int) -> bool:
        """Determine if trading should continue for another cycle"""
        if not result or cycle >= max_cycles:
            return False
        
        result_lower = str(result).lower()
        
        # Continue if target not achieved
        continue_indicators = [
            "mission status: ongoing",
            "target achievement: continuing",
            "continuing 🔄", 
            "not yet achieved",
            "target not reached",
            "continuing to",
            "multiple cycles needed"
        ]
        
        # Stop if clearly achieved
        stop_indicators = [
            "target achieved",
            "mission status: complete",
            "achieved ✅",
            "complete 🎉",
            "successfully completed",
            "goal reached"
        ]
        
        # Check for stop indicators first
        for indicator in stop_indicators:
            if indicator in result_lower:
                return False
        
        # Check for continue indicators
        for indicator in continue_indicators:
            if indicator in result_lower:
                return True
        
        # If no profitable positions were identified and no trades were made, continue
        if ("profitable positions identified: 0" in result_lower or 
            "total profit realized: $0" in result_lower or
            "no opportunities identified" in result_lower):
            return cycle < max_cycles
        
        # Default: don't continue unless explicitly indicated
        return False

    def _create_dynamic_team_collaboration(self, user_input: str) -> str:
        """Create dynamic team collaboration with profit optimization"""
        from crewai import Crew, Task
        
        # Check if user wants profit optimization or if no specific target is provided
        if ("optimize profits" in user_input.lower() or 
            "profit optimization" in user_input.lower() or 
            "leader agent" in user_input.lower() or
            self._needs_default_target(user_input)):
            
            # Add default target if none specified
            enhanced_input = self._add_default_target(user_input)
            return self._create_profit_optimized_collaboration(enhanced_input)
        
        # Create context for team collaboration
        context = ""
        if self.conversation_history:
            context = "\n--- Recent Conversation Context ---\n"
            for entry in self.conversation_history[-3:]:
                context += f"User: {entry['user']}\n"
                context += f"Agent: {entry['agent'][:200]}...\n\n"
            context += "--- End Context ---\n\n"
        
        # Create sequential tasks for all agents
        tasks = []
        
        # Task 1: Market Analysis (using imported task)
        tasks.append(get_stock_analysis)
        
        # Task 2: News Sentiment Analysis (using imported task)
        tasks.append(news_sentiment_analysis_task)
        
        # Task 3: Risk Assessment (using imported task)
        tasks.append(risk_assessment_task)
        
        # Task 4: Portfolio Optimization (using imported task)
        tasks.append(portfolio_optimization_task)
        
        # Task 5: Trading Decision (using imported task)
        tasks.append(trade_decision)
        
        # Task 6: Performance Analysis (using imported task)
        tasks.append(performance_analysis_task)
        
        # Task 7: Custom Code Development (if needed) - REMOVED
        # coder_task removed - not essential for core trading functionality
        
        # Task 8: Order Management & Profit Optimization (using imported task)
        tasks.append(order_management_task)
        
        # REMOVED - Task 9: Stock Scanning and Opportunity Analysis (scan_agent removed)
        

        
        # Create the collaborative crew (memory=False to avoid OpenAI API requirement)
        team_crew = Crew(
            agents=[
                create_analyst_agent(),
                create_news_sentiment_agent(),
                create_risk_management_agent(),
                create_portfolio_management_agent(),
                create_trader_agent(),
                create_performance_tracking_agent(),
                # coder_agent,  # Removed - not essential for core trading
                create_order_management_leader_agent()
                # scan_agent  # REMOVED
            ],
            tasks=tasks,
            verbose=True,
            process="sequential",
            memory=False,  # Disabled to avoid OpenAI API requirement - maintains $0 cost
            max_rpm=60,
            share_crew=True
        )
        
        # Execute the collaborative analysis with error handling
        print(f"{Fore.CYAN}│ {Fore.WHITE}🤝 Starting collaborative team analysis...")
        
        # Import the error handling function
        from crew import execute_crew_with_fallback
        
        execution_result = execute_crew_with_fallback(team_crew, max_retries=2)
        
        if execution_result["success"]:
            result = execution_result["result"]
            print(f"{Fore.CYAN}│ {Fore.GREEN}✅ Team analysis completed successfully (attempt {execution_result['attempt']})")
            
            # Store the result for potential execution
            self.last_team_output = str(result)
            
            # Auto-execute trades if enabled
            if self.auto_execute_trades:
                print(f"{Fore.CYAN}│ {Fore.MAGENTA}⚡ AUTO-EXECUTING RECOMMENDATIONS...")
                print(f"{Fore.CYAN}│")
                
                try:
                    # Fix NoneType error - ensure result is valid
                    if result and str(result).strip():
                        execution_result = execute_team_recommendations(str(result))
                    else:
                        execution_result = {"success": False, "message": "No trading recommendations found in team output"}
                    
                    if execution_result.get("success", False):
                        print(f"{Fore.CYAN}│ {Fore.GREEN}✅ Trading recommendations executed successfully")
                        if execution_result.get("executed_trades"):
                            print(f"{Fore.CYAN}│ {Fore.WHITE}📊 Executed {len(execution_result['executed_trades'])} trades")
                    else:
                        print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠️ {execution_result.get('message', 'Unknown execution error')}")
                except Exception as e:
                    print(f"{Fore.CYAN}│ {Fore.RED}❌ Error executing recommendations: {str(e)}")
                    print(f"{Fore.CYAN}│ {Fore.YELLOW}💡 Continuing with analysis results...")
        else:
            print(f"{Fore.CYAN}│ {Fore.RED}❌ Team analysis failed: {execution_result['error']}")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}💡 Falling back to individual agent recommendations...")
            
            # Fallback to simplified analysis
            result = f"Team analysis failed after {execution_result['attempt']} attempts. "
            result += "Individual agents should provide basic recommendations. "
            result += f"Error: {execution_result['error']}"
            
            self.last_team_output = result
    
    def _create_profit_optimized_collaboration(self, user_input: str) -> str:
        """Create profit-optimized team collaboration with Order Management Leader"""
        try:
            from utils.profit_optimization_system import create_profit_optimized_team_collaboration
            
            print(f"{Fore.CYAN}│ {Fore.YELLOW}🎯 PROFIT OPTIMIZATION MODE ACTIVATED")
            print(f"{Fore.CYAN}│ {Fore.WHITE}🔄 All 8 agents working together with Order Management Leader...")
            print(f"{Fore.CYAN}│ {Fore.MAGENTA}💪 TRADE TILL TASK DONE approach - will continue until target achieved")
            print(f"{Fore.CYAN}│")
            
            # Execute profit-optimized collaboration with continuation logic
            max_cycles = 3  # Prevent infinite loops
            cycle = 1
            
            while cycle <= max_cycles:
                print(f"{Fore.CYAN}│ {Fore.YELLOW}🔄 EXECUTION CYCLE {cycle}/{max_cycles}")
                print(f"{Fore.CYAN}│")
                
                # Execute collaboration
                result = create_profit_optimized_team_collaboration(user_input)
                
                # Check if target achieved or should continue
                if self._should_continue_trading(result, cycle, max_cycles):
                    print(f"{Fore.CYAN}│ {Fore.YELLOW}🎯 Target not yet achieved - continuing with cycle {cycle + 1}")
                    print(f"{Fore.CYAN}│")
                    cycle += 1
                    # Update user input for next cycle
                    user_input = f"Continue the previous trading strategy - {user_input}"
                else:
                    print(f"{Fore.CYAN}│ {Fore.GREEN}✅ Target achieved or maximum cycles reached")
                    print(f"{Fore.CYAN}│")
                    break
            
            return result
            
        except Exception as e:
            return f"{Fore.RED}[ERROR] Profit optimization failed: {str(e)}"
    
    def _add_to_history(self, user_input: str, agent_response: str):
        """Add conversation to history and record experience for learning"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'agent': agent_response,
            'agent_type': self.current_agent_name
        })
        
        # Record experience for agent learning
        success_score = self._estimate_response_success(agent_response)
        self._record_agent_experience(user_input, agent_response, success_score)
        
        # Keep only last 20 exchanges
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _estimate_response_success(self, agent_response: str) -> float:
        """Estimate the success score of an agent response"""
        try:
            # Simple heuristics for response quality
            base_score = 0.5
            
            # Length bonus (more detailed responses are usually better)
            if len(agent_response) > 200:
                base_score += 0.1
            if len(agent_response) > 500:
                base_score += 0.1
            
            # Content quality indicators
            quality_indicators = [
                '📊', '💡', '✅', '🎯', '📈', '📉',  # Emoji usage
                'analysis', 'recommendation', 'strategy', 'data',  # Key terms
                '%', '$', 'price', 'trend', 'risk'  # Financial terms
            ]
            
            for indicator in quality_indicators:
                if indicator.lower() in agent_response.lower():
                    base_score += 0.02
            
            # Error indicators (reduce score)
            error_indicators = ['error', 'failed', '❌', 'unable', 'cannot']
            for error in error_indicators:
                if error.lower() in agent_response.lower():
                    base_score -= 0.1
            
            return max(0.0, min(1.0, base_score))  # Clamp between 0 and 1
            
        except Exception:
            return 0.5  # Default neutral score
    
    def run(self):
        """Main chat loop"""
        try:
            while True:
                # Get user input
                try:
                    user_input = input(f"{Fore.GREEN}User: {Fore.WHITE}").strip()
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}[INTERRUPTED] Type !exit to quit or continue chatting...")
                    continue
                
                if not user_input:
                    continue
                
                # Print user input
                self._print_user_input(user_input)
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    if user_input == '!exit':
                        break
                    continue
                
                # Print agent header
                self._print_agent_header(self.current_agent_name)
                
                # Stream agent response
                try:
                    response = self._stream_agent_response(user_input)
                    
                    # Print response with streaming effect
                    print(f"{Fore.CYAN}│ {Fore.WHITE}", end="")
                    
                    # Simple streaming effect
                    words = response.split()
                    for i, word in enumerate(words):
                        print(word, end=" ", flush=True)
                        time.sleep(0.05)  # Small delay for streaming effect
                    
                    print()  # New line after response
                    
                except KeyboardInterrupt:
                    print(f"\n{Fore.CYAN}│ {Fore.YELLOW}[INTERRUPTED] You can give new instructions now.")
                    response = "[INTERRUPTED]"
                
                # Print agent footer
                self._print_agent_footer()
                
                # Add to history
                if response != "[INTERRUPTED]":
                    self._add_to_history(user_input, response)
                
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}")
            print(f"{Fore.WHITE}Please try again or contact support.")


def main():
    """Main function"""
    chat = AgentZeroStyleChat()
    chat.run()


if __name__ == "__main__":
    main() 