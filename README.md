# TimeLogApp Release Package

This is the official TimeLogApp installer and source code repository.

## Quick Start

### Option 1: Silent Launch (Recommended)
```bash
LaunchTimeLogApp.vbs
```
Double-click to start the app without any setup.

### Option 2: Install & Run
```bash
python setup.py
```

### Option 3: Direct Launch
```bash
python TimeLogApp_PySide6.py
```

## Files Included

- **TimeLogApp_PySide6.py** - Main application (1000+ lines, production-ready)
- **LaunchTimeLogApp.vbs** - Silent launcher (no cmd window)
- **LaunchTimeLogApp.bat** - Batch launcher with console output
- **setup.py** - Installation script with dependency management
- **test_timelogapp.py** - 5 comprehensive tests (all passing ✓)
- **Documentation**
  - INSTALL.md - Installation guide
  - PYSIDE6_README.md - PySide6 setup documentation
  - ULTRA_COMPACT_WIDGET_COMPLETE.md - Feature specification

## Requirements

- Python 3.10+
- PySide6 (auto-installed by setup.py)
- Windows 10+ recommended

## Features

✓ **Ultra-Compact Widget Mode** (380×200 px)
- Professional dark theme
- Start/Pause/Stop/Reset timer controls
- Quick activity entry
- Fullscreen toggle (▼ button)

✓ **Fullscreen Mode**
- Complete entry form with Time In/Out fields
- Today's activity log with sorting
- Statistics (today, this week, entry count)
- Full-featured time tracking

✓ **Data Persistence**
- Automatic save to ~/.timelogapp/data.json
- Survives app restart
- JSON format with full entry details

✓ **Dark Theme**
- Eye-friendly professional palette
- High contrast text
- Consistent styling throughout

## Version History

**v1.0.0** (Current)
- ✓ Widget mode: 380×200 pixels
- ✓ Fullscreen mode: True fullscreen
- ✓ All buttons display properly
- ✓ Save Entry button positioned correctly
- ✓ Time In/Out fields properly sized
- ✓ 5/5 tests passing
- ✓ Production-ready

## Installation Steps

### Windows

1. **Download** all files to a folder
2. **Run installer**: `python setup.py`
   - Or double-click `LaunchTimeLogApp.vbs` to start immediately
3. **Shortcuts created**:
   - Desktop shortcut
   - Start Menu entry
4. **Done!** The app is ready to use

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "PySide6 not found" | `pip install PySide6` |
| "Python not found" | Install Python 3.10+ from python.org |
| App won't launch | Run `LaunchTimeLogApp.bat` to see errors |
| Permission denied | Run setup.py as Administrator |

## Usage Guide

### Widget Mode (Default)
1. Type activity name
2. Click ▶ Start timer
3. Click ⏸ Pause when needed
4. Click ⏹ Stop & save entry
5. Click ✕ Reset timer
6. Click ▲ Go fullscreen

### Fullscreen Mode
1. Use the entry form to manually log times
2. View all entries in Today's Log table
3. Check statistics dashboard
4. Click ▼ Return to widget mode

## Technical Details

### Architecture
- **Framework**: PySide6 (Qt for Python)
- **UI Mode**: Borderless, draggable window
- **Data Storage**: JSON files in ~/.timelogapp/
- **Theme**: Custom dark palette

### Directory Structure
```
~/.timelogapp/
├── data.json       (all time entries)
└── config.json     (window state & preferences)
```

### Entry Schema
```json
{
  "date": "2026-10-26",
  "task": "Activity Name",
  "time_in": "09:00",
  "time_out": "10:30",
  "duration": "1h 30m",
  "id": "timestamp"
}
```

## Testing

All tests pass ✓

```bash
python test_timelogapp.py
```

Tests verify:
1. Data persistence & loading
2. Duration calculations
3. Multiple entries
4. File integrity
5. Entry serialization

## License

TimeLogApp v1.0.0 - Production Ready

---

**Support**: For issues or feature requests, check the documentation or review the code comments in TimeLogApp_PySide6.py
