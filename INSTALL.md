# TimeLogApp - Installer & Setup Guide

## Quick Start

### Option 1: Simple Launch (Recommended)
Double-click `LaunchTimeLogApp.vbs` to start the app immediately without any installation.

### Option 2: Python Installation
```bash
python setup.py
```

### Option 3: Manual Setup
```bash
pip install PySide6
python TimeLogApp_PySide6.py
```

---

## Installation Methods

### Windows Desktop
1. Download all files to a folder
2. Ensure Python 3.10+ is installed
3. Run `setup.py` or double-click `LaunchTimeLogApp.vbs`

### Requirements
- Python 3.10+
- PySide6 (`pip install PySide6`)
- Windows 10+ (for best experience)

### What Gets Installed
- Main application: `TimeLogApp_PySide6.py`
- Launchers: `LaunchTimeLogApp.vbs`, `LaunchTimeLogApp.bat`
- Documentation: README files
- Tests: `test_timelogapp.py`

---

## Directory Structure

```
TimeLogApp/
├── TimeLogApp_PySide6.py          # Main application
├── LaunchTimeLogApp.vbs            # Silent launcher (recommended)
├── LaunchTimeLogApp.bat            # Batch launcher with console
├── setup.py                        # Installation script
├── test_timelogapp.py              # Test suite
├── PYSIDE6_README.md               # PySide6 documentation
├── ULTRA_COMPACT_WIDGET_COMPLETE.md # Feature guide
└── TimeLogApp_Installer.nsi        # NSIS installer script
```

---

## Features

✓ **Ultra-Compact Widget Mode** (380×200 px)
- Timer display
- Control buttons (Start, Pause, Stop, Reset)
- Quick entry field
- Minimize & Close buttons
- Fullscreen toggle

✓ **Fullscreen Mode**
- Complete time entry form
- Today's log table
- Statistics dashboard
- All features accessible

✓ **Dark Theme**
- Professional dark palette
- Easy on the eyes
- High contrast text

✓ **Data Persistence**
- All entries saved automatically
- Survives app restart
- Data stored in `~/.timelogapp/data.json`

---

## Usage

### Widget Mode (Default)
1. Type activity name in the input field
2. Click ▶ to start timer
3. Click ⏸ to pause
4. Click ⏹ to save entry
5. Click ✕ to reset

### Fullscreen Mode
1. Click ▲ (maximize button) to go fullscreen
2. Use entry form for manual time entries
3. View all entries in Today's Log
4. Check statistics
5. Click ▼ to return to widget mode

---

## Troubleshooting

### "PySide6 not found"
```bash
pip install PySide6
```

### "Python not found"
Install Python 3.10+ from [python.org](https://www.python.org)

### App won't launch
- Check Python is in PATH: `python --version`
- Verify PySide6 is installed: `pip list | grep PySide6`
- Try using `LaunchTimeLogApp.bat` to see error messages

---

## Version
**TimeLogApp v1.0.0** - Production Ready ✓

All 5 core tests passing (100%)
