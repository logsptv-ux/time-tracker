#!/usr/bin/env python3
"""
TimeLogApp Installation Script
Installs TimeLogApp with all dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python 3.10+ is installed"""
    if sys.version_info < (3, 10):
        print(f"ERROR: Python 3.10+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return False
    return True

def install_pyside6():
    """Install PySide6 if not already installed"""
    try:
        import PySide6
        print(f"✓ PySide6 already installed: {PySide6.__version__}")
        return True
    except ImportError:
        print("Installing PySide6...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
            print("✓ PySide6 installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: Failed to install PySide6")
            return False

def create_app_directory():
    """Create application directory"""
    if sys.platform == "win32":
        app_dir = Path(os.getenv("PROGRAMFILES")) / "TimeLogApp"
    else:
        app_dir = Path.home() / ".local" / "share" / "TimeLogApp"

    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def copy_app_files(app_dir):
    """Copy application files to installation directory"""
    files_to_copy = [
        "TimeLogApp_PySide6.py",
        "LaunchTimeLogApp.vbs",
        "LaunchTimeLogApp.bat",
        "PYSIDE6_README.md",
        "ULTRA_COMPACT_WIDGET_COMPLETE.md",
        "test_timelogapp.py",
    ]

    source_dir = Path.cwd()
    for file in files_to_copy:
        src = source_dir / file
        dst = app_dir / file
        if src.exists():
            import shutil
            shutil.copy2(src, dst)
            print(f"✓ Copied {file}")
        else:
            print(f"⚠ Skipped {file} (not found)")

def create_shortcuts():
    """Create desktop and start menu shortcuts (Windows)"""
    if sys.platform != "win32":
        return

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")

        app_dir = Path(os.getenv("PROGRAMFILES")) / "TimeLogApp"
        desktop = Path.home() / "Desktop"
        start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "TimeLogApp"

        start_menu.mkdir(parents=True, exist_ok=True)

        # Desktop shortcut
        desktop_link = desktop / "TimeLogApp.lnk"
        shortcut = shell.CreateShortcut(str(desktop_link))
        shortcut.TargetPath = str(app_dir / "LaunchTimeLogApp.vbs")
        shortcut.WorkingDirectory = str(app_dir)
        shortcut.IconLocation = str(app_dir / "TimeLogApp_PySide6.py")
        shortcut.save()
        print(f"✓ Created desktop shortcut")

        # Start menu shortcut
        menu_link = start_menu / "TimeLogApp.lnk"
        shortcut = shell.CreateShortcut(str(menu_link))
        shortcut.TargetPath = str(app_dir / "LaunchTimeLogApp.vbs")
        shortcut.WorkingDirectory = str(app_dir)
        shortcut.save()
        print(f"✓ Created start menu shortcut")
    except Exception as e:
        print(f"⚠ Could not create shortcuts: {e}")

def main():
    print("\n" + "="*60)
    print("TimeLogApp Installer")
    print("="*60 + "\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected\n")

    # Install PySide6
    if not install_pyside6():
        sys.exit(1)
    print()

    # Create app directory
    app_dir = create_app_directory()
    print(f"✓ App directory: {app_dir}\n")

    # Copy files
    copy_app_files(app_dir)
    print()

    # Create shortcuts
    create_shortcuts()
    print()

    print("="*60)
    print("Installation Complete!")
    print("="*60)
    print(f"\nTimeLogApp installed to: {app_dir}")
    print("\nYou can now:")
    print("  • Double-click 'TimeLogApp' on your desktop")
    print("  • Or find it in Start Menu > TimeLogApp")
    print("\nEnjoy your time tracker!\n")

if __name__ == "__main__":
    main()
