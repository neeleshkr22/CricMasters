@echo off
echo 🚀 Setting up Cric Masters Bot for deployment...
echo.

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Run health check
echo 🔍 Running deployment health check...
python deployment_check.py

echo.
echo ✅ Setup complete! 
echo.
echo 📋 Next steps:
echo 1. Create .env file with your tokens
echo 2. Choose hosting platform (Railway.app recommended)
echo 3. Deploy and test!
echo.
pause