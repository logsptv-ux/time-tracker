@echo off
REM ==============================================================================
REM TimeLogApp - Packaging Script for Portable Distribution
REM ==============================================================================
echo Creating portable distribution...

if exist dist_portable rmdir /s /q dist_portable
mkdir dist_portable

REM Copy necessary files
copy main.py dist_portable\
copy requirements.txt dist_portable\
copy setup.bat dist_portable\
xcopy /e /i TimeLogApp dist_portable\TimeLogApp\

REM Create ZIP file using PowerShell
echo Zipping files...
powershell -Command "Compress-Archive -Path 'dist_portable\*' -DestinationPath 'TimeLogApp_Portable.zip' -Force"

echo Portable distribution created: TimeLogApp_Portable.zip
echo Cleanup...
rmdir /s /q dist_portable
echo Done.
pause
