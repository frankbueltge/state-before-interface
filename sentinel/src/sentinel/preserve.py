"""Preservation: original bytes plus a manifest entry with URL, UTC retrieval
time and SHA-256 (invariant I1). Snapshot directories are append-only (I3).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2,
                               sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class Snapshot:
    """One dated snapshot directory with its manifest."""

    def __init__(self, repo_root: Path, day: str):
        self.day = day
        self.dir = repo_root / "snapshots" / day
        self.manifest_path = self.dir / "manifest.json"
        existing = read_json(self.manifest_path, {"run_date": day, "entries": []})
        self.entries: list[dict] = existing["entries"]

    def preserve(self, relative_name: str, data: bytes, url: str,
                 http_status: int) -> dict:
        path = self.dir / relative_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        entry = {
            "file": f"snapshots/{self.day}/{relative_name}",
            "url": url,
            "retrieved_at": utc_now(),
            "http_status": http_status,
            "sha256": sha256(data),
            "bytes": len(data),
        }
        self.entries.append(entry)
        return entry

    def write_manifest(self) -> None:
        write_json(self.manifest_path, {"run_date": self.day,
                                        "entries": self.entries})
