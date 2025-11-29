@echo off
echo ================================
echo Cric Mater Bot - Quick Start
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env >nul
    echo.
    echo [ACTION REQUIRED] Please edit .env file with your credentials:
    echo   1. Discord Bot Token
    echo   2. MongoDB Connection String
    echo   3. Your Discord User ID
    echo.
    echo Press any key to open .env in notepad...
    pause >nul
    notepad .env
)

echo [OK] .env file exists
echo.

REM Check if packages are installed
echo Checking required packages...
pip show discord.py >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
    echo.
) else (
    echo [OK] Packages already installed
)

echo.
echo ================================
echo All checks complete!
echo ================================
echo.
echo Ready to start the bot!
echo.
echo Press any key to start bot.py...
pause >nul

python bot.py
