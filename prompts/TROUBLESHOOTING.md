# CrewAI Stock Trading Agents - Troubleshooting Guide

## Common Issues and Solutions

### 1. ModuleNotFoundError: No module named 'tools'

**Error:**
```
ModuleNotFoundError: No module named 'tools'
```

**Cause:** Running individual agent files directly instead of from the project root.

**Solutions:**

#### Option A: Run from project root (Recommended)
```bash
# Navigate to the main project directory
cd crewai-stock-trader-agents-main

# Run the main application
python agent_zero_chat.py

# Or run the crew system
python crew.py
```

#### Option B: Add project to Python path
```bash
# Navigate to the main project directory
cd crewai-stock-trader-agents-main

# Set PYTHONPATH (Windows)
set PYTHONPATH=%PYTHONPATH%;.

# Set PYTHONPATH (Linux/macOS)
export PYTHONPATH="${PYTHONPATH}:."

# Now you can run individual files
python agents/scan_agent.py
```

#### Option C: Use Python module execution
```bash
# From the main project directory
python -m agents.scan_agent
```

### 2. Package Installation Failures

**Error:**
```
ERROR: Could not find a version that satisfies the requirement tvdatafeed>=1.3.0
```

**Solution:** We've updated the requirements to use packages that are actually available on PyPI.

```bash
# Use our updated installer
python install_dependencies.py enhanced

# Or install manually with working packages
pip install lightweight-charts alpha-vantage ta finta
```

### 3. TA-Lib Installation Issues

**Windows:**
1. Download TA-Lib wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install manually:
   ```bash
   pip install TA_Lib-0.4.25-cp311-cp311-win_amd64.whl
   ```
   (adjust filename for your Python version)

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

**Alternative:** If TA-Lib fails, the system will work with the `ta` and `finta` libraries:
```bash
pip install ta finta
```

### 4. API Key Configuration

**Missing API Keys:**
Make sure your `.env` file is properly configured:

```bash
# Copy the template
cp exemple_env_template.txt .env

# Edit with your API keys
# Add your StocksTrader API credentials
# Add Alpha Vantage API key (free tier available)
```

### 5. Virtual Environment Issues

**Recommended Setup:**
```bash
# Create virtual environment
python -m venv trading_env

# Activate (Windows)
trading_env\Scripts\activate

# Activate (Linux/macOS)
source trading_env/bin/activate

# Install dependencies
python install_dependencies.py enhanced
```

### 6. Import Path Issues in IDE

If running from an IDE like VSCode or PyCharm:

1. **VSCode:** Set the workspace folder to `crewai-stock-trader-agents-main`
2. **PyCharm:** Mark the `crewai-stock-trader-agents-main` directory as "Sources Root"
3. **General:** Ensure your Python interpreter is pointing to the correct environment

### 7. Memory/Performance Issues

**Large Model Memory Usage:**
```bash
# Use smaller models for testing
# Edit .env file:
OPENAI_MODEL_NAME=gpt-3.5-turbo  # Instead of gpt-4

# Or use local models with Ollama
# See README.md for Ollama setup
```

### 8. Network/Firewall Issues

**API Connection Problems:**
- Check your firewall settings
- Ensure internet connectivity
- Verify API endpoints are accessible
- Consider using VPN if regional restrictions apply

### 9. Database Errors

**SQLite Database Issues:**
```bash
# Delete corrupted databases (they will be recreated)
rm agent_memory.db
rm web_research_cache.db
rm trading_goals.db
rm agent_learning.db

# Restart the application
python agent_zero_chat.py
```

### 10. Getting Help

**Still having issues?**

1. **Check Requirements:** Ensure all dependencies are installed:
   ```bash
   pip list | grep -E "(crewai|yfinance|pandas|numpy)"
   ```

2. **Verify Python Version:** Requires Python 3.10+
   ```bash
   python --version
   ```

3. **Clean Installation:**
   ```bash
   pip uninstall -r requirements.txt -y
   python install_dependencies.py full
   ```

4. **Run Diagnostics:**
   ```bash
   python -c "import sys; print(f'Python: {sys.version}'); import pandas; print(f'Pandas: {pandas.__version__}'); import crewai; print(f'CrewAI: {crewai.__version__}')"
   ```

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Module not found | Run from project root: `cd crewai-stock-trader-agents-main` |
| Package not found | Use updated installer: `python install_dependencies.py enhanced` |
| TA-Lib fails | Install alternatives: `pip install ta finta` |
| API errors | Check `.env` file configuration |
| Import errors | Set PYTHONPATH or use `python -m` execution |

## Contact Support

If you continue to experience issues:
- Check the README.md for detailed setup instructions
- Review the requirements files for dependency information
- Ensure you're using a supported Python version (3.10+) 