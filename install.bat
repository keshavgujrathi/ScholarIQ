@echo off
setlocal enabledelayedexpansion

:: Set colors
for /F "tokens=1,2 delims=#" %%a in ('"%SYSTEMROOT%\System32\prompt $H#$E^| cmd /d /k echo on"') do (set "DEL=%%a")
set "GREEN=%DEL%[32m"
set "YELLOW=%DEL%[33m"
set "NC=%DEL%[0m"

:: Function to print with color
:printc
set "COLOR=%~1"
set "TEXT=%~2"
<nul set /p="!COLOR!"
echo !TEXT!%
<nul set /p="!NC!"
goto :eof

:: Main script
echo Starting ScholarIQ installation...

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%Python is not installed or not in PATH. Please install Python 3.8 or higher and try again.%NC%
    pause
    exit /b 1
)

:: Create virtual environment
echo %GREEN%Creating virtual environment...%NC%
python -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo %GREEN%Upgrading pip...%NC%
python -m pip install --upgrade pip

:: Install production dependencies
echo %GREEN%Installing production dependencies...%NC%
pip install -r requirements.txt

:: Check for --dev flag
if "%~1"=="--dev" (
    echo %GREEN%Installing development dependencies...%NC%
    pip install -r requirements-dev.txt
    
    echo %GREEN%Setting up pre-commit hooks...%NC%
    pre-commit install
)

:: Download spaCy models
echo %GREEN%Downloading spaCy models...%NC%
python -m spacy download en_core_web_sm

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo %GREEN%Creating .env file...%NC%
    copy /y .env.example .env >nul
    echo %YELLOW%Please update the .env file with your configuration.%NC%
)

:: Initialize database
echo %GREEN%Initializing database...%NC%
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())" || (
    echo %YELLOW%Database initialization failed. Make sure your database is running and configured correctly.%NC%
)

echo %GREEN%Installation complete!%NC%
echo %GREEN%To activate the virtual environment, run:%NC% venv\Scripts\activate.bat
echo %GREEN%To start the development server:%NC% uvicorn app.main:app --reload

pause
