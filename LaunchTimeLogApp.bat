@echo off
REM ============================================================================
REM TimeLogApp - PySide6 Launcher
REM ============================================================================
REM This batch file launches the PySide6 version of TimeLogApp
REM It checks for Python and PySide6, installs if needed, then launches the app
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors for output (Windows 10+)
cls
echo.
echo ============================================================================
echo                    TimeLogApp - PySide6 Launcher
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
echo [OK] Python found: %PYTHON_VERSION%
echo.

REM Check if PySide6 is installed
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PySide6 is not installed. Installing now...
    echo.
    pip install PySide6
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install PySide6
        echo.
        echo Try running:
        echo   pip install PySide6
        echo.
        pause
        exit /b 1
    )
)

REM Verify PySide6 installation
python -c "import PySide6; print('PySide6 version:', PySide6.__version__)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PySide6 installation failed
    echo.
    pause
    exit /b 1
)

echo [OK] PySide6 is installed
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Check if TimeLogApp_PySide6.py exists
if not exist "%SCRIPT_DIR%TimeLogApp_PySide6.py" (
    echo [ERROR] TimeLogApp_PySide6.py not found in:
    echo %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

echo [INFO] Launching TimeLogApp PySide6...
echo.
echo ============================================================================
echo.

REM Launch the TimeLogApp
cd /d "%SCRIPT_DIR%"
python TimeLogApp_PySide6.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo [ERROR] TimeLogApp failed to launch
    echo ============================================================================
    echo.
    pause
    exit /b 1
)

exit /b 0
