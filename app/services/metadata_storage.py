
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4


METADATA_FILE = (
    Path(__file__).resolve().parents[2] / "storage" / "metadata.json"
)

_metadata_lock = Lock()


def _read_metadata() -> list[dict]:
    if not METADATA_FILE.exists():
        return []

    with METADATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Metadata file must contain a JSON list.")

    return data


def _write_metadata(records: list[dict]) -> None:
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first, then replace the metadata file.
    temporary_file = METADATA_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=2, ensure_ascii=False)

        temporary_file.replace(METADATA_FILE)
    finally:
        temporary_file.unlink(missing_ok=True)


def create_document_metadata(file_info: dict) -> dict:
    with _metadata_lock:
        records = _read_metadata()

        record = {
            "document_id": str(uuid4()),
            "original_filename": file_info["original_filename"],
            "stored_filename": file_info["stored_filename"],
            "content_type": file_info["content_type"],
            "size_bytes": file_info["size_bytes"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

        records.append(record)
        _write_metadata(records)

        return record


def list_documents() -> list[dict]:
    with _metadata_lock:
        return _read_metadata()


def get_document(document_id: str) -> dict | None:
    with _metadata_lock:
        records = _read_metadata()

        for record in records:
            if record.get("document_id") == document_id:
                return record

    return None
