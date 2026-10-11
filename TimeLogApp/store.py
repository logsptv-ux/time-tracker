import copy
import datetime
import json
import os
import uuid
import tempfile
from pathlib import Path
from .portable import DATA_DIR


def _get_default_path() -> Path:
    return DATA_DIR / "time_log.json"


_ENTRY_FIELDS = {"id", "date", "task", "time_in", "time_out"}
_PENDING_FIELDS = {"date", "task", "time_in"}
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M"


def _validate_timestamp(value, field_name):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a timestamp string")
    try:
        datetime.datetime.strptime(value, _TIMESTAMP_FORMAT)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must use YYYY-MM-DDTHH:MM format"
        ) from exc


def _validate_date(value, field_name):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a date string")
    try:
        datetime.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc


def _duration_minutes(time_in, time_out):
    start = datetime.datetime.strptime(time_in, _TIMESTAMP_FORMAT)
    end = datetime.datetime.strptime(time_out, _TIMESTAMP_FORMAT)
    if end < start:
        end += datetime.timedelta(days=1)
    minutes = int((end - start).total_seconds() // 60)
    if minutes <= 0 or minutes > 24 * 60:
        raise ValueError("Session duration must be positive and not exceed 24 hours")


class Store:
    def __init__(self, path: str | None = None):
        if path is None:
            path = str(_get_default_path())
        self.path = path

    def _validate_entry(self, entry, index):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry at index {index} must be an object")
        missing = _ENTRY_FIELDS - set(entry.keys())
        if missing:
            raise ValueError(
                f"Entry at index {index} missing fields: {', '.join(sorted(missing))}"
            )
        if not isinstance(entry["id"], str) or not entry["id"]:
            raise ValueError(f"Entry at index {index} has an invalid id")
        if not isinstance(entry["task"], str):
            raise ValueError(f"Entry at index {index} task must be a string")
        _validate_date(entry["date"], f"Entry at index {index} date")
        _validate_timestamp(entry["time_in"], f"Entry at index {index} time_in")
        _validate_timestamp(entry["time_out"], f"Entry at index {index} time_out")
        try:
            _duration_minutes(entry["time_in"], entry["time_out"])
        except ValueError as exc:
            raise ValueError(f"Entry at index {index}: {exc}") from exc

    def _validate_pending(self, pending):
        if pending is not None:
            if not isinstance(pending, dict):
                raise ValueError("Document pending must be null or an object")
            missing = _PENDING_FIELDS - set(pending.keys())
            if missing:
                raise ValueError(
                    f"Pending session missing fields: {', '.join(sorted(missing))}"
                )
            if not isinstance(pending["task"], str):
                raise ValueError("Pending session task must be a string")
            _validate_date(pending["date"], "Pending session date")
            _validate_timestamp(pending["time_in"], "Pending session time_in")

    def _validate_document(self, doc):
        if not isinstance(doc, dict):
            raise ValueError("Document must be a JSON object")
        if doc.get("version") != 1:
            raise ValueError(f"Unsupported document version: {doc.get('version')}")
        if not isinstance(doc.get("entries"), list):
            raise ValueError("Document entries must be a list")
        if "pending" not in doc:
            raise ValueError("Document missing 'pending' key")
        seen_ids = set()
        for i, entry in enumerate(doc.get("entries", [])):
            self._validate_entry(entry, i)
            if entry["id"] in seen_ids:
                raise ValueError(f"Duplicate entry id: {entry['id']}")
            seen_ids.add(entry["id"])
        self._validate_pending(doc["pending"])

    def load(self) -> dict:
        if not os.path.isfile(self.path):
            doc = {"version": 1, "entries": [], "pending": None}
            self.save(doc)
            return doc
        with open(self.path, "r", encoding="utf-8") as f:
            raw = f.read()
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Malformed JSON in {self.path}: {e}. Original file preserved."
            ) from e
        if not isinstance(doc, dict) or doc.get("version") != 1:
            raise ValueError(
                f"Unsupported document version in {self.path}. Original file preserved."
            )
        self._validate_document(doc)
        return doc

    def save(self, document: dict) -> None:
        self._validate_document(document)

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

        tmp_dir = os.path.dirname(self.path) or "."
        fd, tmp_path = tempfile.mkstemp(dir=tmp_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                # Optimize: Use separators to reduce file size
                json.dump(document, f, indent=2, ensure_ascii=False, separators=(',', ': '))
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
        except Exception:
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)
            raise

    def create_backup(self) -> str:
        """Create a backup of the current data file."""
        if not os.path.isfile(self.path):
            return ""

        backup_dir = Path(self.path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"time_log_backup_{timestamp}.json"

        import shutil
        shutil.copy2(self.path, backup_path)

        # Keep only last 10 backups
        backups = sorted(backup_dir.glob("time_log_backup_*.json"))
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()

        return str(backup_path)

    def add_entry(self, document: dict, entry: dict) -> dict:
        if not isinstance(entry, dict):
            raise ValueError("Entry must be a dictionary")
        candidate = dict(entry)
        if "id" not in candidate:
            candidate["id"] = str(uuid.uuid4())
        self._validate_entry(candidate, len(document.get("entries", [])))
        existing_ids = {item["id"] for item in document.get("entries", [])}
        if candidate["id"] in existing_ids:
            raise ValueError(f"Duplicate entry id: {candidate['id']}")
        document["entries"].append(candidate)
        return candidate

    def remove_entry(self, document: dict, entry_id: str) -> bool:
        for i, entry in enumerate(document["entries"]):
            if entry["id"] == entry_id:
                del document["entries"][i]
                return True
        return False

    def update_entry(self, document: dict, entry_id: str, **kwargs) -> bool:
        if "id" in kwargs and kwargs["id"] != entry_id:
            raise ValueError("Entry id cannot be changed")
        for index, entry in enumerate(document["entries"]):
            if entry["id"] == entry_id:
                candidate = dict(entry)
                candidate.update(kwargs)
                self._validate_entry(candidate, index)
                other_ids = {
                    item["id"] for item in document["entries"] if item["id"] != entry_id
                }
                if candidate["id"] in other_ids:
                    raise ValueError(f"Duplicate entry id: {candidate['id']}")
                entry.clear()
                entry.update(candidate)
                return True
        return False

    def set_pending(self, document: dict, pending: dict | None) -> dict:
        self._validate_pending(pending)
        document["pending"] = pending
        return document
