"""
Test script for TimeLogApp - Tests data persistence without GUI
Runs all critical functionality tests
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import traceback

# Import the data model from the main app
sys.path.insert(0, r'C:\Users\evang\OneDrive\Desktop')

from TimeLogApp_PySide6 import TimeEntry, TimeLogData


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_data_persistence():
    """Test 1: Data persistence - entries saved to disk and reloaded"""
    print_header("TEST 1: Data Persistence (Save & Load)")

    try:
        # Create a fresh data instance
        data1 = TimeLogData()
        initial_count = len(data1.entries)
        print(f"[INFO] Starting with {initial_count} existing entries")

        # Add a test entry
        test_entry = TimeEntry(
            date="2024-10-26",
            task="Test Task Alpha",
            time_in="09:00",
            time_out="10:30"
        )

        success = data1.add_entry(test_entry)
        if not success:
            print("[FAIL] Failed to add entry to data model")
            return False

        print(f"[OK] Entry added: {test_entry.task}")
        print(f"    Date: {test_entry.date}, In: {test_entry.time_in}, Out: {test_entry.time_out}")

        # Verify it was saved by reloading
        data2 = TimeLogData()
        print(f"[INFO] Reloaded data from disk: {len(data2.entries)} entries")

        # Check if our entry is there
        found = False
        for entry in data2.entries:
            if entry.task == "Test Task Alpha" and entry.date == "2024-10-26":
                found = True
                print(f"[OK] Entry FOUND after reload: {entry.task}")
                print(f"    Duration: {entry.duration_display()}")
                break

        if not found:
            print("[FAIL] Entry NOT found after reload - data persistence broken!")
            return False

        print("[PASS] Data persistence working correctly")
        return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        traceback.print_exc()
        return False


def test_duration_calculation():
    """Test 2: Duration calculation"""
    print_header("TEST 2: Duration Calculation")

    try:
        test_cases = [
            ("09:00", "10:30", 90, "1.5 Hrs"),
            ("14:00", "14:45", 45, "0.75 Hrs"),
            ("08:00", "17:00", 540, "9 Hrs"),
            ("23:00", "01:00", 120, "2 Hrs"),  # Overnight
        ]

        all_passed = True
        for time_in, time_out, expected_mins, expected_display in test_cases:
            entry = TimeEntry("2024-10-26", "Test", time_in, time_out)
            actual_mins = entry.duration_minutes()
            actual_display = entry.duration_display()

            if abs(actual_mins - expected_mins) < 1:  # Allow 1 min rounding
                print(f"[OK] {time_in} -> {time_out}: {actual_display}")
            else:
                print(f"[FAIL] {time_in} -> {time_out}: got {actual_display}, expected {expected_display}")
                all_passed = False

        if all_passed:
            print("[PASS] All duration calculations correct")
        return all_passed

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        traceback.print_exc()
        return False


def test_multiple_entries():
    """Test 3: Multiple entries and statistics"""
    print_header("TEST 3: Multiple Entries & Statistics")

    try:
        data = TimeLogData()
        today = datetime.now().strftime("%Y-%m-%d")
        initial_count = len([e for e in data.entries if e.date == today])

        # Add multiple entries
        entries_to_add = [
            TimeEntry(today, "Morning Meeting", "09:00", "10:00"),
            TimeEntry(today, "Development Work", "10:30", "12:30"),
            TimeEntry(today, "Lunch Break", "12:30", "13:30"),
            TimeEntry(today, "Code Review", "13:30", "14:30"),
        ]

        for entry in entries_to_add:
            if not data.add_entry(entry):
                print(f"[FAIL] Failed to add {entry.task}")
                return False
            print(f"[OK] Added: {entry.task} ({entry.duration_display()})")

        # Calculate total
        today_entries = [e for e in data.entries if e.date == today]
        total_mins = sum(e.duration_minutes() for e in today_entries)
        total_hours = int(total_mins // 60)
        total_mins = int(total_mins % 60)

        print(f"\n[INFO] Today's Summary:")
        print(f"    Total entries: {len(today_entries)}")
        print(f"    Total time: {total_hours}h {total_mins}m")

        # Verify all entries saved
        data2 = TimeLogData()
        reloaded_count = len([e for e in data2.entries if e.date == today])

        if reloaded_count >= initial_count + len(entries_to_add):
            print(f"[OK] All entries persisted: {reloaded_count} total")
            print("[PASS] Multiple entries saved and statistics calculated")
            return True
        else:
            print(f"[FAIL] Lost entries - expected {initial_count + len(entries_to_add)}, got {reloaded_count}")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        traceback.print_exc()
        return False


def test_data_file_integrity():
    """Test 4: Data file integrity and format"""
    print_header("TEST 4: Data File Integrity")

    try:
        data_file = Path.home() / ".timelogapp" / "data.json"

        if not data_file.exists():
            print(f"[WARN] Data file doesn't exist yet: {data_file}")
            # Create one
            data = TimeLogData()
            test_entry = TimeEntry("2024-10-26", "Integrity Test", "15:00", "15:30")
            data.add_entry(test_entry)

        if not data_file.exists():
            print("[FAIL] Data file still doesn't exist after save attempt")
            return False

        print(f"[OK] Data file exists: {data_file}")

        # Read and validate JSON
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            print(f"[OK] Valid JSON format")

            if "entries" in content:
                entry_count = len(content["entries"])
                print(f"[OK] Contains 'entries' field with {entry_count} entries")

                # Validate structure of first entry
                if entry_count > 0:
                    first = content["entries"][0]
                    required_fields = ["id", "date", "task", "time_in", "time_out"]
                    missing = [f for f in required_fields if f not in first]

                    if missing:
                        print(f"[FAIL] Missing fields: {missing}")
                        return False

                    print(f"[OK] Entry structure valid")
                    print(f"    Sample: {first['task']} on {first['date']}")
            else:
                print("[FAIL] Missing 'entries' field")
                return False

            file_size = data_file.stat().st_size
            print(f"[OK] File size: {file_size} bytes")

            print("[PASS] Data file integrity verified")
            return True

        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON: {e}")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        traceback.print_exc()
        return False


def test_entry_serialization():
    """Test 5: Entry serialization to/from dict"""
    print_header("TEST 5: Entry Serialization")

    try:
        # Create an entry
        original = TimeEntry("2024-10-26", "Serialization Test", "11:00", "11:45")
        original_id = original.id

        # Serialize
        entry_dict = original.to_dict()
        print(f"[OK] Serialized entry to dict")
        print(f"    Fields: {list(entry_dict.keys())}")

        # Deserialize
        restored = TimeEntry.from_dict(entry_dict)

        # Verify all fields match
        if (restored.id == original_id and
            restored.date == original.date and
            restored.task == original.task and
            restored.time_in == original.time_in and
            restored.time_out == original.time_out):
            print(f"[OK] Deserialized entry matches original")
            print(f"    Task: {restored.task}")
            print(f"    Duration: {restored.duration_display()}")
            print("[PASS] Serialization working correctly")
            return True
        else:
            print("[FAIL] Deserialized entry doesn't match original")
            return False

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n")
    print("="*70)
    print("  TimeLogApp - Comprehensive Test Suite".center(70))
    print("  Testing data persistence, calculations, and serialization".center(70))
    print("="*70)

    tests = [
        ("Data Persistence", test_data_persistence),
        ("Duration Calculation", test_duration_calculation),
        ("Multiple Entries", test_multiple_entries),
        ("Data File Integrity", test_data_file_integrity),
        ("Entry Serialization", test_entry_serialization),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FATAL] Unhandled exception in {name}: {e}")
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** ALL TESTS PASSED - Application is ready for use! ***")
        return True
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed - see details above ***")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        traceback.print_exc()
        sys.exit(1)
