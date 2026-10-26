# TimeLogApp - PySide6 Version

A beautiful, modern time tracking desktop application built with PySide6.

## Installation

### Prerequisites
- Python 3.10+
- PySide6

### Setup

```bash
# Install PySide6
pip install PySide6

# Run the application
python TimeLogApp_PySide6.py
```

## Features

### Core Functionality
- **Timer**: Start, pause, stop, and reset a real-time timer
- **Manual Entries**: Add time entries with custom times
- **Persistent Storage**: All entries saved locally
- **Statistics**: Daily and weekly time summaries
- **Entry Logging**: View all time entries in a clean table

### Design
- **Minimalist Black & White**: Clean, professional aesthetic
- **Responsive Layout**: Scalable window with proper spacing
- **Modern Components**: Native PySide6 widgets with custom styling
- **System Clock**: Real-time clock display in the header
- **Task Management**: Quick entry creation with validation

## Usage

### Adding Time with Timer
1. Enter a task name in "New Entry" section
2. Click "▶ Start" to begin timing
3. Click "⏸ Pause" to pause (click ▶ Start to resume)
4. Click "⏹ Stop" to save the entry automatically
5. Or click "✕ Reset" to discard

### Manual Entry
1. Fill in Task Name, Time In (HH:MM), and Time Out (HH:MM)
2. Click "Save Entry"
3. Entry appears in the table

### View Statistics
- **Today**: Total hours and minutes for today
- **This Week**: Total hours and minutes for the last 7 days
- **Entries**: Number of entries today

## Data Storage

Data is stored in `~/.timelogapp/data.json` (your user home directory).

## Architecture

- **TimeEntry**: Data model for individual entries
- **TimeLogData**: Handles persistence (load/save)
- **TimeLogApp**: Main UI window with all components
- **Theme**: Color palette configuration
- **StyleSheet**: Global CSS styling

## Keyboard Shortcuts

- `Ctrl+S`: Save entry (manual entry form)
- `Ctrl+Q`: Quit application

## File Structure

```
TimeLogApp_PySide6.py
├── Theme (colors and palette)
├── StyleSheet (global styles)
├── TimeEntry (data model)
├── TimeLogData (persistence)
└── TimeLogApp (main window)
```

## Customization

### Change Colors
Edit the `Theme` class at the top of the file:
```python
class Theme:
    BG_PRIMARY = "#ffffff"      # Main background
    ACCENT = "#000000"          # Button and accent color
    # ... other colors
```

### Adjust Window Size
Change the default geometry in `TimeLogApp.__init__()`:
```python
self.setGeometry(100, 100, 1000, 800)  # x, y, width, height
```

## Requirements

- PySide6 (Qt for Python)
- Python 3.10 or higher
- Cross-platform (Windows, macOS, Linux)

## Performance

The application is lightweight and runs efficiently with:
- Minimal memory footprint
- Instant timer updates
- Fast data persistence
- Smooth UI interactions

Enjoy your time tracking!
