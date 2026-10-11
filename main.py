"""Entry point for the Time Log Application.

A modern time tracking application with:
- Clock in/out functionality
- Time entry management with validation
- Period-based reporting (custom 15-day billing cycles)
- CSV export capabilities
- Overnight shift support
"""

import tkinter as tk
from tkinter import ttk
from TimeLogApp.time_log_tab import TimeLogTab

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Time Log Application")
        self.geometry("900x700")
        self.minsize(850, 650)

        self.create_widgets()

    # ------------------------------------------------------------------
    def create_widgets(self):
        # Create Time Log tab as the main interface (no notebook needed)
        self.time_log_tab = TimeLogTab(self)
        self.time_log_tab.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
