"""Analytics and statistics for time log entries."""

import datetime
from collections import defaultdict


def get_statistics(entries: list, start_date: str, end_date: str) -> dict:
    """Calculate comprehensive statistics for a period."""
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)

    period_entries = [
        e for e in entries
        if start <= datetime.date.fromisoformat(e["date"]) <= end
    ]

    if not period_entries:
        return {
            "total_hours": 0.0,
            "total_entries": 0,
            "avg_hours_per_day": 0.0,
            "days_worked": 0,
            "top_tasks": [],
            "longest_session": None,
            "shortest_session": None,
        }

    # Calculate durations
    durations = []
    task_hours = defaultdict(float)
    daily_hours = defaultdict(float)

    for entry in period_entries:
        time_in = datetime.datetime.strptime(entry["time_in"], "%Y-%m-%dT%H:%M")
        time_out = datetime.datetime.strptime(entry["time_out"], "%Y-%m-%dT%H:%M")
        if time_out < time_in:
            time_out += datetime.timedelta(days=1)

        hours = (time_out - time_in).total_seconds() / 3600
        durations.append((hours, entry))

        task = entry.get("task", "Untitled") or "Untitled"
        task_hours[task] += hours
        daily_hours[entry["date"]] += hours

    total_hours = sum(d[0] for d in durations)
    days_worked = len(daily_hours)

    # Top tasks
    top_tasks = sorted(task_hours.items(), key=lambda x: x[1], reverse=True)[:5]

    # Longest and shortest sessions
    longest = max(durations, key=lambda x: x[0])
    shortest = min(durations, key=lambda x: x[0])

    return {
        "total_hours": round(total_hours, 2),
        "total_entries": len(period_entries),
        "avg_hours_per_day": round(total_hours / days_worked if days_worked > 0 else 0, 2),
        "days_worked": days_worked,
        "top_tasks": [(task, round(hours, 2)) for task, hours in top_tasks],
        "longest_session": {
            "hours": round(longest[0], 2),
            "task": longest[1].get("task", "Untitled") or "Untitled",
            "date": longest[1]["date"]
        },
        "shortest_session": {
            "hours": round(shortest[0], 2),
            "task": shortest[1].get("task", "Untitled") or "Untitled",
            "date": shortest[1]["date"]
        },
    }


def get_task_breakdown(entries: list, start_date: str, end_date: str) -> list:
    """Get breakdown of hours by task for a period."""
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)

    task_hours = defaultdict(float)

    for entry in entries:
        entry_date = datetime.date.fromisoformat(entry["date"])
        if start <= entry_date <= end:
            time_in = datetime.datetime.strptime(entry["time_in"], "%Y-%m-%dT%H:%M")
            time_out = datetime.datetime.strptime(entry["time_out"], "%Y-%m-%dT%H:%M")
            if time_out < time_in:
                time_out += datetime.timedelta(days=1)

            hours = (time_out - time_in).total_seconds() / 3600
            task = entry.get("task", "Untitled") or "Untitled"
            task_hours[task] += hours

    # Sort by hours descending
    return [(task, round(hours, 2)) for task, hours in
            sorted(task_hours.items(), key=lambda x: x[1], reverse=True)]


def predict_period_total(entries: list, start_date: str, end_date: str) -> dict:
    """Predict total hours for current period based on progress."""
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    today = datetime.date.today()

    if today < start:
        return {"predicted_total": 0.0, "confidence": "low"}

    if today >= end:
        # Period is complete
        task_hours = defaultdict(float)
        for entry in entries:
            entry_date = datetime.date.fromisoformat(entry["date"])
            if start <= entry_date <= end:
                time_in = datetime.datetime.strptime(entry["time_in"], "%Y-%m-%dT%H:%M")
                time_out = datetime.datetime.strptime(entry["time_out"], "%Y-%m-%dT%H:%M")
                if time_out < time_in:
                    time_out += datetime.timedelta(days=1)
                hours = (time_out - time_in).total_seconds() / 3600
                task_hours[entry["date"]] += hours

        total = sum(task_hours.values())
        return {"predicted_total": round(total, 2), "confidence": "actual"}

    # Calculate current total and days elapsed
    current_total = 0.0
    for entry in entries:
        entry_date = datetime.date.fromisoformat(entry["date"])
        if start <= entry_date <= today:
            time_in = datetime.datetime.strptime(entry["time_in"], "%Y-%m-%dT%H:%M")
            time_out = datetime.datetime.strptime(entry["time_out"], "%Y-%m-%dT%H:%M")
            if time_out < time_in:
                time_out += datetime.timedelta(days=1)
            hours = (time_out - time_in).total_seconds() / 3600
            current_total += hours

    days_elapsed = (today - start).days + 1
    total_days = (end - start).days + 1

    if days_elapsed < 3:
        confidence = "low"
    elif days_elapsed < total_days * 0.5:
        confidence = "medium"
    else:
        confidence = "high"

    # Simple linear projection
    avg_per_day = current_total / days_elapsed if days_elapsed > 0 else 0
    predicted = avg_per_day * total_days

    return {
        "predicted_total": round(predicted, 2),
        "current_total": round(current_total, 2),
        "days_elapsed": days_elapsed,
        "total_days": total_days,
        "confidence": confidence
    }
