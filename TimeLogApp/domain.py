import datetime
import csv
import io


def parse_time_12h(time_str: str) -> datetime.time:
    parts = time_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid time format: {time_str!r}")
    time_part, meridian = parts
    meridian = meridian.upper()
    if meridian not in ("AM", "PM"):
        raise ValueError(f"Invalid meridian: {meridian!r}")
    if ":" not in time_part:
        raise ValueError(f"Invalid time format: {time_str!r}")
    hour_str, minute_str = time_part.split(":", 1)
    try:
        hour = int(hour_str)
        minute = int(minute_str)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str!r}")
    if not (1 <= hour <= 12):
        raise ValueError(f"Hour out of range: {hour}")
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute out of range: {minute}")
    if meridian == "AM":
        hour_24 = 0 if hour == 12 else hour
    else:
        hour_24 = 12 if hour == 12 else hour + 12
    return datetime.time(hour_24, minute)


def format_time_12h(t: datetime.time) -> str:
    if t.hour == 0:
        hour_12 = 12
        meridian = "AM"
    elif t.hour < 12:
        hour_12 = t.hour
        meridian = "AM"
    elif t.hour == 12:
        hour_12 = 12
        meridian = "PM"
    else:
        hour_12 = t.hour - 12
        meridian = "PM"
    return f"{hour_12:02d}:{t.minute:02d} {meridian}"


def duration_minutes(time_in_iso: str, time_out_iso: str) -> int:
    try:
        time_in = _parse_iso_datetime(time_in_iso)
    except ValueError:
        raise ValueError(
            f"Invalid time_in: {time_in_iso!r}. Expected format YYYY-MM-DDTHH:MM"
        ) from None
    try:
        time_out = _parse_iso_datetime(time_out_iso)
    except ValueError:
        raise ValueError(
            f"Invalid time_out: {time_out_iso!r}. Expected format YYYY-MM-DDTHH:MM"
        ) from None
    if time_out < time_in:
        time_out += datetime.timedelta(days=1)
    mins = int((time_out - time_in).total_seconds() // 60)
    if mins <= 0:
        raise ValueError("Duration must be positive")
    if mins > 24 * 60:
        raise ValueError("Duration exceeds 24 hours")
    return mins


def is_valid_duration(minutes: int) -> bool:
    return 0 < minutes <= 24 * 60


def get_period(date: datetime.date) -> tuple[datetime.date, datetime.date]:
    day = date.day
    if 11 <= day <= 25:
        start = date.replace(day=11)
        end = date.replace(day=25)
    elif day >= 26:
        start = date.replace(day=26)
        if date.month == 12:
            end = datetime.date(date.year + 1, 1, 10)
        else:
            end = datetime.date(date.year, date.month + 1, 10)
    else:
        if date.month == 1:
            start = datetime.date(date.year - 1, 12, 26)
        else:
            start = datetime.date(date.year, date.month - 1, 26)
        end = date.replace(day=10)
    return (start, end)


def get_periods_for_entries(entries: list) -> list:
    periods = {}
    for entry in entries:
        entry_date = datetime.date.fromisoformat(entry["date"])
        start, end = get_period(entry_date)
        key = (start.isoformat(), end.isoformat())
        if key not in periods:
            periods[key] = (start, end)
    return sorted(periods.values(), key=lambda p: p[0])


def entries_overlap(entry1: dict, entry2: dict) -> bool:
    t1_in = _parse_iso_datetime(entry1["time_in"])
    t1_out = _parse_iso_datetime(entry1["time_out"])
    if t1_out <= t1_in:
        t1_out += datetime.timedelta(days=1)
    t2_in = _parse_iso_datetime(entry2["time_in"])
    t2_out = _parse_iso_datetime(entry2["time_out"])
    if t2_out <= t2_in:
        t2_out += datetime.timedelta(days=1)
    return t1_in < t2_out and t2_in < t1_out


def find_replacement(entries: list, date: str, task: str) -> int | None:
    if not task or not task.strip():
        return None
    normalized = task.strip().lower()
    for i, entry in enumerate(entries):
        if entry["date"] == date and entry["task"].strip().lower() == normalized:
            return i
    return None


def daily_total(entries: list, date: str) -> float:
    total_mins = 0
    for entry in entries:
        if entry["date"] == date:
            total_mins += duration_minutes(entry["time_in"], entry["time_out"])
    return round(total_mins / 60.0, 2)


def period_total(entries: list, start_date: str, end_date: str) -> float:
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    total_mins = 0
    for entry in entries:
        entry_date = datetime.date.fromisoformat(entry["date"])
        if start <= entry_date <= end:
            total_mins += duration_minutes(entry["time_in"], entry["time_out"])
    return round(total_mins / 60.0, 2)


def csv_rows(entries: list, start_date: str, end_date: str) -> list:
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    period_entries = []
    for entry in entries:
        entry_date = datetime.date.fromisoformat(entry["date"])
        if start <= entry_date <= end:
            period_entries.append(entry)
    period_entries.sort(key=lambda e: (e["date"], e["time_in"]))
    rows = [["Date", "Task", "Time In", "Time Out", "Duration Hours"]]
    total_mins = 0
    for entry in period_entries:
        mins = duration_minutes(entry["time_in"], entry["time_out"])
        total_mins += mins
        task_display = entry["task"] if entry["task"] else "Untitled"
        time_in_dt = _parse_iso_datetime(entry["time_in"])
        time_out_dt = _parse_iso_datetime(entry["time_out"])
        if time_out_dt < time_in_dt:
            time_out_dt += datetime.timedelta(days=1)
        rows.append([
            entry["date"],
            task_display,
            format_time_12h(time_in_dt.time()),
            format_time_12h(time_out_dt.time()),
            f"{mins / 60.0:.2f}",
        ])
    total_hours = round(total_mins / 60.0, 2)
    rows.append(["", "Period Total", "", "", f"{total_hours:.2f}"])
    return rows


def _parse_iso_datetime(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M")
