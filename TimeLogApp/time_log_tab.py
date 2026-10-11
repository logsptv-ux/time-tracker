"""Time Log tab — disciplined modern desktop UI for time tracking."""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import datetime
from pathlib import Path
from typing import Optional
import csv
from tkcalendar import DateEntry

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from TimeLogApp.domain import (
    parse_time_12h,
    format_time_12h,
    duration_minutes,
    get_period,
    get_periods_for_entries,
    entries_overlap,
    find_replacement,
    daily_total,
    period_total,
    csv_rows,
    is_valid_duration,
)
from TimeLogApp.store import Store
from TimeLogApp.analytics import get_statistics, get_task_breakdown, predict_period_total


def _get_app_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_csv_export_dir() -> Path:
    return _get_app_dir() / "exports"


def _parse_dt(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M")


def _fmt_date(d: datetime.date) -> str:
    return d.strftime("%b %d, %Y")


# ============================================================================
# Utility: Hover tooltip
# ============================================================================
class Tooltip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self.text, background="#1e293b", foreground="white",
                       font=("Segoe UI", 8), relief="flat", padx=8, pady=4)
        lbl.pack()

    def _hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ============================================================================
# Main UI
# ============================================================================
class TimeLogTab(ttk.Frame):
    _COLS = ("Date", "Task", "Time In", "Time Out", "Duration")

    def __init__(self, master=None, **kwargs):
        self.store = kwargs.pop("store", None) or Store()
        super().__init__(master, **kwargs)
        self.document: Optional[dict] = None
        self.editing_entry_id: Optional[str] = None
        self._period_options: list = []
        self._sort_col = "Date"
        self._sort_rev = True
        self._all_entries: list = []
        self._clock_id: Optional[str] = None
        self._timer_running = False
        self._timer_start_time: Optional[datetime.datetime] = None

        self._setup_theme()
        self._build_ui()
        self._refresh()
        self._start_clock()

    # -------------------------------------------------------------------------- #
    # Theme
    # -------------------------------------------------------------------------- #
    def _setup_theme(self):
        # Using a darker, more modern professional palette
        self.C = {
            "primary":    "#3b82f6",    # Blue 500
            "primary600": "#2563eb",
            "success":    "#22c55e",    # Green 500
            "success600": "#16a34a",
            "danger":     "#ef4444",    # Red 500
            "danger600":  "#dc2626",
            "bg":         "#0f172a",    # Slate 900 (Dark Mode Base)
            "card":       "#1e293b",    # Slate 800
            "border":     "#334155",    # Slate 700
            "border300":  "#475569",    # Slate 600
            "text":       "#f8fafc",    # Slate 50
            "text2":      "#e2e8f0",    # Slate 200
            "muted":      "#94a3b8",    # Slate 400
            "muted2":     "#64748b",    # Slate 500
            "accent":     "#fbbf24",    # Amber 400
        }

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Update styling to match dark theme
        style.configure("Main.TFrame",      background=self.C["bg"])
        style.configure("Card.TFrame",      background=self.C["card"],
                        relief="flat", borderwidth=0, highlightthickness=0)
        style.configure("CardBordered.TFrame", background=self.C["card"],
                        relief="solid", borderwidth=1, highlightthickness=0)

        style.configure("Modern.Treeview",
                        background=self.C["card"], foreground=self.C["text"],
                        fieldbackground=self.C["card"], borderwidth=0,
                        font=("Segoe UI", 10), rowheight=32)
        style.configure("Modern.Treeview.Heading",
                        font=("Segoe UI", 10, "bold"), foreground=self.C["text"],
                        background=self.C["border"], relief="flat", padding=6)
        style.map("Modern.Treeview",
                  background=[("selected", self.C["primary"])],
                  foreground=[("selected", "#FFFFFF")])

        style.configure("Modern.TCombobox",
                        fieldbackground=self.C["card"],
                        background=self.C["card"],
                        foreground=self.C["text"],
                        font=("Segoe UI", 11))

    # -------------------------------------------------------------------------- #
    # Builder helpers
    # -------------------------------------------------------------------------- #
    def _frame(self, parent, **kw):
        return tk.Frame(parent, bg=self.C["card"], **kw)

    def _label(self, parent, text, bold=False, size=11, color=None, bg=None, **kw):
        weight = "bold" if bold else "normal"
        color = color or self.C["text"]
        bg = bg or self.C["card"]
        return tk.Label(parent, text=text, font=("Segoe UI", size, weight),
                        fg=color, bg=bg, **kw)

    def _btn(self, parent, text, command, bg, fg="white", hover_bg=None,
             width=None, padx=16, pady=8, size=11, bold=True, **kw):
        weight = "bold" if bold else "normal"
        b = tk.Button(parent, text=text, command=command,
                      font=("Segoe UI", size, weight),
                      bg=bg, fg=fg, relief="flat", cursor="hand2",
                      padx=padx, pady=pady, borderwidth=0,
                      activebackground=hover_bg or bg,
                      activeforeground=fg,
                      **kw)
        if hover_bg:
            b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
            b.bind("<Leave>", lambda e: b.config(bg=bg))
        if width:
            b.config(width=width)
        return b

    def _entry(self, parent, textvar, width=14):
        return tk.Entry(parent, textvariable=textvar,
                        font=("Segoe UI", 11),
                        bg=self.C["card"], fg=self.C["text"],
                        insertbackground=self.C["primary"],
                        relief="solid", borderwidth=1,
                        highlightbackground=self.C["border"],
                        highlightcolor=self.C["primary"],
                        highlightthickness=1, width=width)

    def _section_card(self, parent, title: str, padding=(16, 12)):
        """Card with label header."""
        wrapper = tk.Frame(parent, bg=self.C["bg"])
        wrapper.pack(fill=tk.X, padx=12, pady=8)

        title_bar = tk.Frame(wrapper, bg=self.C["bg"])
        title_bar.pack(fill=tk.X, padx=padding[0], pady=padding[1])

        tk.Label(title_bar, text=title, font=("Segoe UI", 12, "bold"),
                 fg=self.C["text"], bg=self.C["card"]).pack(side=tk.LEFT)

        card = tk.Frame(wrapper, bg=self.C["card"], relief="solid", borderwidth=1)
        card.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=(0, padding[1]))

        inner = tk.Frame(card, bg=self.C["card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        return inner

    def _hr(self, parent):
        tk.Frame(parent, bg=self.C["border"], height=1).pack(fill=tk.X, pady=12)

    # -------------------------------------------------------------------------- #
    # Clock
    # -------------------------------------------------------------------------- #
    def _start_clock(self):
        self._tick_clock()
        self._clock_id = self.after(1000, self._start_clock)

    def _tick_clock(self):
        now = datetime.datetime.now()
        self._clock_var.set(now.strftime("%I:%M:%S %p"))

    def destroy(self):
        if self._clock_id:
            self.after_cancel(self._clock_id)
        super().destroy()

    # -------------------------------------------------------------------------- #
    # Chart logic
    # -------------------------------------------------------------------------- #
    def _refresh_chart(self, start, end):
        # Clear previous chart
        for widget in self._chart_container.winfo_children():
            widget.destroy()

        entries = self._valid_entries()
        breakdown = get_task_breakdown(entries, start.isoformat(), end.isoformat())

        if not breakdown:
            tk.Label(self._chart_container, text="No data for period",
                     bg=self.C["card"], fg=self.C["muted"]).pack(pady=20)
            return

        tasks = [t for t, h in breakdown]
        hours = [h for t, h in breakdown]

        fig = Figure(figsize=(4, 3), dpi=100, facecolor=self.C["card"])
        ax = fig.add_subplot(111)
        ax.pie(hours, labels=tasks, autopct='%1.1f%%', textprops={'color': self.C["text"]})
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------------------- #
    # Build UI
    # -------------------------------------------------------------------------- #
    def _build_ui(self):
        self.configure(style="Main.TFrame")

        # ── Header: Brand + Clock + Current Period ───────────────────────────────
        hdr = tk.Frame(self, bg=self.C["primary"], height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Brand (left)
        brand = tk.Frame(hdr, bg=self.C["primary"])
        brand.pack(side=tk.LEFT, padx=16, pady=6)
        tk.Label(brand, text="Time Log", font=("Segoe UI", 16, "bold"),
                 fg="white", bg=self.C["primary"]).pack(anchor=tk.W)

        # Period indicator (center)
        period_frame = tk.Frame(hdr, bg=self.C["primary"])
        period_frame.pack(side=tk.LEFT, padx=30, pady=6)
        self._period_label = tk.Label(period_frame, text="Loading...",
                                      font=("Segoe UI", 9, "bold"),
                                      fg="white", bg=self.C["primary"])
        self._period_label.pack(anchor=tk.W)

        # Clock (right)
        clock_frame = tk.Frame(hdr, bg=self.C["primary"])
        clock_frame.pack(side=tk.RIGHT, padx=16, pady=6)
        self._clock_var = tk.StringVar(value="--:--:--")
        tk.Label(clock_frame, textvariable=self._clock_var,
                 font=("Segoe UI", 12, "bold"), fg="white", bg=self.C["primary"]).pack(anchor=tk.W)

        # ── Content (scrollable) ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=self.C["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self._canvas = tk.Canvas(content, bg=self.C["bg"], highlightthickness=0)
        vscroll = ttk.Scrollbar(content, orient="vertical", command=self._canvas.yview)
        scroll_content = tk.Frame(self._canvas, bg=self.C["bg"])

        scroll_content.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        self._canvas.configure(yscrollcommand=vscroll.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel
        self.bind_all("<MouseWheel>", lambda e: self._canvas.yview_scroll(int(-e.delta/120), "units"))

        # ── Sections ─────────────────────────────────────────────────────────────
        self._build_entry_form(scroll_content)
        self._build_pending_section(scroll_content)

        # ── Chart Section ──
        self._chart_container = self._section_card(scroll_content, "Task Breakdown")

        self._build_history(scroll_content)
        self._build_summary(scroll_content)

        # Keyboard hint bar (bottom)
        hint = tk.Frame(self, bg=self.C["muted2"], height=24)
        hint.pack(fill=tk.X)
        hint.pack_propagate(False)
        tk.Label(hint, text="Shortcuts: Ctrl+S Save  Ctrl+I Clock In  Ctrl+O Clock Out  Ctrl+E Export  Ctrl+Backspace Delete",
                 font=("Segoe UI", 7), fg=self.C["card"], bg=self.C["muted2"]).pack(side=tk.LEFT, padx=10)

    # -------------------------------------------------------------------------- #
    # Entry Form
    # -------------------------------------------------------------------------- #
    def _build_entry_form(self, parent):
        inner = self._section_card(parent, "New Entry")

        # Top row: Date + Task
        top = tk.Frame(inner, bg=self.C["card"])
        top.pack(fill=tk.X, pady=(0, 16))

        # Date
        date_col = tk.Frame(top, bg=self.C["card"])
        date_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))
        self._label(date_col, "Date", bold=True, size=9, color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 4))
        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        self._date_entry = self._entry(date_col, self.date_var, width=14)
        self._date_entry.pack(fill=tk.X)
        Tooltip(self._date_entry, "YYYY-MM-DD format")

        # Task
        task_col = tk.Frame(top, bg=self.C["card"])
        task_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._label(task_col, "Task", bold=True, size=9, color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 4))
        self.task_var = tk.StringVar()
        self._task_entry = self._entry(task_col, self.task_var, width=30)
        self._task_entry.pack(fill=tk.X)
        self._task_entry.bind("<Return>", lambda e: self._on_save())
        Tooltip(self._task_entry, "What did you work on?")

        # Time row
        times = tk.Frame(inner, bg=self.C["card"])
        times.pack(fill=tk.X, pady=(0, 16))

        # Time In
        ti_col = tk.Frame(times, bg=self.C["card"])
        ti_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        self._label(ti_col, "Time In", bold=True, size=9, color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 4))
        ti_row = tk.Frame(ti_col, bg=self.C["card"])
        ti_row.pack(fill=tk.X)
        self.time_in_var = tk.StringVar()
        e = self._entry(ti_row, self.time_in_var, width=12)
        e.pack(side=tk.LEFT, ipady=6, ipadx=6, padx=(0, 8))
        self.btn_time_in = self._btn(ti_row, "Clock In", self._on_time_in,
                                     self.C["primary"], hover_bg=self.C["primary600"], size=10)
        self.btn_time_in.pack(side=tk.LEFT)

        # Time Out
        to_col = tk.Frame(times, bg=self.C["card"])
        to_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._label(to_col, "Time Out", bold=True, size=9, color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 4))
        to_row = tk.Frame(to_col, bg=self.C["card"])
        to_row.pack(fill=tk.X)
        self.time_out_var = tk.StringVar()
        e = self._entry(to_row, self.time_out_var, width=12)
        e.pack(side=tk.LEFT, ipady=6, ipadx=6, padx=(0, 8))
        self.btn_time_out = self._btn(to_row, "Clock Out", self._on_time_out,
                                      self.C["success"], hover_bg=self.C["success600"], size=10)
        self.btn_time_out.pack(side=tk.LEFT)

        # Timer row (Quick Start/Stop for active timing)
        timer_row = tk.Frame(inner, bg=self.C["card"])
        timer_row.pack(fill=tk.X, pady=(0, 16))

        self._label(timer_row, "Quick Timer", bold=True, size=9, color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 4))

        timer_buttons = tk.Frame(inner, bg=self.C["card"])
        timer_buttons.pack(fill=tk.X, pady=(0, 16))

        self.btn_timer_start = self._btn(timer_buttons, "▶ Start Timer", self._on_timer_start,
                                         self.C["primary"], hover_bg=self.C["primary600"], size=10)
        self.btn_timer_start.pack(side=tk.LEFT, padx=(0, 8))
        Tooltip(self.btn_timer_start, "Start tracking time immediately")

        self.btn_timer_stop = self._btn(timer_buttons, "⏹ Stop & Save", self._on_timer_stop,
                                        self.C["success"], hover_bg=self.C["success600"], size=10)
        self.btn_timer_stop.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_timer_stop.config(state=tk.DISABLED)
        Tooltip(self.btn_timer_stop, "Stop timer and save entry")

        self.btn_timer_reset = self._btn(timer_buttons, "✕ Reset", self._on_timer_reset,
                                         self.C["danger"], fg="white",
                                         hover_bg=self.C["danger600"], size=10)
        self.btn_timer_reset.pack(side=tk.LEFT)
        self.btn_timer_reset.config(state=tk.DISABLED)
        Tooltip(self.btn_timer_reset, "Clear timer without saving")

        self._timer_label = tk.Label(timer_buttons, text="", font=("Segoe UI", 11, "bold"),
                                     fg=self.C["accent"], bg=self.C["card"])
        self._timer_label.pack(side=tk.LEFT, padx=(20, 0))

        # Actions
        self._hr(inner)

        actions = tk.Frame(inner, bg=self.C["card"])
        actions.pack(anchor=tk.W)

        self.btn_save = self._btn(actions, "Save Entry", self._on_save,
                                  self.C["success"], hover_bg=self.C["success600"],
                                  size=11, bold=True, padx=24, pady=8)
        self.btn_save.pack(side=tk.LEFT, padx=(0, 12))
        Tooltip(self.btn_save, "Ctrl+S")

        self.btn_clear = self._btn(actions, "Clear", self._on_clear,
                                   self.C["border"], fg=self.C["text2"],
                                   hover_bg=self.C["border300"], size=10, bold=False)
        self.btn_clear.pack(side=tk.LEFT)
        Tooltip(self.btn_clear, "Ctrl+N")

        # Edit badge (hidden initially)
        self._edit_badge = tk.Label(actions, text="✏ Editing", font=("Segoe UI", 9),
                                    fg=self.C["accent"], bg=self.C["card"])
        self._edit_badge.pack(side=tk.LEFT, padx=(12, 0))
        self._edit_badge.pack_forget()

    # -------------------------------------------------------------------------- #
    # Pending Session
    # -------------------------------------------------------------------------- #
    def _build_pending_section(self, parent):
        inner = self._section_card(parent, "Active Session", padding=(20, 12))

        self._pending_label = tk.Label(inner, text="No active session",
                                       font=("Segoe UI", 11), fg=self.C["muted2"],
                                       bg=self.C["card"])
        self._pending_label.pack(anchor=tk.W, pady=(0, 12))

        actions = tk.Frame(inner, bg=self.C["card"])
        actions.pack(anchor=tk.W)

        self.btn_pending_out = self._btn(actions, "Complete Session",
                                         self._on_pending_time_out,
                                         self.C["success"], hover_bg=self.C["success600"],
                                         size=10)
        self.btn_pending_out.pack(side=tk.LEFT, padx=(0, 10))
        Tooltip(self.btn_pending_out, "Mark active session as complete")

        self.btn_cancel_pending = self._btn(actions, "Cancel", self._on_cancel_pending,
                                            self.C["danger"], fg="white",
                                            hover_bg=self.C["danger600"],
                                            size=10)
        self.btn_cancel_pending.pack(side=tk.LEFT)
        Tooltip(self.btn_cancel_pending, "Discard active session")

    # -------------------------------------------------------------------------- #
    # History
    # -------------------------------------------------------------------------- #
    def _build_history(self, parent):
        inner = self._section_card(parent, "Time Entries", padding=(20, 12))

        # Header with count
        header = tk.Frame(inner, bg=self.C["card"])
        header.pack(fill=tk.X, pady=(0, 12))

        self._label(header, "Recent", bold=True, size=12).pack(side=tk.LEFT)
        self._entry_count = tk.Label(header, text="0 entries",
                                     font=("Segoe UI", 10), fg=self.C["muted2"],
                                     bg=self.C["card"])
        self._entry_count.pack(side=tk.LEFT, padx=(10, 0))

        # Search
        search = tk.Frame(inner, bg=self.C["card"])
        search.pack(fill=tk.X, pady=(0, 12))

        tk.Label(search, text="🔍", font=("Segoe UI", 10),
                 fg=self.C["muted"], bg=self.C["card"]).pack(side=tk.LEFT, padx=(0, 6))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter_entries())
        search_entry = tk.Entry(search, textvariable=self._search_var,
                                font=("Segoe UI", 11),
                                bg=self.C["card"], fg=self.C["text"],
                                relief="solid", borderwidth=1,
                                highlightbackground=self.C["border"],
                                highlightcolor=self.C["primary"],
                                highlightthickness=1, width=30)
        search_entry.pack(side=tk.LEFT)
        Tooltip(search_entry, "Filter by task or date")

        # Tree
        tree_frame = tk.Frame(inner, bg=self.C["card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.history_tree = ttk.Treeview(
            tree_frame, columns=self._COLS, show="headings",
            selectmode="browse", style="Modern.Treeview", height=8)
        for col in self._COLS:
            self.history_tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.history_tree.column(col, width={"Task": 240, "Duration": 90}.get(col, 110),
                                     anchor="center" if col != "Task" else "w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_tree.bind("<<TreeviewSelect>>", self._on_select_entry)
        self.history_tree.bind("<Double-1>", self._on_double_click_entry)

        # Delete button
        self.btn_delete = self._btn(inner, "Delete Selected", self._on_delete,
                                    self.C["danger"], fg="white",
                                    hover_bg=self.C["danger600"], size=10)
        self.btn_delete.pack(anchor=tk.W)

    # -------------------------------------------------------------------------- #
    # Summary / Analytics
    # -------------------------------------------------------------------------- #
    def _build_summary(self, parent):
        inner = self._section_card(parent, "Period Summary", padding=(20, 12))

        # Period selector
        period_row = tk.Frame(inner, bg=self.C["card"])
        period_row.pack(fill=tk.X, pady=(0, 16))

        # Helper to style DateEntry
        style = ttk.Style()
        style.configure("DateEntry", fieldbackground=self.C["card"], background=self.C["card"], foreground=self.C["text"], borderwidth=0)

        self._label(period_row, "From:", bold=True, size=9, color=self.C["muted"]).pack(side=tk.LEFT, padx=(0, 8))
        self.start_date_entry = DateEntry(period_row, width=12, background=self.C["primary"], foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 12))

        self._label(period_row, "To:", bold=True, size=9, color=self.C["muted"]).pack(side=tk.LEFT, padx=(0, 8))
        self.end_date_entry = DateEntry(period_row, width=12, background=self.C["primary"], foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 12))

        self.btn_apply = self._btn(period_row, "Apply", self._on_apply_date_range,
                                   self.C["primary"], hover_bg=self.C["primary600"], size=10)
        self.btn_apply.pack(side=tk.LEFT, padx=(0, 12))

        # Quick-select Buttons
        preset_frame = tk.Frame(inner, bg=self.C["card"])
        preset_frame.pack(fill=tk.X, pady=(0, 16))
        self._btn(preset_frame, "This Period", lambda: self._on_preset("this_period"), self.C["border"], size=9, bold=False).pack(side=tk.LEFT, padx=(0, 8))
        self._btn(preset_frame, "Last Period", lambda: self._on_preset("last_period"), self.C["border"], size=9, bold=False).pack(side=tk.LEFT, padx=(0, 8))
        self._btn(preset_frame, "This Month", lambda: self._on_preset("this_month"), self.C["border"], size=9, bold=False).pack(side=tk.LEFT, padx=(0, 8))


        # Stats strip (4 cards)
        stats = tk.Frame(inner, bg=self.C["card"])
        stats.pack(fill=tk.X, pady=(0, 16))

        stat_configs = [
            ("Hours", "total_hours", "0.0", self.C["primary"]),
            ("Days", "days_worked", "0", self.C["accent"]),
            ("Entries", "total_entries", "0", self.C["success"]),
            ("Avg/Day", "avg_hours_per_day", "0.0", self.C["primary"]),
        ]

        for label, key, init, color in stat_configs:
            box = tk.Frame(stats, bg=self.C["card"])
            box.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 12))
            tk.Label(box, text=label, font=("Segoe UI", 9, "bold"),
                     fg=self.C["muted2"], bg=self.C["card"]).pack(anchor=tk.W)
            val = tk.Label(box, text=init, font=("Segoe UI", 20, "bold"),
                           fg=color, bg=self.C["card"])
            val.pack(anchor=tk.W)
            setattr(self, f"_stat_{key}", val)

        # Prediction line
        self._pred_label = tk.Label(inner, text="", font=("Segoe UI", 9),
                                    fg=self.C["muted2"], bg=self.C["card"])
        self._pred_label.pack(anchor=tk.W, pady=(0, 12))

        # Daily breakdown
        daily_frame = tk.Frame(inner, bg=self.C["card"])
        daily_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        self._label(daily_frame, "Daily Breakdown", bold=True, size=9,
                    color=self.C["muted"]).pack(anchor=tk.W, pady=(0, 8))

        self.daily_tree = ttk.Treeview(daily_frame, columns=("Date", "Hours"),
                                       show="headings", height=6,
                                       style="Modern.Treeview")
        self.daily_tree.heading("Date", text="Date")
        self.daily_tree.heading("Hours", text="Hours")
        self.daily_tree.column("Date", width=140, anchor="w")
        self.daily_tree.column("Hours", width=80, anchor="center")
        dsb = ttk.Scrollbar(daily_frame, orient="vertical", command=self.daily_tree.yview)
        self.daily_tree.configure(yscrollcommand=dsb.set)
        self.daily_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Export buttons
        self._hr(inner)

        export_frame = tk.Frame(inner, bg=self.C["card"])
        export_frame.pack(anchor=tk.W)

        self.btn_export = self._btn(export_frame, "Export CSV", self._on_export_csv,
                                    self.C["primary"], hover_bg=self.C["primary600"],
                                    size=10, padx=20)
        self.btn_export.pack(side=tk.LEFT, padx=(0, 10))
        Tooltip(self.btn_export, "Ctrl+E")

        self.btn_backup = self._btn(export_frame, "Backup", self._on_backup,
                                    self.C["border"], fg=self.C["text2"],
                                    hover_bg=self.C["border300"], size=10)
        self.btn_backup.pack(side=tk.LEFT)
        Tooltip(self.btn_backup, "Save backup to data/backups/")

    # -------------------------------------------------------------------------- #
    # Data helpers
    # -------------------------------------------------------------------------- #
    def _valid_entries(self) -> list:
        result = []
        for e in (self.document or {}).get("entries", []):
            if not isinstance(e, dict):
                continue
            if not all(k in e for k in ("id", "date", "task", "time_in", "time_out")):
                continue
            try:
                _parse_dt(e["time_in"])
                _parse_dt(e["time_out"])
            except (ValueError, TypeError):
                continue
            result.append(e)
        return result

    def _has_pending(self) -> bool:
        return bool(self.document and self.document.get("pending"))

    def _get_pending(self):
        return self.document.get("pending") if self.document else None

    def _refresh_entry_form(self):
        if self.editing_entry_id and self.document:
            for entry in self.document.get("entries", []):
                if not isinstance(entry, dict):
                    continue
                if entry.get("id") == self.editing_entry_id:
                    self.date_var.set(entry.get("date", ""))
                    self.task_var.set(entry.get("task") or "")
                    try:
                        ti = _parse_dt(entry["time_in"])
                        to = _parse_dt(entry["time_out"])
                        if to < ti:
                            to += datetime.timedelta(days=1)
                        self.time_in_var.set(format_time_12h(ti.time()))
                        self.time_out_var.set(format_time_12h(to.time()))
                    except Exception:
                        self.time_in_var.set("")
                        self.time_out_var.set("")
                    self._edit_badge.pack(side=tk.LEFT, padx=(12, 0))
                    return
        if not self._has_pending():
            self.date_var.set(datetime.date.today().isoformat())
        self.task_var.set("")
        self.time_in_var.set("")
        self.time_out_var.set("")
        self._edit_badge.pack_forget()

    def _update_controls(self):
        has = self._has_pending()
        self.btn_time_in.config(state=tk.DISABLED if has else tk.NORMAL)
        self.btn_time_out.config(state=tk.NORMAL if has else tk.DISABLED)

    # -------------------------------------------------------------------------- #
    # Refresh
    # -------------------------------------------------------------------------- #
    def _refresh(self):
        try:
            self.document = self.store.load()
        except ValueError as e:
            messagebox.showerror("Data Error", str(e))
            self.document = {"version": 1, "entries": [], "pending": None}
            self.editing_entry_id = None

        self._refresh_entry_form()
        self._refresh_pending()
        self._refresh_entries()
        self._refresh_summary()
        self._update_controls()

    def _refresh_pending(self):
        pending = self._get_pending()
        if pending:
            date_str = pending.get("date", "")
            task = pending.get("task", "") or "Untitled"
            time_in = pending.get("time_in", "")
            try:
                ti_dt = _parse_dt(time_in)
                elapsed = datetime.datetime.now() - ti_dt
                hrs = int(elapsed.total_seconds() // 3600)
                mins = int((elapsed.total_seconds() % 3600) // 60)
                elapsed_str = f"({hrs}h {mins}m elapsed)"
            except Exception:
                elapsed_str = ""
            self._pending_label.config(text=f"{task} • {date_str} • {elapsed_str}",
                                       fg=self.C["primary"])
            self.btn_pending_out.config(state=tk.NORMAL)
            self.btn_cancel_pending.config(state=tk.NORMAL)
        else:
            self._pending_label.config(text="No active session", fg=self.C["muted2"])
            self.btn_pending_out.config(state=tk.DISABLED)
            self.btn_cancel_pending.config(state=tk.DISABLED)

    def _refresh_entries(self):
        entries = sorted(self._valid_entries(), key=lambda e: (e["date"], e["time_in"]),
                         reverse=self._sort_rev)
        self._all_entries = []
        for e in entries:
            task = e["task"] or "Untitled"
            ti_dt = _parse_dt(e["time_in"])
            to_dt = _parse_dt(e["time_out"])
            if to_dt < ti_dt:
                to_dt += datetime.timedelta(days=1)
            try:
                dur = f"{duration_minutes(e['time_in'], e['time_out']) / 60:.2f}"
            except ValueError:
                dur = "–"
            row = {"id": e["id"], "date": e["date"], "task": task,
                   "ti": format_time_12h(ti_dt.time()),
                   "to": format_time_12h(to_dt.time()), "dur": dur}
            self._all_entries.append(row)
        self._render_entries()

    def _render_entries(self, filtered=True):
        self.history_tree.delete(*self.history_tree.get_children())
        for r in self._all_entries:
            self.history_tree.insert("", tk.END, iid=r["id"],
                                     values=(r["date"], r["task"], r["ti"], r["to"], r["dur"]))
        self._entry_count.config(text=f"{len(self._all_entries)} entries")

    def _filter_entries(self):
        query = self._search_var.get().strip().lower()
        if not query:
            self._render_entries(filtered=False)
            return
        filtered = [r for r in self._all_entries
                    if query in r["task"].lower() or query in r["date"]]
        self._render_entries(filtered=True)

    def _sort_by(self, col: str):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = True

        key_map = {
            "Date": lambda r: r["date"],
            "Task": lambda r: r["task"].lower(),
            "Time In": lambda r: r["ti"],
            "Time Out": lambda r: r["to"],
            "Duration": lambda r: float(r["dur"]) if r["dur"] != "–" else 0,
        }
        self._all_entries.sort(key=key_map.get(col, lambda r: r["date"]), reverse=self._sort_rev)
        self._filter_entries()

    def _refresh_summary(self):
        if not self.document:
            return

        # Set default period
        today = datetime.date.today()
        start, end = get_period(today)
        self.start_date_entry.set_date(start)
        self.end_date_entry.set_date(end)
        self._apply_range(start, end)

    def _on_apply_date_range(self):
        start = self.start_date_entry.get_date()
        end = self.end_date_entry.get_date()
        self._apply_range(start, end)

    def _on_preset(self, preset):
        today = datetime.date.today()
        if preset == "this_period":
            start, end = get_period(today)
        elif preset == "last_period":
            # Rough approximation
            start, end = get_period(today - datetime.timedelta(days=15))
        elif preset == "this_month":
            start = today.replace(day=1)
            end = today
        else:
            return
        self.start_date_entry.set_date(start)
        self.end_date_entry.set_date(end)
        self._apply_range(start, end)

    def _apply_range(self, start, end):
        s, e = start.isoformat(), end.isoformat()
        self._period_label.config(text=f"{start.strftime('%b %d')} – {end.strftime('%b %d')}")

        self._refresh_chart(start, end)

        entries = self._valid_entries()
        stats = get_statistics(entries, s, e)

        self._stat_total_hours.config(text=f"{stats['total_hours']:.1f}")
        self._stat_days_worked.config(text=str(stats['days_worked']))
        self._stat_total_entries.config(text=str(stats['total_entries']))
        self._stat_avg_hours_per_day.config(text=f"{stats['avg_hours_per_day']:.1f}")

        pred = predict_period_total(entries, s, e)
        if pred.get("confidence") and pred.get("confidence") != "actual":
            conf = pred["confidence"]
            conf_text = {"low": "(early)", "medium": "(mid)", "high": "(on track)"}.get(conf, "")
            self._pred_label.config(text=f"Projected: {pred.get('predicted_total', 0):.1f}h {conf_text}")
        else:
            self._pred_label.config(text="")

        self.daily_tree.delete(*self.daily_tree.get_children())
        current = start
        while current <= end:
            total = daily_total(entries, current.isoformat())
            tag = ("has_hours",) if total > 0 else ()
            self.daily_tree.insert("", tk.END, values=(current.strftime("%b %d"), f"{total:.1f}"), tags=tag)
            current += datetime.timedelta(days=1)

    # -------------------------------------------------------------------------- #
    # Actions
    # -------------------------------------------------------------------------- #
    def _on_time_in(self):
        now = datetime.datetime.now()
        date_str = self.date_var.get().strip()
        try:
            datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messagebox.showerror("Validation", "Invalid date. Use YYYY-MM-DD.")
            return

        self.time_in_var.set(format_time_12h(now.time()))
        pending = {"date": date_str, "task": self.task_var.get(),
                   "time_in": f"{date_str}T{now.strftime('%H:%M')}"}
        try:
            self.store.set_pending(self.document, pending)
            self.store.save(self.document)
            self._refresh_pending()
            self._update_controls()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _on_time_out(self):
        self.time_out_var.set(format_time_12h(datetime.datetime.now().time()))

    def _on_save(self):
        date_str = self.date_var.get().strip()
        try:
            datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messagebox.showerror("Validation", "Invalid date. Use YYYY-MM-DD.")
            return

        task = self.task_var.get().strip()
        time_in = self.time_in_var.get().strip()
        time_out = self.time_out_var.get().strip()

        if not time_in:
            messagebox.showerror("Validation", "Time In is required.")
            return
        if not time_out:
            messagebox.showerror("Validation", "Time Out is required.")
            return

        try:
            t_in = parse_time_12h(time_in)
            t_out = parse_time_12h(time_out)
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return

        entry_date = datetime.date.fromisoformat(date_str)
        ti_iso = f"{date_str}T{t_in.strftime('%H:%M')}"
        to_dt = datetime.datetime.combine(entry_date, t_out)
        if to_dt < datetime.datetime.combine(entry_date, t_in):
            to_dt += datetime.timedelta(days=1)
        to_iso = f"{to_dt.strftime('%Y-%m-%d')}T{t_out.strftime('%H:%M')}"

        try:
            mins = duration_minutes(ti_iso, to_iso)
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
            return

        if not is_valid_duration(mins):
            messagebox.showerror("Validation", "Duration must be 1min–24hrs.")
            return

        new_entry = {"date": date_str, "task": task, "time_in": ti_iso, "time_out": to_iso}
        entries = self.document["entries"]

        if self.editing_entry_id:
            for e in entries:
                if e["id"] == self.editing_entry_id:
                    new_entry["id"] = e["id"]
                    break
            for e in entries:
                if e["id"] != self.editing_entry_id and entries_overlap(e, new_entry):
                    messagebox.showerror("Overlap", f"Overlaps with: {e['date']} – {e['task'] or 'Untitled'}")
                    return
            self.store.update_entry(self.document, self.editing_entry_id, **new_entry)
        else:
            for e in entries:
                if entries_overlap(e, new_entry):
                    messagebox.showerror("Overlap", f"Overlaps with: {e['date']} – {e['task'] or 'Untitled'}")
                    return
            self.store.add_entry(self.document, new_entry)

        if self._has_pending():
            self.store.set_pending(self.document, None)

        try:
            self.store.save(self.document)
        except ValueError as e:
            messagebox.showerror("Save Error", str(e))
            return

        self.editing_entry_id = None
        self._refresh()

    def _on_clear(self):
        self.editing_entry_id = None
        self._refresh_entry_form()
        self._update_controls()

    def _on_pending_time_out(self):
        pending = self._get_pending()
        if not pending:
            return
        if pending.get("date"):
            self.date_var.set(pending["date"])
        self.time_out_var.set(format_time_12h(datetime.datetime.now().time()))

    def _on_cancel_pending(self):
        if not self._has_pending():
            return
        if not messagebox.askyesno("Cancel Session", "Discard the active session?"):
            return
        self.store.set_pending(self.document, None)
        try:
            self.store.save(self.document)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        self.editing_entry_id = None
        self._refresh()

    def _on_timer_start(self):
        """Start the timer by populating Time In field and setting timer state."""
        date_str = self.date_var.get().strip()
        try:
            datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messagebox.showerror("Validation", "Invalid date. Use YYYY-MM-DD.")
            return

        task = self.task_var.get().strip()
        if not task:
            messagebox.showerror("Validation", "Task name is required to start timer.")
            return

        now = datetime.datetime.now()
        self.time_in_var.set(format_time_12h(now.time()))
        self._timer_running = True
        self._timer_start_time = now

        self.btn_timer_start.config(state=tk.DISABLED)
        self.btn_timer_stop.config(state=tk.NORMAL)
        self.btn_timer_reset.config(state=tk.NORMAL)
        self._update_timer_display()

    def _on_timer_stop(self):
        """Stop the timer, set Time Out, and save the entry."""
        if not self._timer_running or not self._timer_start_time:
            messagebox.showerror("Error", "Timer is not running.")
            return

        now = datetime.datetime.now()
        self.time_out_var.set(format_time_12h(now.time()))
        self._timer_running = False
        self._timer_label.config(text="")

        self.btn_timer_start.config(state=tk.NORMAL)
        self.btn_timer_stop.config(state=tk.DISABLED)
        self.btn_timer_reset.config(state=tk.DISABLED)

        # Automatically save the entry
        self._on_save()

    def _on_timer_reset(self):
        """Reset the timer without saving."""
        if not messagebox.askyesno("Reset Timer", "Clear the timer without saving?"):
            return

        self._timer_running = False
        self._timer_start_time = None
        self.time_in_var.set("")
        self.time_out_var.set("")
        self._timer_label.config(text="")

        self.btn_timer_start.config(state=tk.NORMAL)
        self.btn_timer_stop.config(state=tk.DISABLED)
        self.btn_timer_reset.config(state=tk.DISABLED)

    def _update_timer_display(self):
        """Update the timer display with elapsed time."""
        if not self._timer_running or not self._timer_start_time:
            return

        elapsed = datetime.datetime.now() - self._timer_start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self._timer_label.config(text=time_str)

        # Schedule next update
        self.after(1000, self._update_timer_display)

    def _on_select_entry(self, _event):
        sel = self.history_tree.selection()
        if not sel or not self.document:
            return
        eid = sel[0]
        for entry in self.document.get("entries", []):
            if entry.get("id") == eid:
                self.editing_entry_id = eid
                self._refresh_entry_form()
                self._update_controls()
                return

    def _on_double_click_entry(self, _event):
        self._on_select_entry(None)

    def _on_delete(self):
        sel = self.history_tree.selection()
        if not sel or not self.document:
            return
        if not messagebox.askyesno("Delete Entry", "Delete this entry?"):
            return
        eid = sel[0]
        if self.store.remove_entry(self.document, eid):
            try:
                self.store.save(self.document)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            if self.editing_entry_id == eid:
                self.editing_entry_id = None
            self._refresh()

    def _on_export_csv(self):
        if not self.document:
            return

        start = self.start_date_entry.get_date()
        end = self.end_date_entry.get_date()
        s, e = start.isoformat(), end.isoformat()
        fn = f"time_log_{s}_to_{e}.csv"
        fp = _get_csv_export_dir() / fn

        if fp.exists():
            if not messagebox.askyesno("Overwrite", f"'{fn}' exists. Overwrite?"):
                return

        entries = self._valid_entries()
        try:
            rows = csv_rows(entries, s, e)
        except Exception as ex:
            messagebox.showerror("Export Error", str(ex))
            return

        try:
            _get_csv_export_dir().mkdir(parents=True, exist_ok=True)
            with open(fp, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            messagebox.showinfo("Exported", f"Saved:\n{fp}")
        except Exception as ex:
            messagebox.showerror("Export Error", str(ex))

    def _on_backup(self):
        try:
            path = self.store.create_backup()
            if path:
                messagebox.showinfo("Backup", f"Saved:\n{path}")
            else:
                messagebox.showinfo("Backup", "No data to back up yet.")
        except Exception as ex:
            messagebox.showerror("Backup Error", str(ex))
