; TimeLogApp Installer Script (NSIS)
; This script creates an installer for TimeLogApp with PySide6

!include "MUI2.nsh"
!include "x64.nsh"

; Define installer name and file
Name "TimeLogApp"
OutFile "TimeLogApp_Installer.exe"
InstallDir "$PROGRAMFILES\TimeLogApp"

; Request admin privileges
RequestExecutionLevel admin

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
    SetOutPath "$INSTDIR"

    ; Copy application files
    File "TimeLogApp_PySide6.py"
    File "LaunchTimeLogApp.vbs"
    File "LaunchTimeLogApp.bat"
    File "PYSIDE6_README.md"
    File "ULTRA_COMPACT_WIDGET_COMPLETE.md"
    File "test_timelogapp.py"

    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\TimeLogApp"
    CreateShortcut "$SMPROGRAMS\TimeLogApp\TimeLogApp.lnk" "$INSTDIR\LaunchTimeLogApp.vbs" "" "$INSTDIR\LaunchTimeLogApp.vbs" 0
    CreateShortcut "$SMPROGRAMS\TimeLogApp\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

    ; Create desktop shortcut
    CreateShortcut "$DESKTOP\TimeLogApp.lnk" "$INSTDIR\LaunchTimeLogApp.vbs" "" "$INSTDIR\LaunchTimeLogApp.vbs" 0

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Write installation info to registry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TimeLogApp" \
        "DisplayName" "TimeLogApp - Time Tracker"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TimeLogApp" \
        "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TimeLogApp" \
        "DisplayVersion" "1.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TimeLogApp" \
        "Publisher" "TimeLogApp"

    MessageBox MB_INFORMATION "TimeLogApp installed successfully!$\n$\nPlease ensure Python 3.10+ and PySide6 are installed.$\n$\nRun: pip install PySide6"
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove installed files
    Delete "$INSTDIR\TimeLogApp_PySide6.py"
    Delete "$INSTDIR\LaunchTimeLogApp.vbs"
    Delete "$INSTDIR\LaunchTimeLogApp.bat"
    Delete "$INSTDIR\PYSIDE6_README.md"
    Delete "$INSTDIR\ULTRA_COMPACT_WIDGET_COMPLETE.md"
    Delete "$INSTDIR\test_timelogapp.py"
    Delete "$INSTDIR\uninstall.exe"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\TimeLogApp\TimeLogApp.lnk"
    Delete "$SMPROGRAMS\TimeLogApp\Uninstall.lnk"
    RMDir "$SMPROGRAMS\TimeLogApp"
    Delete "$DESKTOP\TimeLogApp.lnk"

    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TimeLogApp"

    ; Remove installation directory
    RMDir "$INSTDIR"

    MessageBox MB_INFORMATION "TimeLogApp uninstalled successfully!"
SectionEnd
