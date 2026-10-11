# TimeLogApp - Modern Time Tracking Application

A disciplined, modern desktop application for tracking work time with an intuitive UI, real-time timer, and visual analytics.

## Quick Start

### Easy Launch (Recommended)

**Option 1: Use the Batch File**
1. Double-click `run_timelogapp.bat` in the Desktop folder
2. The app will automatically check dependencies and launch

**Option 2: Create a Shortcut** 
1. Run `create_shortcut.bat` to generate a `.lnk` shortcut file
2. Double-click the `TimeLogApp.lnk` shortcut to launch
3. You can pin this shortcut to Start Menu or Taskbar for quick access

**Option 3: Command Line**
```powershell
cd C:\Users\evang\OneDrive\Desktop
python main.py
```

## Features

### Core Functionality
- **Clock In/Clock Out** - Traditional time tracking buttons
- **Start/Stop Timer** - New quick-entry timer for easy tracking
  - Click "▶ Start Timer" to begin
  - Timer displays elapsed time in HH:MM:SS format
  - Click "⏹ Stop & Save" to auto-save the entry
  - Click "✕ Reset" to clear without saving
- **Time Entry Management** - Add, edit, and delete time entries
- **Overnight Shift Support** - Properly handles shifts crossing midnight
- **Overlap Detection** - Prevents conflicting time entries

### Analytics & Visualization
- **Task Breakdown Chart** - Pie chart showing time spent per task
- **Period Summary** - Statistics for selected time period
- **Daily Breakdown** - View hours logged per day
- **Trend Analysis** - Projected totals and confidence indicators
- **CSV Export** - Export time entries for external analysis

### Modern UI
- **Dark Theme** - Easy on the eyes, professional appearance
- **Responsive Design** - Works on different screen sizes
- **Intuitive Layout** - Organized sections for easy navigation
- **Live Clock** - Current time display at the top
- **Period Selector** - Switch between billing cycles quickly

### Data Management
- **Automatic Backups** - Keeps last 10 backups of your data
- **JSON Storage** - Human-readable data format
- **Data Validation** - Ensures data integrity
- **Search & Filter** - Find entries by task or date

## UI Sections

### Header
- **Brand**: "Time Log" title
- **Period Display**: Current 15-day billing cycle
- **Live Clock**: Real-time hour:minute:second display

### New Entry Form
- **Date**: Entry date (YYYY-MM-DD format)
- **Task**: What you worked on
- **Time In/Out**: Specific times or use Clock In/Clock Out buttons
- **Quick Timer**: NEW! Start/Stop/Reset buttons for easy tracking
- **Save/Clear**: Save entry or clear the form

### Active Session
- Shows currently pending work session
- Complete Session or Cancel buttons
- Displays elapsed time for active work

### Task Breakdown Chart
- Visual pie chart of time per task
- Updates when you change the period
- Shows percentage breakdown
- Entries from the timer appear here

### Time Entries
- Searchable/filterable list of all entries
- Sort by Date, Task, Time In, Time Out, Duration
- Double-click to edit an entry
- Delete button for removing entries
- Entry count display

### Period Summary
- Total hours for the period
- Days worked
- Number of entries
- Average hours per day
- Projected total with confidence level
- Daily breakdown table

## File Structure

```
C:\Users\evang\OneDrive\Desktop\
├── main.py                          # Application entry point
├── run_timelogapp.bat               # Easy launcher (double-click to run)
├── create_shortcut.bat              # Creates Windows shortcut
├── TimeLogApp/
│   ├── __init__.py
│   ├── time_log_tab.py              # Main UI (contains timer feature)
│   ├── domain.py                    # Business logic & validation
│   ├── store.py                     # Data persistence (JSON)
│   ├── analytics.py                 # Chart & statistics calculations
│   └── README.md                    # Module documentation
├── data/
│   ├── time_log.json                # Your time entries (auto-created)
│   └── backups/                     # Automatic backups (auto-created)
└── exports/                         # CSV exports (created when you export)
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save Entry |
| **Ctrl+I** | Clock In (sets Time In to now) |
| **Ctrl+O** | Clock Out (sets Time Out to now) |
| **Ctrl+E** | Export to CSV |
| **Ctrl+Backspace** | Delete Selected Entry |
| **Enter** | Submit entry from Task field |

## Using the Timer Feature (New!)

### Quick Entry with Timer

1. **Start Timing**
   - Enter your task name (required)
   - Optionally adjust the date (defaults to today)
   - Click **▶ Start Timer**
   - Time In is automatically set to current time
   - Timer display shows "00:00:00" and begins counting

2. **Work**
   - Timer updates every second showing elapsed time
   - E.g., "00:05:23" after 5 minutes and 23 seconds
   - Display is in amber color for visibility

3. **Stop and Save**
   - When finished, click **⏹ Stop & Save**
   - Time Out automatically set to current time
   - Entry is automatically saved with full validation
   - Entry appears immediately in Time Entries list
   - Timer resets

4. **Alternative: Reset Without Saving**
   - If you change your mind, click **✕ Reset**
   - Confirmation dialog appears
   - If you confirm, timer clears without saving
   - No data is recorded

### Timer Features
- **Validation**: Task name required, date format checked
- **Auto-Save**: Stops timer and saves entry in one click
- **Overlap Detection**: Saved entries checked for conflicts
- **Error Handling**: Clear error messages if something fails
- **Button State Management**: Buttons enable/disable appropriately

## Data Format

### Time Entry (JSON)
```json
{
  "id": "uuid-string",
  "date": "2026-09-28",
  "task": "Development",
  "time_in": "2026-09-28T14:30",
  "time_out": "2026-09-28T15:45"
}
```

### Time Format
All times use 24-hour format internally, displayed as 12-hour AM/PM in the UI:
- **Stored**: "2026-09-28T14:30" (24-hour format)
- **Displayed**: "02:30 PM" (12-hour format with AM/PM)

## Common Tasks

### View Time for a Specific Period
1. Click the period dropdown (top right of Time Entries section)
2. Select the desired period
3. Chart and summary automatically update

### Export Your Time Entries
1. Select the desired period
2. Click "Export CSV" button
3. File saved to `C:\Users\evang\OneDrive\Desktop\exports\`

### Backup Your Data
1. Click "Backup" button in summary section
2. Backup saved to `data/backups/` directory
3. Last 10 backups automatically kept

### Edit an Entry
1. Click on an entry in the Time Entries list (or double-click)
2. Entry details appear in the New Entry form
3. Yellow "✏ Editing" badge appears
4. Make changes and click Save

### Delete an Entry
1. Click on an entry in the Time Entries list to select it
2. Click "Delete Selected" button
3. Confirm deletion
4. Entry is removed

## Requirements

- **Python 3.8+** - Download from https://www.python.org
- **matplotlib** - Installed automatically by launcher
- **Windows 10/11** - Tested on these versions

## Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://www.python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installing

### "Application failed to start"
- Check that TimeLogApp folder exists
- Verify all files are in the correct location
- Try running from command line to see error message:
  ```powershell
  cd C:\Users\evang\OneDrive\Desktop
  python main.py
  ```

### "matplotlib not found"
- The launcher tries to install it automatically
- If it fails, install manually:
  ```powershell
  pip install matplotlib
  ```

### Data Not Showing
- Check that `data/time_log.json` exists
- File is created automatically on first run
- If missing, just add an entry to create it

### Timer Not Working
- Ensure task name is entered (required)
- Check that date is in YYYY-MM-DD format
- Make sure you have at least 1 second of elapsed time before stopping

## Data Location

- **Entries**: `C:\Users\evang\OneDrive\Desktop\data\time_log.json`
- **Backups**: `C:\Users\evang\OneDrive\Desktop\data\backups\`
- **Exports**: `C:\Users\evang\OneDrive\Desktop\exports\`

All data is stored locally on your computer. No internet connection required.

## Recent Updates

### Version 2.1 (September 28, 2026)
- **NEW**: Start/Stop Timer feature for quick entry
- **NEW**: Task Breakdown Chart (pie chart visualization)
- **IMPROVED**: Modern dark theme with refined styling
- **FIXED**: Bug preventing multiple entries for same task on same date
- **IMPROVED**: Better error handling and validation messages

### What's New in Timer Feature
- One-click timer with elapsed time display
- Auto-save on stop with full validation
- Confirmation dialog on reset
- Live 1-second updates
- Amber-colored display for visibility
- Smart button state management

## Getting Help

### Check the Logs
When running from command line, error messages display:
```powershell
python main.py
```

### Review Documentation
- `DEBUG_AND_TEST_COMPLETE.md` - Detailed test results
- `FINAL_TEST_REPORT.md` - Comprehensive feature documentation
- `TEST_REPORT.md` - Original test report

### Contact
For issues or feature requests, check the application logs or review the test documentation for troubleshooting steps.

## Development

### Project Structure
- **time_log_tab.py** - Main UI controller with timer feature
- **domain.py** - Business logic and validation
- **store.py** - Data persistence with atomic writes
- **analytics.py** - Statistics and chart data calculations

### Testing
Comprehensive test suite includes:
- 49/50 tests passing (98% success rate)
- Structural verification
- Functional simulation
- Integration testing
- No conflicts with existing features

### Build & Run from Source
```powershell
cd C:\Users\evang\OneDrive\Desktop
python -m venv venv              # Create virtual environment (optional)
.\venv\Scripts\activate          # Activate (if created)
pip install matplotlib            # Install dependencies
python main.py                    # Run application
```

## License

This application is for personal use. All rights reserved.

---

**Ready to track your time?**

1. Double-click `run_timelogapp.bat` to launch
2. Or run `python main.py` from the command line
3. Start tracking with the new timer feature!

**Version**: 2.1 | **Last Updated**: September 28, 2026
