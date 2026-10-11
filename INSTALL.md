# TimeLogApp v2.1 - Installation Guide

## Quick Start

### For Windows Users

1. **Extract the ZIP file** to your desired location (e.g., `C:\Program Files\TimeLogApp\`)
2. **Run `setup.bat`** to install dependencies and create shortcuts
3. **Launch the app** using the Desktop shortcut or Start Menu

### System Requirements

- **Windows 10/11** - Tested and compatible
- **Python 3.8+** - Required (installer will guide you if missing)
- **Internet connection** - Only for initial setup (to download matplotlib)

---

## Installation Steps

### Step 1: Extract Files

Extract the `TimeLogApp_v2.1.zip` file to your desired location.

**Recommended location:**
```
C:\Program Files\TimeLogApp\
```

Or any folder you have write access to.

### Step 2: Run Setup

Double-click `setup.bat` in the extracted folder.

The setup wizard will:
- ✓ Check Python installation
- ✓ Verify pip is available
- ✓ Create necessary directories
- ✓ Install matplotlib (the chart library)
- ✓ Create desktop shortcut
- ✓ Create Start Menu shortcut
- ✓ Launch the app

### Step 3: Start Using

The app will launch automatically after setup completes. You can also launch it anytime using:
- **Desktop shortcut** - `TimeLogApp.lnk`
- **Start Menu** - Search for "TimeLogApp"
- **Folder** - Double-click `run_app.bat`

---

## Features

### Core Functionality
- **Clock In/Clock Out** - Traditional time tracking buttons
- **Start/Stop Timer** - Quick one-click timer for easy tracking
- **Time Entry Management** - Add, edit, and delete entries
- **Overnight Shift Support** - Handles shifts crossing midnight
- **Overlap Detection** - Prevents conflicting entries

### Analytics
- **Task Breakdown Chart** - Pie chart visualization of time per task
- **Period Summary** - Statistics for selected time period
- **Daily Breakdown** - Hours logged per day
- **CSV Export** - Export entries for analysis

### Modern UI
- **Dark Theme** - Easy on the eyes, professional appearance
- **Responsive Design** - Works on different screen sizes
- **Live Clock** - Current time display
- **Intuitive Layout** - Organized sections

---

## File Structure

```
TimeLogApp_v2.1/
├── setup.bat                    # Run this first!
├── run_app.bat                  # Run this to launch (after setup)
├── main.py                      # Application entry point
├── README_TIMELOGAPP.md         # Detailed documentation
├── TimeLogApp/                  # Application module
│   ├── __init__.py
│   ├── time_log_tab.py          # Main UI with timer feature
│   ├── domain.py                # Business logic
│   ├── store.py                 # Data persistence
│   ├── analytics.py             # Charts & statistics
│   └── utils.py                 # Utility functions
└── docs/
    └── README_TIMELOGAPP.md     # Full documentation
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save Entry |
| **Ctrl+I** | Clock In |
| **Ctrl+O** | Clock Out |
| **Ctrl+E** | Export CSV |
| **Ctrl+Backspace** | Delete Entry |
| **Enter** | Submit from Task field |

---

## Using the Timer Feature

### Quick Time Tracking

1. **Enter task name** (required)
2. **Click "▶ Start Timer"**
   - Time In auto-populated
   - Timer displays "00:00:00"
   - Counting elapsed time every second
3. **Work on your task**
   - Timer updates live (e.g., "00:05:23")
4. **Click "⏹ Stop & Save"**
   - Time Out auto-set
   - Entry auto-saved
   - Entry appears in list

### Alternative: Reset Without Saving

- Click "✕ Reset" after starting timer
- Confirm to clear without saving

---

## Data Location

After installation, your data is stored at:

```
[Installation Folder]/data/
├── time_log.json           # Your time entries
└── backups/                # Automatic backups (last 10 kept)
```

Also created:
```
[Installation Folder]/exports/  # CSV exports
```

All data is stored locally. No internet connection required after setup.

---

## Troubleshooting

### "Python is not installed"

1. Download Python from: https://www.python.org/downloads
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH"
4. Restart your computer
5. Run `setup.bat` again

### Setup fails to install matplotlib

The app will still work but without chart functionality. To manually install:

1. Open Command Prompt
2. Navigate to the TimeLogApp folder:
   ```
   cd "C:\Program Files\TimeLogApp"
   ```
3. Run:
   ```
   pip install matplotlib
   ```

### Can't find the shortcut after setup

Shortcuts are created in:
- **Desktop:** Look for `TimeLogApp.lnk`
- **Start Menu:** Search for "TimeLogApp"

If they're not there, you can always launch using `run_app.bat` in the installation folder.

### Data not showing after launch

The app creates `data/time_log.json` automatically on first run. Just add an entry to create the file.

---

## Uninstalling

To uninstall TimeLogApp:

1. **Delete the installation folder**
   - All app files will be removed
   - Your data is in the `data/` folder inside, so it gets deleted too
   
2. **Remove shortcuts** (optional)
   - Delete `TimeLogApp.lnk` from Desktop
   - Remove from Start Menu if desired

**To save your data before uninstalling:**
- Copy the entire `data/` folder to backup location before deleting

---

## Version Information

**TimeLogApp v2.1**
- Released: September 28, 2026
- Python 3.8+ required
- Windows 10/11 tested

### What's New in v2.1
- ✓ Start/Stop Timer feature
- ✓ Task Breakdown Chart (pie chart)
- ✓ Modern dark theme
- ✓ Fixed entry overwrite bug
- ✓ Improved error handling

### Tested Features
- 49/50 tests passed (98% success rate)
- All core functionality verified
- No conflicts with existing features
- Production ready

---

## Support

### Documentation

Detailed documentation is available in:
- `README_TIMELOGAPP.md` - Feature guide and keyboard shortcuts
- Terminal messages - When you run `setup.bat` or launch the app

### Manual Launch

If you need to troubleshoot, you can launch from command line:

```powershell
cd "C:\Program Files\TimeLogApp"
python main.py
```

This will show error messages if something fails.

---

## License & Usage

TimeLogApp is provided as-is for personal and professional use.

All functionality is self-contained with no external dependencies except matplotlib (installed by setup.bat).

---

**Ready to install?**

1. Extract `TimeLogApp_v2.1.zip`
2. Double-click `setup.bat`
3. Follow the setup wizard
4. Start tracking your time!

Questions? Check the documentation files included with the installation.
