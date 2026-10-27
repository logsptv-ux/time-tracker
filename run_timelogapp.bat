@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM TimeLogApp Launcher - Enhanced Version
REM ==============================================================================
REM This batch file launches the Time Log Application with error checking
REM and automatic dependency installation
REM ==============================================================================

cls
echo.
echo ============================================================================
echo   TimeLogApp Launcher
echo ============================================================================
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"
set "APP_DIR=%cd%"

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [OK] %PYTHON_VERSION%

REM Check if main.py exists
echo Checking main.py...
if not exist "main.py" (
    echo.
    echo ERROR: main.py not found in:
    echo %APP_DIR%
    echo.
    pause
    exit /b 1
)
echo [OK] main.py found

REM Check if TimeLogApp directory exists
echo Checking TimeLogApp module...
if not exist "TimeLogApp" (
    echo.
    echo ERROR: TimeLogApp directory not found
    echo.
    pause
    exit /b 1
)
echo [OK] TimeLogApp module found

REM Check if matplotlib is installed, install if missing
echo Checking dependencies...
python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [!] matplotlib not found, installing...
    python -m pip install matplotlib --quiet
    if errorlevel 1 (
        echo [!] Warning: Could not install matplotlib automatically
        echo     The app will have limited chart functionality
    ) else (
        echo [OK] matplotlib installed successfully
    )
) else (
    echo [OK] matplotlib already installed
)

REM All checks passed, launch the app
echo.
echo ============================================================================
echo   Starting TimeLogApp...
echo ============================================================================
echo.
echo Features:
echo   - Clock In/Clock Out time tracking
echo   - Start/Stop Timer for quick entry
echo   - Task Breakdown Chart (pie chart visualization)
echo   - Period-based reporting
echo   - CSV export
echo   - Modern dark theme UI
echo.
echo ============================================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: Application failed to start
    echo ============================================================================
    echo.
    pause
    exit /b 1
)

exit /b 0
