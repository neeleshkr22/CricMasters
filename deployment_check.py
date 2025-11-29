#!/usr/bin/env python3
"""
Deployment Health Check Script for Cric Masters Bot
Verifies all dependencies and configurations before deployment
"""

import os
import sys
import importlib
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version.major}.{version.minor} (requires 3.8+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_dependencies():
    """Check if all required packages are installed"""
    requirements = [
        'discord.py',
        'python-dotenv', 
        'motor',
        'pymongo',
        'Pillow',
        'aiohttp',
        'dnspython'
    ]
    
    results = []
    for req in requirements:
        module_name = req.replace('-', '_')
        try:
            module = importlib.import_module(module_name.split('.')[0])
            version = getattr(module, '__version__', 'unknown')
            results.append((True, req, version))
        except ImportError:
            results.append((False, req, 'Not installed'))
    
    return results

def check_environment():
    """Check environment variables"""
    required_vars = ['DISCORD_TOKEN', 'MONGODB_URI', 'ADMIN_IDS']
    results = []
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        results.append((True, '.env file', 'Found'))
    else:
        results.append((False, '.env file', 'Missing'))
    
    # Check environment variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
            results.append((True, var, masked_value))
        else:
            results.append((False, var, 'Not set'))
    
    return results

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'bot.py',
        'config.py',
        'requirements.txt',
        'database/db.py',
        'data/players.py',
        'cogs/admin_commands.py',
        'cogs/economy_commands.py',
        'cogs/match_commands.py',
        'utils/match_engine.py',
        'utils/ovr_calculator.py'
    ]
    
    results = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            results.append((True, file_path, f"{size} bytes"))
        else:
            results.append((False, file_path, "Missing"))
    
    return results

def check_data_integrity():
    """Check if data files are properly formatted"""
    results = []
    
    # Check players.py
    try:
        sys.path.append('data')
        from players import get_all_players
        players = get_all_players()
        results.append((True, "Player data", f"{len(players)} players loaded"))
    except Exception as e:
        results.append((False, "Player data", str(e)))
    
    # Check JSON files
    json_files = ['data/celebration_gifs.json', 'data/stadium_gifs.json']
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                results.append((True, json_file, f"{len(data)} entries"))
        except FileNotFoundError:
            results.append((False, json_file, "File not found"))
        except json.JSONDecodeError:
            results.append((False, json_file, "Invalid JSON"))
    
    return results

def print_results(title, results):
    """Print formatted results"""
    print(f"\n{'='*20} {title} {'='*20}")
    
    for success, item, details in results:
        status = "✅" if success else "❌"
        print(f"{status} {item:<25} {details}")
    
    failed = sum(1 for success, _, _ in results if not success)
    if failed == 0:
        print(f"🎉 All checks passed!")
    else:
        print(f"⚠️  {failed} issues found")

def main():
    """Run all deployment checks"""
    print("🚀 Cric Masters Bot - Deployment Health Check")
    print("=" * 50)
    
    # Run all checks
    python_ok, python_info = check_python_version()
    deps = check_dependencies()
    env = check_environment()
    files = check_file_structure()
    data = check_data_integrity()
    
    # Print results
    print(f"\n✅ Python Version: {python_info}" if python_ok else f"\n❌ Python Version: {python_info}")
    
    print_results("Dependencies", deps)
    print_results("Environment", env)
    print_results("File Structure", files)
    print_results("Data Integrity", data)
    
    # Overall assessment
    total_checks = 1 + len(deps) + len(env) + len(files) + len(data)
    failed_checks = (0 if python_ok else 1) + sum(1 for success, _, _ in deps + env + files + data if not success)
    
    print(f"\n{'='*50}")
    if failed_checks == 0:
        print("🎉 DEPLOYMENT READY! All systems operational.")
        print("\n🚀 Next steps:")
        print("1. Choose hosting platform (Railway.app recommended)")
        print("2. Set up MongoDB Atlas database")
        print("3. Deploy and test with 'cmhelp' command")
    else:
        print(f"❌ DEPLOYMENT BLOCKED: {failed_checks}/{total_checks} checks failed")
        print("\n🔧 Fix the issues above before deploying")
    
    print("=" * 50)

if __name__ == "__main__":
    main()