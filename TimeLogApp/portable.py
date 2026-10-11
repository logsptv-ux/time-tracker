import sys
import os
from pathlib import Path

def get_base_path():
    """Get the path to the application directory."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller runs from a temp directory
        return Path(sys._MEIPASS)
    else:
        # Standard script execution
        return Path(__file__).resolve().parent.parent

def get_data_dir():
    """Return the path to the writeable data directory."""
    if hasattr(sys, '_MEIPASS'):
        # For an executable, data should be in the user's AppData
        appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        data_dir = appdata / 'TimeLogApp' / 'data'
    else:
        # Standard development
        data_dir = get_base_path() / 'data'

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# Initialize data dir once
DATA_DIR = get_data_dir()
