@echo off
REM ==============================================================================
REM TimeLogApp v2.1 - Setup/Installer
REM ==============================================================================
REM This installer sets up TimeLogApp on a new PC
REM Handles Python verification, dependency installation, and shortcuts
REM ==============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================================
echo   TimeLogApp v2.1 - Setup Wizard
echo ============================================================================
echo.
echo   Modern Time Tracking Application
echo   - Start/Stop Timer for quick entry
echo   - Task Breakdown Chart visualization
echo   - Period-based reporting
echo   - CSV export capabilities
echo.

REM Get installation directory
set "INSTALL_DIR=%~dp0"
set "APP_MODULE=%INSTALL_DIR%TimeLogApp"

echo Installing to: %INSTALL_DIR%
echo.

REM ============================================================================
REM Step 1: Check Python
REM ============================================================================
echo [Step 1/5] Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads
    echo.
    echo IMPORTANT: During installation, check:
    echo   - "Add Python to PATH"
    echo   - "Install pip"
    echo.
    echo After installing Python, run this setup again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [OK] %PYTHON_VERSION%

REM ============================================================================
REM Step 2: Check pip
REM ============================================================================
echo [Step 2/5] Checking pip package manager...

python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    pause
    exit /b 1
)

echo [OK] pip is available

REM ============================================================================
REM Step 3: Create directories
REM ============================================================================
echo [Step 3/5] Creating application directories...

if not exist "%INSTALL_DIR%data" mkdir "%INSTALL_DIR%data"
if not exist "%INSTALL_DIR%data\backups" mkdir "%INSTALL_DIR%data\backups"
if not exist "%INSTALL_DIR%exports" mkdir "%INSTALL_DIR%exports"

echo [OK] Directories created

REM ============================================================================
REM Step 4: Install dependencies
REM ============================================================================
echo [Step 4/5] Installing required packages...

echo   - Installing matplotlib...
python -m pip install matplotlib --quiet 2>nul
if errorlevel 1 (
    echo   [WARNING] Failed to install matplotlib
    echo   The app will have limited chart functionality
) else (
    echo   [OK] matplotlib installed
)

REM ============================================================================
REM Step 5: Create shortcuts and launchers
REM ============================================================================
echo [Step 5/5] Creating shortcuts and launchers...

REM Create run_app.bat in install directory
echo Creating launcher...
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo python main.py
echo if errorlevel 1 (
echo     echo.
echo     echo Error: Application failed to start
echo     pause
echo )
) > "%INSTALL_DIR%run_app.bat"

REM Create Desktop shortcut
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    set "VBS_FILE=%TEMP%\create_shortcut.vbs"
    (
        echo Set oWS = WScript.CreateObject("WScript.Shell"^)
        echo Set oLink = oWS.CreateShortcut("%DESKTOP%\TimeLogApp.lnk"^)
        echo oLink.TargetPath = "%INSTALL_DIR%run_app.bat"
        echo oLink.WorkingDirectory = "%INSTALL_DIR%"
        echo oLink.Description = "TimeLogApp - Modern Time Tracking"
        echo oLink.IconLocation = "C:\Windows\System32\shell32.dll,52"
        echo oLink.Save
    ) > "!VBS_FILE!"

    cscript.exe "!VBS_FILE!" >nul 2>&1
    del "!VBS_FILE!" >nul 2>&1
    echo   [OK] Desktop shortcut created
)

REM Create Start Menu shortcut
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%START_MENU%" (
    set "VBS_FILE=%TEMP%\create_start_menu.vbs"
    (
        echo Set oWS = WScript.CreateObject("WScript.Shell"^)
        echo Set oLink = oWS.CreateShortcut("%START_MENU%\TimeLogApp.lnk"^)
        echo oLink.TargetPath = "%INSTALL_DIR%run_app.bat"
        echo oLink.WorkingDirectory = "%INSTALL_DIR%"
        echo oLink.Description = "TimeLogApp - Modern Time Tracking"
        echo oLink.IconLocation = "C:\Windows\System32\shell32.dll,52"
        echo oLink.Save
    ) > "!VBS_FILE!"

    cscript.exe "!VBS_FILE!" >nul 2>&1
    del "!VBS_FILE!" >nul 2>&1
    echo   [OK] Start Menu shortcut created
)

REM ============================================================================
REM Installation Complete
REM ============================================================================
echo.
echo ============================================================================
echo   Installation Complete!
echo ============================================================================
echo.
echo TimeLogApp v2.1 has been successfully installed.
echo.
echo Launch the app using any of these methods:
echo   1. Desktop shortcut (TimeLogApp.lnk^)
echo   2. Start Menu search (type "TimeLogApp"^)
echo   3. Double-click: run_app.bat in the installation folder
echo.
echo Installation Location: %INSTALL_DIR%
echo Data Location: %INSTALL_DIR%data
echo.
echo Features:
echo   - Start/Stop Timer for quick time tracking
echo   - Task Breakdown Chart showing time distribution
echo   - Period-based reporting and analytics
echo   - CSV export for your data
echo   - Modern dark theme UI
echo.
echo To uninstall: Simply delete the installation folder
echo               (Desktop shortcuts will not auto-remove)
echo.
echo ============================================================================
echo.

timeout /t 2 /nobreak

echo Starting TimeLogApp...
start "" "%INSTALL_DIR%run_app.bat"

exit /b 0
