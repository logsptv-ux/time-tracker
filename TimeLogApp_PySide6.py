"""
TimeLogApp - PySide6 Version with Widget Mode (Ultra-Compact)
A beautiful, modern time tracking application with minimalist dark design.
Features: Ultra-compact widget mode and full-featured mode with toggle.
"""

import sys
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QFrame, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QTime, QPoint
from PySide6.QtGui import QFont


# ============================================================================
# Configuration & Constants
# ============================================================================

class Theme:
    """Dark mode color theme"""
    BG_PRIMARY = "#1a1a1a"
    BG_SECONDARY = "#2d2d2d"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#aaaaaa"
    BORDER = "#444444"
    ACCENT = "#ffffff"
    HOVER_BG = "#333333"


class StyleSheet:
    """Global stylesheets for the application - Full dark mode"""

    @staticmethod
    def get_main_stylesheet():
        return """
            QMainWindow {
                background-color: """ + Theme.BG_PRIMARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QWidget {
                background-color: """ + Theme.BG_PRIMARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QFrame#header {
                background-color: """ + Theme.BG_SECONDARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
                padding: 8px;
                border-radius: 0px;
                border-bottom: 2px solid """ + Theme.BORDER + """;
            }

            QLabel {
                background-color: transparent;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QLabel#label-secondary {
                font-size: 11px;
                color: """ + Theme.TEXT_SECONDARY + """;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            QPushButton {
                background-color: """ + Theme.BG_SECONDARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
                border: 1px solid """ + Theme.BORDER + """;
                border-radius: 4px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                min-width: 60px;
                min-height: 36px;
            }

            QPushButton:hover {
                background-color: """ + Theme.HOVER_BG + """;
                border: 1px solid """ + Theme.TEXT_SECONDARY + """;
            }

            QPushButton:pressed {
                background-color: """ + Theme.BG_PRIMARY + """;
            }

            QLineEdit {
                background-color: """ + Theme.BG_SECONDARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
                border: 1px solid """ + Theme.BORDER + """;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }

            QLineEdit:focus {
                border: 2px solid """ + Theme.TEXT_SECONDARY + """;
            }

            QTableWidget {
                background-color: """ + Theme.BG_SECONDARY + """;
                alternate-background-color: """ + Theme.BG_PRIMARY + """;
                border: 1px solid """ + Theme.BORDER + """;
                gridline-color: """ + Theme.BORDER + """;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QTableWidget::item {
                padding: 6px;
                background-color: """ + Theme.BG_SECONDARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QTableWidget::item:alternate {
                background-color: """ + Theme.BG_PRIMARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
            }

            QHeaderView::section {
                background-color: """ + Theme.BG_PRIMARY + """;
                color: """ + Theme.TEXT_PRIMARY + """;
                padding: 6px;
                border: none;
                border-bottom: 2px solid """ + Theme.BORDER + """;
                font-weight: 600;
                font-size: 10px;
            }

            QScrollBar:vertical {
                background-color: """ + Theme.BG_PRIMARY + """;
                width: 12px;
            }

            QScrollBar::handle:vertical {
                background-color: """ + Theme.BORDER + """;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: """ + Theme.TEXT_SECONDARY + """;
            }
        """


# ============================================================================
# Data Model
# ============================================================================

class TimeEntry:
    """Represents a single time entry"""

    def __init__(self, date: str, task: str, time_in: str, time_out: str, entry_id: str = None):
        self.id = entry_id or datetime.now().isoformat()
        self.date = date
        self.task = task
        self.time_in = time_in
        self.time_out = time_out

    def duration_minutes(self) -> float:
        """Calculate duration in minutes"""
        try:
            start = datetime.strptime(self.time_in, "%H:%M")
            end = datetime.strptime(self.time_out, "%H:%M")
            if end < start:
                end += timedelta(days=1)
            return (end - start).total_seconds() / 60
        except Exception as e:
            print(f"Error calculating duration: {e}")
            return 0

    def duration_display(self) -> str:
        """Return formatted duration"""
        minutes = self.duration_minutes()
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "task": self.task,
            "time_in": self.time_in,
            "time_out": self.time_out,
        }

    @staticmethod
    def from_dict(data: dict) -> 'TimeEntry':
        return TimeEntry(
            data["date"],
            data["task"],
            data["time_in"],
            data["time_out"],
            data["id"]
        )


class TimeLogData:
    """Manages data persistence"""

    def __init__(self):
        self.data_file = Path.home() / ".timelogapp" / "data.json"
        self.config_file = Path.home() / ".timelogapp" / "config.json"
        self.data_file.parent.mkdir(exist_ok=True, parents=True)
        self.entries: list[TimeEntry] = []
        self.pending_session: Optional[dict] = None
        self.load()

    def load(self):
        """Load entries from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [
                        TimeEntry.from_dict(e)
                        for e in data.get("entries", [])
                    ]
                    self.pending_session = data.get("pending")
                    print(f"[OK] Loaded {len(self.entries)} entries from {self.data_file}")
            else:
                print(f"[INFO] No data file found, starting fresh")
                self.entries = []
                self.pending_session = None
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")
            traceback.print_exc()
            self.entries = []
            self.pending_session = None

    def save(self):
        """Save entries to file"""
        try:
            data = {
                "entries": [e.to_dict() for e in self.entries],
                "pending": self.pending_session,
            }
            self.data_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Saved {len(self.entries)} entries")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save data: {e}")
            traceback.print_exc()
            return False

    def load_config(self) -> dict:
        """Load app configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load config: {e}")
        return {"compact_mode": True, "geometry": None}

    def save_config(self, config: dict):
        """Save app configuration"""
        try:
            self.config_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Failed to save config: {e}")

    def add_entry(self, entry: TimeEntry) -> bool:
        """Add a new entry and save"""
        try:
            self.entries.append(entry)
            success = self.save()
            if success:
                print(f"[OK] Entry added: {entry.task} ({entry.date})")
            return success
        except Exception as e:
            print(f"[ERROR] Failed to add entry: {e}")
            traceback.print_exc()
            return False

    def remove_entry(self, entry_id: str) -> bool:
        """Remove an entry and save"""
        try:
            original_count = len(self.entries)
            self.entries = [e for e in self.entries if e.id != entry_id]
            if len(self.entries) < original_count:
                success = self.save()
                if success:
                    print(f"[OK] Entry removed")
                return success
            return False
        except Exception as e:
            print(f"[ERROR] Failed to remove entry: {e}")
            traceback.print_exc()
            return False


# ============================================================================
# Main Application
# ============================================================================

class TimeLogApp(QMainWindow):
    """Main application window with widget and full modes"""

    # Window size constants - ULTRA COMPACT
    WIDGET_WIDTH = 380
    WIDGET_HEIGHT = 200
    FULL_WIDTH = 1100
    FULL_HEIGHT = 880

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeLog")

        # Make window borderless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Track mouse position for dragging
        self.drag_position = QPoint()
        self.is_dragging = False

        self.data = TimeLogData()
        self.config = self.data.load_config()
        self.compact_mode = self.config.get("compact_mode", True)

        self.timer_running = False
        self.timer_start_time: Optional[datetime] = None
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        # Store references to hideable sections
        self.full_entry_form_section = None
        self.table_section = None
        self.stats_section = None
        self.footer_frame = None
        self.quick_entry_section = None
        self.toggle_btn = None

        print("\n" + "="*60)
        print("TimeLogApp Starting...")
        print(f"[INFO] Mode: {'Compact' if self.compact_mode else 'Full'}")
        print("="*60)

        self.init_ui()
        self.apply_theme()
        self.start_clock()
        self.apply_mode()

        print("[OK] Application initialized successfully\n")

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.position().y() < 50:  # Only drag from header area
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to end dragging"""
        self.is_dragging = False
        event.accept()

    def init_ui(self):
        """Initialize the user interface - ULTRA COMPACT"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header - compact
        self.create_header()
        layout.addWidget(self.header_frame)

        # Main content - no scroll area, just direct layout
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(6)

        # Timer Display
        self.create_timer_section(content_layout)

        # Quick Controls
        self.create_controls_section(content_layout)

        # Quick Entry (for compact mode)
        self.create_quick_entry_section(content_layout)

        # Full Entry Form (hidden in compact mode)
        self.create_entry_form(content_layout)

        # Time Entries Table (hidden in compact mode)
        self.create_entries_table(content_layout)

        # Statistics (hidden in compact mode)
        self.create_statistics_section(content_layout)

        layout.addWidget(content)

        # Footer (hidden in compact mode)
        self.create_footer()
        layout.addWidget(self.footer_frame)

    def create_header(self):
        """Create the header section with window controls on right"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header")
        self.header_frame.setFixedHeight(40)

        layout = QHBoxLayout(self.header_frame)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        # Draggable area on left (stretch spacer)
        layout.addStretch()

        # Window control buttons on right: Toggle, Minimize, Close
        self.toggle_btn = QPushButton("▲")
        self.toggle_btn.setObjectName("secondary")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        self.toggle_btn.clicked.connect(self.toggle_mode)
        layout.addWidget(self.toggle_btn)

        # Minimize button
        btn_minimize = QPushButton("−")
        btn_minimize.setObjectName("secondary")
        btn_minimize.setFixedSize(32, 32)
        btn_minimize.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        btn_minimize.clicked.connect(self.showMinimized)
        layout.addWidget(btn_minimize)

        # Close button
        btn_close = QPushButton("✕")
        btn_close.setObjectName("secondary")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("font-size: 14px; font-weight: bold; padding: 0px;")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

    def create_timer_section(self, parent_layout):
        """Create the timer display section - COMPACT"""
        self.timer_display = QLabel("00:00:00")
        self.timer_display.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        self.timer_display.setFixedHeight(32)
        parent_layout.addWidget(self.timer_display)

    def create_controls_section(self, parent_layout):
        """Create the control buttons - COMPACT SYMBOLS ONLY"""
        frame = QWidget()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addStretch()

        self.btn_start = QPushButton("▶")
        self.btn_start.setFixedSize(36, 32)
        self.btn_start.setFont(QFont("Arial", 10))
        self.btn_start.clicked.connect(self.on_timer_start)
        layout.addWidget(self.btn_start)

        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(36, 32)
        self.btn_pause.setFont(QFont("Arial", 10))
        self.btn_pause.clicked.connect(self.on_timer_pause)
        self.btn_pause.setEnabled(False)
        layout.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(36, 32)
        self.btn_stop.setFont(QFont("Arial", 10))
        self.btn_stop.clicked.connect(self.on_timer_stop)
        self.btn_stop.setEnabled(False)
        layout.addWidget(self.btn_stop)

        self.btn_reset = QPushButton("✕")
        self.btn_reset.setFixedSize(36, 32)
        self.btn_reset.setFont(QFont("Arial", 10))
        self.btn_reset.clicked.connect(self.on_timer_reset)
        self.btn_reset.setEnabled(False)
        layout.addWidget(self.btn_reset)

        layout.addStretch()
        parent_layout.addWidget(frame)

    def create_quick_entry_section(self, parent_layout):
        """Create the quick entry section - JUST INPUT FIELD"""
        self.quick_task_input = QLineEdit()
        self.quick_task_input.setPlaceholderText("Activity name...")
        self.quick_task_input.setFixedHeight(28)
        self.quick_entry_section = self.quick_task_input
        parent_layout.addWidget(self.quick_task_input)

    def create_entry_form(self, parent_layout):
        """Create the entry form section (hidden in compact mode)"""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)

        title = QLabel("New Entry")
        title.setObjectName("label-secondary")
        layout.addWidget(title)

        task_label = QLabel("Task Name")
        layout.addWidget(task_label)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("e.g., Design Review, Meeting")
        layout.addWidget(self.task_input)

        time_layout = QHBoxLayout()
        time_layout.setSpacing(12)

        time_in_layout = QVBoxLayout()
        time_in_label = QLabel("Time In")
        time_in_layout.addWidget(time_in_label)
        self.time_in_input = QLineEdit()
        self.time_in_input.setPlaceholderText("HH:MM")
        self.time_in_input.setMinimumHeight(32)
        self.time_in_input.setMinimumWidth(120)
        time_in_layout.addWidget(self.time_in_input)
        time_layout.addLayout(time_in_layout, 1)

        time_out_layout = QVBoxLayout()
        time_out_label = QLabel("Time Out")
        time_out_layout.addWidget(time_out_label)
        self.time_out_input = QLineEdit()
        self.time_out_input.setPlaceholderText("HH:MM")
        self.time_out_input.setMinimumHeight(32)
        self.time_out_input.setMinimumWidth(120)
        time_out_layout.addWidget(self.time_out_input)
        time_layout.addLayout(time_out_layout, 1)

        layout.addLayout(time_layout)

        # Add spacing before button
        layout.addSpacing(12)

        btn_save = QPushButton("Save Entry")
        btn_save.setMinimumHeight(36)
        btn_save.clicked.connect(self.on_save_entry)
        layout.addWidget(btn_save)

        self.full_entry_form_section = frame
        parent_layout.addWidget(frame)

    def create_entries_table(self, parent_layout):
        """Create the entries table"""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)

        title = QLabel("Today's Log")
        title.setObjectName("label-secondary")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Task", "Time In", "Time Out", "Duration"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)

        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setMinimumHeight(200)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)
        self.table_section = frame
        parent_layout.addWidget(frame)

        self.refresh_table()

    def create_statistics_section(self, parent_layout):
        """Create the statistics section"""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)

        title = QLabel("Statistics")
        title.setObjectName("label-secondary")
        layout.addWidget(title)

        stats_layout = QHBoxLayout()

        self.stat_today = self.create_stat_box("Today", "0h 0m")
        stats_layout.addWidget(self.stat_today)

        self.stat_week = self.create_stat_box("This Week", "0h 0m")
        stats_layout.addWidget(self.stat_week)

        self.stat_entries = self.create_stat_box("Entries", "0")
        stats_layout.addWidget(self.stat_entries)

        layout.addLayout(stats_layout)
        self.stats_section = frame
        parent_layout.addWidget(frame)

    def create_stat_box(self, label: str, value: str) -> QFrame:
        """Create a statistic box"""
        box = QFrame()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 9px;")
        layout.addWidget(label_widget)

        value_widget = QLabel(value)
        value_widget.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_widget.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(value_widget)

        box.value_label = value_widget
        return box

    def create_footer(self):
        """Create the footer section"""
        self.footer_frame = QFrame()
        self.footer_frame.setStyleSheet(f"background-color: {Theme.BORDER};")
        self.footer_frame.setFixedHeight(20)

        layout = QHBoxLayout(self.footer_frame)
        layout.setContentsMargins(8, 0, 8, 0)

        footer_label = QLabel("~/.timelogapp/data.json")
        footer_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 8px;")
        layout.addWidget(footer_label)
        layout.addStretch()

    def apply_theme(self):
        """Apply the theme stylesheet"""
        self.setStyleSheet(StyleSheet.get_main_stylesheet())

    def apply_mode(self):
        """Apply the current mode (compact or full)"""
        if self.compact_mode:
            self.showNormal()
            self.setGeometry(100, 100, self.WIDGET_WIDTH, self.WIDGET_HEIGHT)
            self.setMinimumSize(self.WIDGET_WIDTH, self.WIDGET_HEIGHT)
            self.setMaximumSize(self.WIDGET_WIDTH, self.WIDGET_HEIGHT)

            if self.full_entry_form_section:
                self.full_entry_form_section.setVisible(False)
            if self.table_section:
                self.table_section.setVisible(False)
            if self.stats_section:
                self.stats_section.setVisible(False)
            if self.footer_frame:
                self.footer_frame.setVisible(False)
            if self.quick_entry_section:
                self.quick_entry_section.setVisible(True)

            if self.toggle_btn:
                self.toggle_btn.setText("▲")

            print("[INFO] Switched to compact widget mode")
        else:
            self.showFullScreen()

            if self.full_entry_form_section:
                self.full_entry_form_section.setVisible(True)
            if self.table_section:
                self.table_section.setVisible(True)
            if self.stats_section:
                self.stats_section.setVisible(True)
            if self.footer_frame:
                self.footer_frame.setVisible(True)
            if self.quick_entry_section:
                self.quick_entry_section.setVisible(False)

            if self.toggle_btn:
                self.toggle_btn.setText("▼")

            self.refresh_table()
            self.update_statistics()

            print("[INFO] Switched to full mode")

    def toggle_mode(self):
        """Toggle between compact and full modes"""
        self.compact_mode = not self.compact_mode
        self.config["compact_mode"] = self.compact_mode
        self.data.save_config(self.config)
        self.apply_mode()

    def start_clock(self):
        """Start the system clock"""
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def update_clock(self):
        """Update the clock display"""
        current_time = QTime.currentTime()
        # Clock only shown in full mode, so this is minimal

    def on_timer_start(self):
        """Start the timer"""
        if not self.timer_running:
            self.timer_running = True
            self.timer_start_time = datetime.now()
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_reset.setEnabled(True)

            print("[INFO] Timer started")

            self.timer_update_timer = QTimer()
            self.timer_update_timer.timeout.connect(self.update_timer_display)
            self.timer_update_timer.start(1000)

    def on_timer_pause(self):
        """Pause the timer"""
        if self.timer_running:
            self.timer_running = False
            if hasattr(self, 'timer_update_timer'):
                self.timer_update_timer.stop()
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            print("[INFO] Timer paused")

    def on_timer_stop(self):
        """Stop and save the timer"""
        if self.timer_start_time:
            self.timer_running = False
            if hasattr(self, 'timer_update_timer'):
                self.timer_update_timer.stop()

            task = self.quick_task_input.text().strip() or "Untitled Task"
            time_in = self.timer_start_time.strftime("%H:%M")
            time_out = datetime.now().strftime("%H:%M")

            entry = TimeEntry(self.current_date, task, time_in, time_out)

            if self.data.add_entry(entry):
                self.refresh_table()
                self.update_statistics()
                QMessageBox.information(self, "Success", f"Entry saved: {task}")
                self.reset_timer()
            else:
                QMessageBox.critical(self, "Error", "Failed to save entry")

    def on_timer_reset(self):
        """Reset the timer"""
        reply = QMessageBox.question(
            self, "Reset Timer",
            "Are you sure you want to clear the timer without saving?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_timer()
            print("[INFO] Timer reset")

    def reset_timer(self):
        """Reset timer to 00:00:00"""
        self.timer_running = False
        self.timer_start_time = None
        if hasattr(self, 'timer_update_timer'):
            self.timer_update_timer.stop()

        self.timer_display.setText("00:00:00")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_reset.setEnabled(False)
        self.quick_task_input.clear()
        self.task_input.clear()
        self.time_in_input.clear()
        self.time_out_input.clear()

    def update_timer_display(self):
        """Update the timer display"""
        if self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            seconds = int(elapsed.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60

            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            self.timer_display.setText(time_str)

    def on_save_entry(self):
        """Save a manual entry from full mode"""
        task = self.task_input.text().strip()
        time_in = self.time_in_input.text().strip()
        time_out = self.time_out_input.text().strip()

        if not task or not time_in or not time_out:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields.")
            return

        try:
            datetime.strptime(time_in, "%H:%M")
            datetime.strptime(time_out, "%H:%M")
        except ValueError:
            QMessageBox.warning(self, "Invalid Time", "Please use HH:MM format (e.g., 14:30)")
            return

        try:
            entry = TimeEntry(self.current_date, task, time_in, time_out)
            if self.data.add_entry(entry):
                self.refresh_table()
                self.update_statistics()

                self.task_input.clear()
                self.time_in_input.clear()
                self.time_out_input.clear()

                QMessageBox.information(self, "Success", "Entry saved successfully!")
                print(f"[OK] Entry saved: {task}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save entry to disk")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save entry: {str(e)}")
            print(f"[ERROR] {e}")
            traceback.print_exc()

    def refresh_table(self):
        """Refresh the entries table"""
        try:
            self.table.setRowCount(0)

            today = datetime.now().strftime("%Y-%m-%d")
            today_entries = [e for e in self.data.entries if e.date == today]
            today_entries.sort(key=lambda e: e.time_in, reverse=True)

            for i, entry in enumerate(today_entries):
                self.table.insertRow(i)

                self.table.setItem(i, 0, QTableWidgetItem(entry.date))
                self.table.setItem(i, 1, QTableWidgetItem(entry.task))
                self.table.setItem(i, 2, QTableWidgetItem(entry.time_in))
                self.table.setItem(i, 3, QTableWidgetItem(entry.time_out))
                self.table.setItem(i, 4, QTableWidgetItem(entry.duration_display()))

            print(f"[OK] Table refreshed with {len(today_entries)} entries")
        except Exception as e:
            print(f"[ERROR] Failed to refresh table: {e}")
            traceback.print_exc()

    def update_statistics(self):
        """Update the statistics displays"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            today_entries = [e for e in self.data.entries if e.date == today]

            today_total_mins = sum(e.duration_minutes() for e in today_entries)
            today_hours = int(today_total_mins // 60)
            today_mins = int(today_total_mins % 60)
            self.stat_today.value_label.setText(f"{today_hours}h {today_mins}m")

            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            week_entries = [e for e in self.data.entries if e.date >= week_ago]
            week_total_mins = sum(e.duration_minutes() for e in week_entries)
            week_hours = int(week_total_mins // 60)
            week_mins = int(week_total_mins % 60)
            self.stat_week.value_label.setText(f"{week_hours}h {week_mins}m")

            self.stat_entries.value_label.setText(str(len(today_entries)))

            print(f"[OK] Statistics updated")
        except Exception as e:
            print(f"[ERROR] Failed to update statistics: {e}")
            traceback.print_exc()

    def closeEvent(self, event):
        """Handle window close"""
        try:
            print("\n[INFO] Closing application...")
            self.data.save()
            print("[OK] Data saved on exit")

            if hasattr(self, 'clock_timer'):
                self.clock_timer.stop()
            if hasattr(self, 'timer_update_timer'):
                self.timer_update_timer.stop()

            print("[OK] Application closed successfully\n")
            event.accept()
        except Exception as e:
            print(f"[ERROR] Error during close: {e}")
            traceback.print_exc()
            event.accept()


# ============================================================================
# Entry Point
# ============================================================================

def main():
    try:
        app = QApplication(sys.argv)
        window = TimeLogApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
