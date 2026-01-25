@echo off
REM Recommendation Engine - Windows Startup Script

setlocal enabledelayedexpansion

color 0A
cls

echo ======================================
echo  Recommendation Engine - Start Script
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo Error: Python 3 is not installed
    echo Please install from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo Error: Node.js is not installed
    echo Please install from: https://nodejs.org/
    pause
    exit /b 1
)

echo Checking dependencies...
echo - Python: OK
echo - Node.js: OK
echo.

REM Install backend dependencies
if not exist "backend\venv" (
    echo Installing backend dependencies...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    call venv\Scripts\deactivate.bat
    cd ..
    echo - Backend dependencies: OK
) else (
    echo - Backend dependencies: Already installed
)

REM Install frontend dependencies
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install --silent
    cd ..
    echo - Frontend dependencies: OK
) else (
    echo - Frontend dependencies: Already installed
)

echo.
echo ======================================
echo  Starting Servers...
echo ======================================
echo.

REM Start backend
echo Starting backend on http://localhost:8000
start cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start frontend
echo Starting frontend on http://localhost:3000
start cmd /k "cd frontend && npm run dev"

echo.
echo ======================================
echo  Servers Started Successfully!
echo ======================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Close either terminal window to stop a server.
echo Close both to stop the entire application.
echo.
pause
