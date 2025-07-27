import os
import sys
import traceback
import numpy as np
import pandas as pd
import json
import math
from typing import Dict, Any, Optional, List
from crewai.tools import tool
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Essential modules only
try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import requests
except ImportError:
    requests = None

@tool("Python Code Executor Tool")
def execute_python_code(code: str, variables: str = "{}") -> str:
    """
    Execute Python code safely with access to math, numpy, pandas, and financial libraries.
    Perfect for custom calculations, data analysis, and financial computations.
    
    Parameters:
        code (str): Python code to execute
        variables (str): JSON string of variables to make available in the code
    
    Returns:
        str: Execution results with output and any created variables
    
    Examples:
        - execute_python_code("result = 100 * 1.05")
        - execute_python_code("import pandas as pd; df = pd.DataFrame({'prices': [100, 105, 110]}); mean_price = df['prices'].mean()")
        - execute_python_code("import numpy as np; returns = np.array([0.05, 0.03, -0.02]); sharpe_ratio = np.mean(returns) / np.std(returns)")
    """
    try:
        # Parse variables if provided
        input_vars = {}
        if variables and variables != "{}":
            try:
                input_vars = json.loads(variables)
            except json.JSONDecodeError:
                return "❌ Error: Invalid JSON format for variables parameter"
        
        # Create safe execution environment
        safe_globals = {
            '__builtins__': {
                'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
                'len': len, 'range': range, 'enumerate': enumerate, 'zip': zip,
                'sorted': sorted, 'reversed': reversed, 'int': int, 'float': float,
                'str': str, 'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
                'set': set, 'print': print, 'type': type, 'isinstance': isinstance,
            },
            'math': math,
            'np': np,
            'numpy': np,
            'pd': pd,
            'pandas': pd,
            'json': json,
            'datetime': datetime,
            'timedelta': timedelta,
        }
        
        # Add yfinance if available
        if yf:
            safe_globals['yf'] = yf
            safe_globals['yfinance'] = yf
        
        # Add input variables
        safe_globals.update(input_vars)
        
        # Capture output
        original_stdout = sys.stdout
        sys.stdout = mystdout = StringIOWrapper()
        
        # Execute code
        exec(code, safe_globals)
        
        # Restore stdout and get output
        sys.stdout = original_stdout
        output = mystdout.getvalue()
        
        # Extract new variables
        result_vars = {}
        for key, value in safe_globals.items():
            if (key not in {'__builtins__', 'math', 'np', 'numpy', 'pd', 'pandas', 
                           'json', 'datetime', 'timedelta', 'yf', 'yfinance'} and
                key not in input_vars and not key.startswith('_')):
                try:
                    # Try to serialize the value
                    json.dumps(value, default=str)
                    result_vars[key] = value
                except (TypeError, ValueError):
                    result_vars[key] = str(value)
        
        # Format result
        result = []
        if output.strip():
            result.append(f"📊 Output:\n{output}")
        
        if result_vars:
            result.append(f"📈 Created Variables:\n{json.dumps(result_vars, indent=2, default=str)}")
        
        return "\n\n".join(result) if result else "✅ Code executed successfully (no output)"
        
    except Exception as e:
        return f"❌ Error executing code: {str(e)}\n{traceback.format_exc()}"

@tool("Financial Calculator Tool")
def calculate_financial_metrics(principal: float, rate: float = None, time: float = None, 
                               calculation_type: str = "compound_interest") -> str:
    """
    Calculate common financial metrics and formulas.
    
    Parameters:
        principal (float): Principal amount or current value
        rate (float): Interest rate or return rate (as decimal, e.g., 0.05 for 5%)
        time (float): Time period in years
        calculation_type (str): Type of calculation
            - "compound_interest": Compound interest calculation
            - "simple_interest": Simple interest calculation
            - "future_value": Future value calculation
            - "present_value": Present value calculation
            - "roi": Return on investment
    
    Returns:
        str: Calculated financial metrics
    """
    try:
        if calculation_type == "compound_interest":
            if not all([principal, rate, time]):
                return "❌ Error: Principal, rate, and time required for compound interest"
            future_value = principal * (1 + rate) ** time
            interest = future_value - principal
            return f"💰 Compound Interest Calculation:\n" \
                   f"Principal: ${principal:,.2f}\n" \
                   f"Rate: {rate*100:.2f}%\n" \
                   f"Time: {time} years\n" \
                   f"Future Value: ${future_value:,.2f}\n" \
                   f"Interest Earned: ${interest:,.2f}"
        
        elif calculation_type == "simple_interest":
            if not all([principal, rate, time]):
                return "❌ Error: Principal, rate, and time required for simple interest"
            interest = principal * rate * time
            future_value = principal + interest
            return f"💰 Simple Interest Calculation:\n" \
                   f"Principal: ${principal:,.2f}\n" \
                   f"Rate: {rate*100:.2f}%\n" \
                   f"Time: {time} years\n" \
                   f"Future Value: ${future_value:,.2f}\n" \
                   f"Interest Earned: ${interest:,.2f}"
        
        elif calculation_type == "roi":
            if not all([principal, rate]):
                return "❌ Error: Principal and final value (as rate) required for ROI"
            roi_percent = ((rate - principal) / principal) * 100
            return f"📈 ROI Calculation:\n" \
                   f"Initial Investment: ${principal:,.2f}\n" \
                   f"Final Value: ${rate:,.2f}\n" \
                   f"ROI: {roi_percent:.2f}%"
        
        else:
            return f"❌ Error: Unknown calculation type '{calculation_type}'"
            
    except Exception as e:
        return f"❌ Error in financial calculation: {str(e)}"

@tool("Data Analysis Tool")
def analyze_data(data: str, analysis_type: str = "basic_stats") -> str:
    """
    Analyze numerical data with statistical calculations.
    
    Parameters:
        data (str): JSON string of numerical data or list of numbers
        analysis_type (str): Type of analysis
            - "basic_stats": Mean, median, mode, std dev
            - "returns": Return calculations for financial data
            - "risk_metrics": Risk analysis metrics
    
    Returns:
        str: Data analysis results
    """
    try:
        # Parse data
        if isinstance(data, str):
            data_list = json.loads(data)
        else:
            data_list = data
        
        if not isinstance(data_list, list) or not data_list:
            return "❌ Error: Data must be a non-empty list of numbers"
        
        # Convert to numpy array
        arr = np.array(data_list, dtype=float)
        
        if analysis_type == "basic_stats":
            stats = {
                "count": len(arr),
                "mean": float(np.mean(arr)),
                "median": float(np.median(arr)),
                "std_dev": float(np.std(arr)),
                "variance": float(np.var(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "range": float(np.max(arr) - np.min(arr))
            }
            
            result = "📊 Basic Statistical Analysis:\n"
            for key, value in stats.items():
                result += f"{key.replace('_', ' ').title()}: {value:.4f}\n"
            return result
        
        elif analysis_type == "returns":
            if len(arr) < 2:
                return "❌ Error: Need at least 2 data points for return calculations"
            
            returns = np.diff(arr) / arr[:-1]
            
            stats = {
                "avg_return": float(np.mean(returns)),
                "total_return": float((arr[-1] - arr[0]) / arr[0]),
                "volatility": float(np.std(returns)),
                "sharpe_ratio": float(np.mean(returns) / np.std(returns)) if np.std(returns) != 0 else 0,
                "max_return": float(np.max(returns)),
                "min_return": float(np.min(returns))
            }
            
            result = "📈 Returns Analysis:\n"
            for key, value in stats.items():
                if 'return' in key or 'ratio' in key:
                    result += f"{key.replace('_', ' ').title()}: {value*100:.2f}%\n"
                else:
                    result += f"{key.replace('_', ' ').title()}: {value:.4f}\n"
            return result
        
        else:
            return f"❌ Error: Unknown analysis type '{analysis_type}'"
            
    except Exception as e:
        return f"❌ Error in data analysis: {str(e)}"

class StringIOWrapper:
    """Simple StringIO wrapper for capturing output"""
    def __init__(self):
        self.content = []
    
    def write(self, s):
        self.content.append(str(s))
    
    def getvalue(self):
        return ''.join(self.content)
    
    def flush(self):
        pass 