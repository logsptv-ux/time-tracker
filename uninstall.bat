@echo off
REM ==============================================================================
REM TimeLogApp v2.1 - Uninstaller
REM ==============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================================================
echo   TimeLogApp v2.1 - Uninstaller
echo ============================================================================
echo.

set "DESKTOP=%USERPROFILE%\Desktop"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

echo This will remove TimeLogApp shortcuts.
echo.
echo Your data files will NOT be deleted.
echo Location: %~dp0data\
echo.
pause

echo.
echo Removing shortcuts...

if exist "%DESKTOP%\TimeLogApp.lnk" (
    del "%DESKTOP%\TimeLogApp.lnk"
    echo [OK] Desktop shortcut removed
)

if exist "%START_MENU%\TimeLogApp.lnk" (
    del "%START_MENU%\TimeLogApp.lnk"
    echo [OK] Start Menu shortcut removed
)

echo.
echo ============================================================================
echo   Uninstall Complete
echo ============================================================================
echo.
echo Shortcuts have been removed.
echo.
echo To fully remove TimeLogApp:
echo   1. Delete the installation folder
echo.
echo To preserve your data before deleting:
echo   1. Copy the 'data' folder to another location
echo   2. Then delete the installation folder
echo.

pause
