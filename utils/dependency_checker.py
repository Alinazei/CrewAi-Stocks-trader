#!/usr/bin/env python3
"""
Dependency Checker Utility
Simple utility to check if required packages are installed
"""

import importlib
import sys
from typing import List, Dict, Tuple

def check_required_packages() -> Tuple[List[str], List[str]]:
    """
    Check if required packages are installed.
    
    Returns:
        Tuple of (installed_packages, missing_packages)
    """
    required_packages = [
        'crewai',
        'yfinance', 
        'pandas',
        'numpy',
        'requests',
        'python-dotenv',
        'pytz',
        'textblob'
    ]
    
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            # Handle package name variations
            import_name = package
            if package == 'python-dotenv':
                import_name = 'dotenv'
            
            importlib.import_module(import_name)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    return installed, missing

def print_dependency_status():
    """Print the status of all required dependencies"""
    installed, missing = check_required_packages()
    
    print("📦 **DEPENDENCY STATUS**")
    print("=" * 30)
    
    if installed:
        print(f"\n✅ **Installed ({len(installed)}):**")
        for package in installed:
            print(f"  • {package}")
    
    if missing:
        print(f"\n❌ **Missing ({len(missing)}):**")
        for package in missing:
            print(f"  • {package}")
        
        print(f"\n💡 **To install missing packages:**")
        print(f"pip install {' '.join(missing)}")
    else:
        print(f"\n🎉 **All required packages are installed!**")
    
    return len(missing) == 0

def ensure_dependencies() -> bool:
    """
    Ensure all required dependencies are installed.
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    installed, missing = check_required_packages()
    
    if missing:
        print(f"⚠️  Missing required packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True

if __name__ == "__main__":
    print_dependency_status() 