@echo off
REM Set environment variables
set APP_ENV=development

REM Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Set up environment variables
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please update the .env file with your configuration and press any key to continue...
    pause >nul
)

REM Initialize the database
echo Initializing database...
python init_db.py

REM Start the application
echo Starting ScholarIQ API server...
uvicorn app.main:app --reload

REM Deactivate virtual environment on exit
call deactivate
