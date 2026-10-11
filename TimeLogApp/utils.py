"""Utility functions for time log validation and formatting."""

import datetime
import re
from typing import Optional, Tuple


def validate_time_format(time_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate time string format.
    Returns (is_valid, error_message).
    """
    if not time_str or not time_str.strip():
        return False, "Time cannot be empty"

    time_str = time_str.strip()

    # Check for 12-hour format with AM/PM
    pattern = r'^(0?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM|am|pm)$'
    if not re.match(pattern, time_str):
        return False, "Use format: HH:MM AM/PM (e.g., 9:00 AM)"

    return True, None


def validate_date_format(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date string format.
    Returns (is_valid, error_message).
    """
    if not date_str or not date_str.strip():
        return False, "Date cannot be empty"

    date_str = date_str.strip()

    try:
        date_obj = datetime.date.fromisoformat(date_str)

        # Check if date is too far in the past (more than 1 year)
        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        if date_obj < one_year_ago:
            return False, f"Date is more than 1 year old. Use dates after {one_year_ago}"

        # Check if date is too far in the future (more than 7 days)
        week_ahead = datetime.date.today() + datetime.timedelta(days=7)
        if date_obj > week_ahead:
            return False, f"Date is too far in the future. Use dates before {week_ahead}"

        return True, None
    except (ValueError, TypeError):
        return False, "Use format: YYYY-MM-DD (e.g., 2026-09-23)"


def validate_task_name(task: str) -> Tuple[bool, Optional[str]]:
    """
    Validate task name.
    Returns (is_valid, error_message).
    """
    if task and len(task.strip()) > 200:
        return False, "Task name must be 200 characters or less"

    return True, None


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{hours}h"

    return f"{hours}h {mins}m"


def parse_flexible_time(time_str: str) -> Optional[datetime.time]:
    """
    Parse time with flexible formats:
    - 9:00 AM, 9:00am, 9am, 9 AM
    - 09:00 AM
    - Military time: 0900, 09:00
    """
    if not time_str:
        return None

    time_str = time_str.strip().upper()

    # Try standard 12-hour format first
    patterns = [
        (r'^(\d{1,2}):(\d{2})\s*(AM|PM)$', True),   # 9:00 AM
        (r'^(\d{1,2})\s*(AM|PM)$', False),          # 9 AM
        (r'^(\d{1,2})(\d{2})$', None),              # 0900 (military)
        (r'^(\d{1,2}):(\d{2})$', None),             # 09:00 (military)
    ]

    for pattern, has_minutes in patterns:
        match = re.match(pattern, time_str)
        if match:
            groups = match.groups()
            hour = int(groups[0])

            if has_minutes is True:
                minute = int(groups[1])
                meridian = groups[2]
            elif has_minutes is False:
                minute = 0
                meridian = groups[1]
            else:
                # Military time
                if len(groups) == 2:
                    minute = int(groups[1])
                else:
                    minute = 0

                # Convert 24-hour to 12-hour
                if 0 <= hour <= 23:
                    return datetime.time(hour, minute)
                return None

            # Convert 12-hour to 24-hour
            if meridian == "AM":
                hour_24 = 0 if hour == 12 else hour
            else:
                hour_24 = 12 if hour == 12 else hour + 12

            if 0 <= hour_24 <= 23 and 0 <= minute <= 59:
                return datetime.time(hour_24, minute)

    return None


def get_week_dates(date: datetime.date) -> list:
    """Get all dates in the week containing the given date."""
    # Find Monday of the week
    monday = date - datetime.timedelta(days=date.weekday())

    return [monday + datetime.timedelta(days=i) for i in range(7)]


def format_relative_date(date: datetime.date) -> str:
    """Format date relative to today (Today, Yesterday, etc.)"""
    today = datetime.date.today()
    delta = (date - today).days

    if delta == 0:
        return "Today"
    elif delta == -1:
        return "Yesterday"
    elif delta == 1:
        return "Tomorrow"
    elif -7 < delta < 0:
        return f"{abs(delta)} days ago"
    elif 0 < delta < 7:
        return f"In {delta} days"
    else:
        return date.strftime("%b %d, %Y")


def calculate_break_time(time_in: str, time_out: str, work_duration_minutes: int) -> int:
    """Calculate break time if the session is unusually long."""
    # If session is over 8 hours, assume there were breaks
    if work_duration_minutes > 480:  # 8 hours
        # Assume 30 min break per 4 hours
        breaks = (work_duration_minutes // 240) * 30
        return min(breaks, 120)  # Max 2 hours of breaks

    return 0


def suggest_time_entry_improvements(entries: list) -> list:
    """Analyze entries and suggest improvements."""
    suggestions = []

    if not entries:
        return suggestions

    # Check for very short entries (< 15 minutes)
    short_entries = [e for e in entries if _get_duration_minutes(e) < 15]
    if len(short_entries) > 3:
        suggestions.append({
            "type": "short_entries",
            "message": f"You have {len(short_entries)} entries under 15 minutes. Consider combining similar tasks.",
            "severity": "info"
        })

    # Check for very long entries (> 12 hours)
    long_entries = [e for e in entries if _get_duration_minutes(e) > 720]
    if long_entries:
        suggestions.append({
            "type": "long_entries",
            "message": f"You have {len(long_entries)} entries over 12 hours. Verify these are correct.",
            "severity": "warning"
        })

    # Check for duplicate tasks on the same day
    date_tasks = {}
    for entry in entries:
        date = entry.get("date")
        task = (entry.get("task") or "").strip().lower()
        if task:
            key = f"{date}:{task}"
            date_tasks[key] = date_tasks.get(key, 0) + 1

    duplicates = {k: v for k, v in date_tasks.items() if v > 1}
    if duplicates:
        suggestions.append({
            "type": "duplicate_tasks",
            "message": f"You have {len(duplicates)} duplicate tasks on the same day. Consider consolidating.",
            "severity": "info"
        })

    return suggestions


def _get_duration_minutes(entry: dict) -> int:
    """Helper to get duration in minutes from entry."""
    try:
        time_in = datetime.datetime.strptime(entry["time_in"], "%Y-%m-%dT%H:%M")
        time_out = datetime.datetime.strptime(entry["time_out"], "%Y-%m-%dT%H:%M")
        if time_out < time_in:
            time_out += datetime.timedelta(days=1)
        return int((time_out - time_in).total_seconds() // 60)
    except:
        return 0


def export_to_json(entries: list, start_date: str, end_date: str) -> str:
    """Export entries to JSON format."""
    import json

    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)

    period_entries = [
        e for e in entries
        if start <= datetime.date.fromisoformat(e["date"]) <= end
    ]

    export_data = {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "entries": period_entries,
        "exported_at": datetime.datetime.now().isoformat(),
        "total_entries": len(period_entries)
    }

    return json.dumps(export_data, indent=2, ensure_ascii=False)
