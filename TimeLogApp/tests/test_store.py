import json
import os
import tempfile
import unittest
from unittest.mock import patch

from TimeLogApp.store import Store


TEST_JSON = """{
  "version": 1,
  "entries": [
    {
      "id": "abc-123",
      "date": "2026-09-22",
      "task": "Work",
      "time_in": "2026-09-22T08:00",
      "time_out": "2026-09-22T17:00"
    }
  ],
  "pending": {
    "date": "2026-09-23",
    "task": "Meeting",
    "time_in": "2026-09-23T09:00"
  }
}"""


class TestStoreLoad(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_create_empty_doc_when_absent(self):
        doc = self.store.load()
        self.assertEqual(doc["version"], 1)
        self.assertEqual(doc["entries"], [])
        self.assertIsNone(doc["pending"])
        self.assertTrue(os.path.isfile(self.store.path))

    def test_load_existing_doc(self):
        with open(self.store.path, "w", encoding="utf-8") as f:
            f.write(TEST_JSON)
        doc = self.store.load()
        self.assertEqual(doc["version"], 1)
        self.assertEqual(len(doc["entries"]), 1)
        self.assertEqual(doc["entries"][0]["task"], "Work")
        self.assertIsNotNone(doc["pending"])
        self.assertEqual(doc["pending"]["task"], "Meeting")

    def test_malformed_json_preserves_file(self):
        with open(self.store.path, "w", encoding="utf-8") as f:
            f.write("{ this is not valid json")
        with open(self.store.path, "r", encoding="utf-8") as f:
            original_content = f.read()
        with self.assertRaises(ValueError):
            self.store.load()
        with open(self.store.path, "r", encoding="utf-8") as f:
            after_content = f.read()
        self.assertEqual(original_content, after_content)

    def test_malformed_json_does_not_overwrite(self):
        with open(self.store.path, "w", encoding="utf-8") as f:
            f.write("{ bad json")
        with open(self.store.path, "r", encoding="utf-8") as f:
            original_content = f.read()
        try:
            self.store.load()
        except ValueError:
            pass
        with open(self.store.path, "r", encoding="utf-8") as f:
            after_content = f.read()
        self.assertEqual(original_content, after_content)

    def test_unsupported_version(self):
        doc = {"version": 2, "entries": [], "pending": None}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()
        with open(self.store.path, "r", encoding="utf-8") as f:
            after = json.loads(f.read())
        self.assertEqual(after["version"], 2)


class TestStoreLoadIncomplete(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_missing_entries_key(self):
        doc = {"version": 1, "pending": None}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()

    def test_entries_not_list(self):
        doc = {"version": 1, "entries": "not a list", "pending": None}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()

    def test_pending_not_dict_or_none(self):
        doc = {"version": 1, "entries": [], "pending": "bad"}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()

    def test_entry_missing_field(self):
        doc = {"version": 1, "entries": [{"id": "x", "date": "2026-09-22", "task": "A"}], "pending": None}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()

    def test_pending_missing_field(self):
        doc = {"version": 1, "entries": [], "pending": {"date": "2026-09-22"}}
        with open(self.store.path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        with self.assertRaises(ValueError):
            self.store.load()


class TestStoreSaveValidation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_save_rejects_bad_version(self):
        doc = {"version": 2, "entries": [], "pending": None}
        with self.assertRaises(ValueError):
            self.store.save(doc)

    def test_save_rejects_entries_not_list(self):
        doc = {"version": 1, "entries": "bad", "pending": None}
        with self.assertRaises(ValueError):
            self.store.save(doc)

    def test_save_rejects_pending_bad_type(self):
        doc = {"version": 1, "entries": [], "pending": 42}
        with self.assertRaises(ValueError):
            self.store.save(doc)


class TestStoreAddEntryValidation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_add_entry_not_dict(self):
        doc = self.store.load()
        with self.assertRaises(ValueError):
            self.store.add_entry(doc, "not a dict")

    def test_add_entry_missing_field(self):
        doc = self.store.load()
        with self.assertRaises(ValueError):
            self.store.add_entry(doc, {"date": "2026-09-22", "task": "A"})


class TestStoreSetPendingValidation(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_set_pending_string_raises(self):
        doc = self.store.load()
        with self.assertRaises(ValueError):
            self.store.set_pending(doc, "bad")

    def test_set_pending_missing_field(self):
        doc = self.store.load()
        with self.assertRaises(ValueError):
            self.store.set_pending(doc, {"date": "2026-09-22"})


class TestStoreSave(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_save_and_load_roundtrip(self):
        doc = {"version": 1, "entries": [{"id": "x", "date": "2026-09-22", "task": "Test", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"}], "pending": None}
        self.store.save(doc)
        loaded = self.store.load()
        self.assertEqual(loaded["version"], 1)
        self.assertEqual(len(loaded["entries"]), 1)
        self.assertEqual(loaded["entries"][0]["task"], "Test")

    def test_atomic_replacement(self):
        doc = {"version": 1, "entries": [], "pending": None}
        self.store.save(doc)
        with open(self.store.path, "r", encoding="utf-8") as f:
            content1 = f.read()
        doc["entries"].append({"id": "y", "date": "2026-09-23", "task": "Test2", "time_in": "2026-09-23T10:00", "time_out": "2026-09-23T11:00"})
        self.store.save(doc)
        with open(self.store.path, "r", encoding="utf-8") as f:
            content2 = f.read()
        self.assertNotEqual(content1, content2)
        reloaded = json.loads(content2)
        self.assertEqual(len(reloaded["entries"]), 1)

    def test_no_temp_files_left_behind(self):
        doc = {"version": 1, "entries": [], "pending": None}
        self.store.save(doc)
        tmpdir = self.tmpdir
        remaining = [f for f in os.listdir(tmpdir) if f.endswith(".tmp")]
        self.assertEqual(remaining, [])


class TestStoreAddEntry(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_add_entry_generates_uuid(self):
        doc = self.store.load()
        entry = {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"}
        result = self.store.add_entry(doc, entry)
        self.assertIn("id", result)
        self.assertIsInstance(result["id"], str)
        self.assertTrue(len(result["id"]) > 0)

    def test_add_entry_persists_in_doc(self):
        doc = self.store.load()
        entry = {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"}
        self.store.add_entry(doc, entry)
        self.assertEqual(len(doc["entries"]), 1)

    def test_add_entry_preserves_existing_ids(self):
        doc = self.store.load()
        entry = {"id": "my-uuid", "date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T17:00"}
        self.store.add_entry(doc, entry)
        self.assertEqual(doc["entries"][0]["id"], "my-uuid")


class TestStoreRemoveEntry(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_remove_existing(self):
        doc = self.store.load()
        self.store.add_entry(doc, {"id": "abc", "date": "2026-09-22", "task": "A", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"})
        self.store.add_entry(doc, {"id": "def", "date": "2026-09-23", "task": "B", "time_in": "2026-09-23T08:00", "time_out": "2026-09-23T09:00"})
        result = self.store.remove_entry(doc, "abc")
        self.assertTrue(result)
        self.assertEqual(len(doc["entries"]), 1)
        self.assertEqual(doc["entries"][0]["id"], "def")

    def test_remove_nonexistent(self):
        doc = self.store.load()
        result = self.store.remove_entry(doc, "nonexistent")
        self.assertFalse(result)


class TestStoreUpdateEntry(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_update_existing(self):
        doc = self.store.load()
        self.store.add_entry(doc, {"id": "abc", "date": "2026-09-22", "task": "Old", "time_in": "2026-09-22T08:00", "time_out": "2026-09-22T09:00"})
        result = self.store.update_entry(doc, "abc", task="New", date="2026-09-23")
        self.assertTrue(result)
        self.assertEqual(doc["entries"][0]["task"], "New")
        self.assertEqual(doc["entries"][0]["date"], "2026-09-23")

    def test_update_nonexistent(self):
        doc = self.store.load()
        result = self.store.update_entry(doc, "xyz", task="New")
        self.assertFalse(result)


class TestStoreSetPending(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_set_pending(self):
        doc = self.store.load()
        pending = {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00"}
        self.store.set_pending(doc, pending)
        self.assertEqual(doc["pending"], pending)

    def test_clear_pending(self):
        doc = self.store.load()
        doc["pending"] = {"date": "2026-09-22", "task": "Work", "time_in": "2026-09-22T08:00"}
        self.store.set_pending(doc, None)
        self.assertIsNone(doc["pending"])


class TestStorePersistenceOfPending(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.store = Store(path=os.path.join(self.tmpdir, "time_log.json"))

    def test_pending_survives_save_and_reload(self):
        doc = self.store.load()
        pending = {"date": "2026-09-22", "task": "Pending Task", "time_in": "2026-09-22T09:00"}
        self.store.set_pending(doc, pending)
        self.store.save(doc)
        doc2 = self.store.load()
        self.assertEqual(doc2["pending"], pending)

    def test_pending_recovery_after_cancellation(self):
        doc = self.store.load()
        pending = {"date": "2026-09-22", "task": "Old Task", "time_in": "2026-09-22T09:00"}
        self.store.set_pending(doc, pending)
        self.store.save(doc)
        doc["pending"] = None
        self.store.save(doc)
        doc2 = self.store.load()
        self.assertIsNone(doc2["pending"])


if __name__ == "__main__":
    unittest.main()
