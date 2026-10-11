import datetime
import unittest
from TimeLogApp.domain import (
    parse_time_12h,
    format_time_12h,
    duration_minutes,
    is_valid_duration,
    get_period,
    get_periods_for_entries,
    entries_overlap,
    find_replacement,
    daily_total,
    period_total,
    csv_rows,
)


class TestParseTime12h(unittest.TestCase):
    def test_midnight(self):
        self.assertEqual(parse_time_12h("12:00 AM"), datetime.time(0, 0))

    def test_noon(self):
        self.assertEqual(parse_time_12h("12:00 PM"), datetime.time(12, 0))

    def test_morning(self):
        self.assertEqual(parse_time_12h("08:00 AM"), datetime.time(8, 0))
        self.assertEqual(parse_time_12h("01:30 AM"), datetime.time(1, 30))

    def test_afternoon(self):
        self.assertEqual(parse_time_12h("05:00 PM"), datetime.time(17, 0))
        self.assertEqual(parse_time_12h("11:45 PM"), datetime.time(23, 45))

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            parse_time_12h("bad")

    def test_invalid_meridian(self):
        with self.assertRaises(ValueError):
            parse_time_12h("08:00 XM")

    def test_invalid_hour(self):
        with self.assertRaises(ValueError):
            parse_time_12h("13:00 AM")

    def test_invalid_minute(self):
        with self.assertRaises(ValueError):
            parse_time_12h("08:60 AM")


class TestFormatTime12h(unittest.TestCase):
    def test_midnight(self):
        self.assertEqual(format_time_12h(datetime.time(0, 0)), "12:00 AM")

    def test_noon(self):
        self.assertEqual(format_time_12h(datetime.time(12, 0)), "12:00 PM")

    def test_morning(self):
        self.assertEqual(format_time_12h(datetime.time(8, 0)), "08:00 AM")
        self.assertEqual(format_time_12h(datetime.time(1, 30)), "01:30 AM")

    def test_afternoon(self):
        self.assertEqual(format_time_12h(datetime.time(17, 0)), "05:00 PM")
        self.assertEqual(format_time_12h(datetime.time(23, 45)), "11:45 PM")


class TestDurationMinutes(unittest.TestCase):
    def test_same_day(self):
        self.assertEqual(
            duration_minutes("2026-09-22T08:00", "2026-09-22T17:00"),
            540,
        )

    def test_overnight(self):
        self.assertEqual(
            duration_minutes("2026-09-22T22:00", "2026-09-23T02:00"),
            240,
        )

    def test_one_minute(self):
        self.assertEqual(
            duration_minutes("2026-09-22T08:00", "2026-09-22T08:01"),
            1,
        )

    def test_zero_duration_raises(self):
        with self.assertRaises(ValueError):
            duration_minutes("2026-09-22T08:00", "2026-09-22T08:00")

    def test_out_before_in_is_overnight(self):
        self.assertEqual(
            duration_minutes("2026-09-22T08:00", "2026-09-22T07:00"),
            1380,
        )

    def test_out_before_in_exceeds_24h_raises(self):
        with self.assertRaises(ValueError):
            duration_minutes("2026-09-22T06:00", "2026-09-24T05:00")

    def test_exactly_24_hours(self):
        self.assertEqual(
            duration_minutes("2026-09-22T08:00", "2026-09-23T08:00"),
            1440,
        )

    def test_over_24_hours_raises(self):
        with self.assertRaises(ValueError):
            duration_minutes("2026-09-22T08:00", "2026-09-24T08:00")

    def test_invalid_iso_time_in(self):
        with self.assertRaises(ValueError):
            duration_minutes("not-a-date", "2026-09-22T17:00")

    def test_invalid_iso_time_out(self):
        with self.assertRaises(ValueError):
            duration_minutes("2026-09-22T08:00", "bad-time")


class TestIsValidDuration(unittest.TestCase):
    def test_valid_positive(self):
        self.assertTrue(is_valid_duration(540))

    def test_valid_max(self):
        self.assertTrue(is_valid_duration(1440))

    def test_zero_invalid(self):
        self.assertFalse(is_valid_duration(0))

    def test_negative_invalid(self):
        self.assertFalse(is_valid_duration(-5))

    def test_over_max_invalid(self):
        self.assertFalse(is_valid_duration(1441))


class TestGetPeriod(unittest.TestCase):
    def test_period_a_start(self):
        start, end = get_period(datetime.date(2026, 9, 11))
        self.assertEqual(start, datetime.date(2026, 9, 11))
        self.assertEqual(end, datetime.date(2026, 9, 25))

    def test_period_a_middle(self):
        start, end = get_period(datetime.date(2026, 9, 18))
        self.assertEqual(start, datetime.date(2026, 9, 11))
        self.assertEqual(end, datetime.date(2026, 9, 25))

    def test_period_a_end(self):
        start, end = get_period(datetime.date(2026, 9, 25))
        self.assertEqual(start, datetime.date(2026, 9, 11))
        self.assertEqual(end, datetime.date(2026, 9, 25))

    def test_period_b_start(self):
        start, end = get_period(datetime.date(2026, 9, 26))
        self.assertEqual(start, datetime.date(2026, 9, 26))
        self.assertEqual(end, datetime.date(2026, 10, 10))

    def test_period_b_end(self):
        start, end = get_period(datetime.date(2026, 10, 10))
        self.assertEqual(start, datetime.date(2026, 9, 26))
        self.assertEqual(end, datetime.date(2026, 10, 10))

    def test_period_b_jan_start(self):
        start, end = get_period(datetime.date(2026, 1, 1))
        self.assertEqual(start, datetime.date(2025, 12, 26))
        self.assertEqual(end, datetime.date(2026, 1, 10))

    def test_period_b_dec_start(self):
        start, end = get_period(datetime.date(2026, 12, 26))
        self.assertEqual(start, datetime.date(2026, 12, 26))
        self.assertEqual(end, datetime.date(2027, 1, 10))

    def test_period_b_dec_10(self):
        start, end = get_period(datetime.date(2025, 12, 10))
        self.assertEqual(start, datetime.date(2025, 11, 26))
        self.assertEqual(end, datetime.date(2025, 12, 10))


class TestGetPeriodsForEntries(unittest.TestCase):
    def test_two_entries_same_period(self):
        entries = [
            {"date": "2026-09-11", "task": "A", "time_in": "2026-09-11T08:00", "time_out": "2026-09-11T09:00"},
            {"date": "2026-09-15", "task": "B", "time_in": "2026-09-15T08:00", "time_out": "2026-09-15T09:00"},
        ]
        periods = get_periods_for_entries(entries)
        self.assertEqual(len(periods), 1)
        self.assertEqual(periods[0], (datetime.date(2026, 9, 11), datetime.date(2026, 9, 25)))

    def test_two_entries_different_periods(self):
        entries = [
            {"date": "2026-09-20", "task": "A", "time_in": "2026-09-20T08:00", "time_out": "2026-09-20T09:00"},
            {"date": "2026-10-05", "task": "B", "time_in": "2026-10-05T08:00", "time_out": "2026-10-05T09:00"},
        ]
        periods = get_periods_for_entries(entries)
        self.assertEqual(len(periods), 2)


class TestEntriesOverlap(unittest.TestCase):
    def test_overlapping_same_day(self):
        e1 = {"time_in": "2026-09-22T08:00", "time_out": "2026-09-22T12:00"}
        e2 = {"time_in": "2026-09-22T10:00", "time_out": "2026-09-22T14:00"}
        self.assertTrue(entries_overlap(e1, e2))

    def test_not_overlapping_adjacent(self):
        e1 = {"time_in": "2026-09-22T08:00", "time_out": "2026-09-22T12:00"}
        e2 = {"time_in": "2026-09-22T12:00", "time_out": "2026-09-22T14:00"}
        self.assertFalse(entries_overlap(e1, e2))

    def test_not_overlapping_disjoint(self):
        e1 = {"time_in": "2026-09-22T08:00", "time_out": "2026-09-22T10:00"}
        e2 = {"time_in": "2026-09-22T14:00", "time_out": "2026-09-22T16:00"}
        self.assertFalse(entries_overlap(e1, e2))

    def test_overnight_overlaps(self):
        e1 = {"time_in": "2026-09-22T22:00", "time_out": "2026-09-23T02:00"}
        e2 = {"time_in": "2026-09-23T00:00", "time_out": "2026-09-23T04:00"}
        self.assertTrue(entries_overlap(e1, e2))

    def test_contains(self):
        e1 = {"time_in": "2026-09-22T06:00", "time_out": "2026-09-22T18:00"}
        e2 = {"time_in": "2026-09-22T08:00", "time_out": "2026-09-22T10:00"}
        self.assertTrue(entries_overlap(e1, e2))


class TestFindReplacement(unittest.TestCase):
    def test_exact_match(self):
        entries = [
            {"date": "2026-09-22", "task": "Meeting", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
            {"date": "2026-09-22", "task": "Report", "time_in": "2026-09-22T10:00", "time_out": "2026-09-22T11:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "Meeting")
        self.assertEqual(idx, 0)

    def test_case_insensitive(self):
        entries = [
            {"date": "2026-09-22", "task": "Meeting", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "meeting")
        self.assertEqual(idx, 0)

    def test_trim_whitespace(self):
        entries = [
            {"date": "2026-09-22", "task": "Meeting", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "  Meeting  ")
        self.assertEqual(idx, 0)

    def test_no_match(self):
        entries = [
            {"date": "2026-09-22", "task": "Meeting", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "Report")
        self.assertIsNone(idx)

    def test_blank_task_returns_none(self):
        entries = [
            {"date": "2026-09-22", "task": "", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "")
        self.assertIsNone(idx)

    def test_whitespace_only_task_returns_none(self):
        entries = [
            {"date": "2026-09-22", "task": "  ", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-22", "   ")
        self.assertIsNone(idx)

    def test_different_date_no_match(self):
        entries = [
            {"date": "2026-09-22", "task": "Meeting", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        idx = find_replacement(entries, "2026-09-23", "Meeting")
        self.assertIsNone(idx)


class TestDailyTotal(unittest.TestCase):
    def test_single_entry(self):
        entries = [
            {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"},
        ]
        self.assertEqual(daily_total(entries, "2026-09-22"), 9.0)

    def test_multiple_entries(self):
        entries = [
            {"date": "2026-09-22", "task": "A", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
            {"date": "2026-09-22", "task": "B", "time_in": "2026-09-22T10:00", "time_out": "2026-09-22T12:00"},
        ]
        self.assertEqual(daily_total(entries, "2026-09-22"), 3.0)

    def test_overnight_counted_on_time_in_date(self):
        entries = [
            {"date": "2026-09-22", "task": "Night", "time_in": "2026-09-22T22:00", "time_out": "2026-09-23T02:00"},
        ]
        self.assertEqual(daily_total(entries, "2026-09-22"), 4.0)
        self.assertEqual(daily_total(entries, "2026-09-23"), 0.0)

    def test_no_entries(self):
        self.assertEqual(daily_total([], "2026-09-22"), 0.0)


class TestPeriodTotal(unittest.TestCase):
    def test_period_a_total(self):
        entries = [
            {"date": "2026-09-11", "task": "A", "time_in": "2026-09-11T08:00", "time_out": "2026-09-11T09:00"},
            {"date": "2026-09-15", "task": "B", "time_in": "2026-09-15T10:00", "time_out": "2026-09-15T12:00"},
        ]
        self.assertEqual(period_total(entries, "2026-09-11", "2026-09-25"), 3.0)

    def test_period_b_total(self):
        entries = [
            {"date": "2026-09-26", "task": "A", "time_in": "2026-09-26T08:00", "time_out": "2026-09-26T10:00"},
            {"date": "2026-10-05", "task": "B", "time_in": "2026-10-05T14:00", "time_out": "2026-10-05T16:00"},
        ]
        self.assertEqual(period_total(entries, "2026-09-26", "2026-10-10"), 4.0)

    def test_year_boundary_period_b(self):
        entries = [
            {"date": "2025-12-26", "task": "A", "time_in": "2025-12-26T08:00", "time_out": "2025-12-26T09:00"},
            {"date": "2026-01-10", "task": "B", "time_in": "2026-01-10T10:00", "time_out": "2026-01-10T11:00"},
        ]
        self.assertEqual(period_total(entries, "2025-12-26", "2026-01-10"), 2.0)

    def test_outside_period_excluded(self):
        entries = [
            {"date": "2026-09-10", "task": "Before", "time_in": "2026-09-10T08:00", "time_out": "2026-09-10T09:00"},
            {"date": "2026-09-15", "task": "Inside", "time_in": "2026-09-15T08:00", "time_out": "2026-09-15T09:00"},
            {"date": "2026-09-26", "task": "After", "time_in": "2026-09-26T08:00", "time_out": "2026-09-26T09:00"},
        ]
        self.assertEqual(period_total(entries, "2026-09-11", "2026-09-25"), 1.0)


class TestCsvRows(unittest.TestCase):
    def test_basic_csv(self):
        entries = [
            {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(rows[0], ["Date", "Task", "Time In", "Time Out", "Duration Hours"])
        self.assertEqual(rows[1], ["2026-09-22", "Work", "08:00 AM", "05:00 PM", "9.00"])
        self.assertEqual(rows[2], ["", "Period Total", "", "", "9.00"])

    def test_blank_task_untitled(self):
        entries = [
            {"date": "2026-09-22", "task": "", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(rows[1][1], "Untitled")

    def test_sorted_by_date_and_time(self):
        entries = [
            {"date": "2026-09-22", "task": "B", "time_in": "2026-09-22T14:00", "time_out": "2026-09-22T16:00"},
            {"date": "2026-09-22", "task": "A", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(rows[1][1], "A")
        self.assertEqual(rows[2][1], "B")

    def test_period_total_row(self):
        entries = [
            {"date": "2026-09-22", "task": "A", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T12:00"},
            {"date": "2026-09-23", "task": "B", "time_in": "2026-09-23T09:00", "time_out": "2026-09-23T11:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(rows[-1], ["", "Period Total", "", "", "6.00"])

    def test_overnight_in_csv(self):
        entries = [
            {"date": "2026-09-22", "task": "Night", "time_in": "2026-09-22T22:00", "time_out": "2026-09-23T02:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(rows[1], ["2026-09-22", "Night", "10:00 PM", "02:00 AM", "4.00"])

    def test_csv_empty_period(self):
        entries = [
            {"date": "2026-09-01", "task": "Outside", "time_in": "2026-09-01T08:00", "time_out": "2026-09-01T09:00"},
        ]
        rows = csv_rows(entries, "2026-09-11", "2026-09-25")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["Date", "Task", "Time In", "Time Out", "Duration Hours"])
        self.assertEqual(rows[1], ["", "Period Total", "", "", "0.00"])

    def test_csv_reversed_dates(self):
        entries = [
            {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"},
        ]
        rows = csv_rows(entries, "2026-09-25", "2026-09-11")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1], ["", "Period Total", "", "", "0.00"])


if __name__ == "__main__":
    unittest.main()
